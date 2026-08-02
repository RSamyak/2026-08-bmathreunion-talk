#!/usr/bin/env python3
"""Deterministic HTML->PDF exporter for a Quarto reveal.js deck.

WHY THIS EXISTS / WHY IT AVOIDS ?print-pdf
-------------------------------------------
reveal.js has a special "print" mode (triggered by the ``?print-pdf`` query
string) that Chrome's own PDF printer relies on. That mode RE-FLOWS the deck:
it forces ``display:block`` inline on every ``<section>``, recomputes ``vh``
units against the paper page size, and repositions fragments so they can be
paginated. For this deck that reflow keeps breaking layouts (the in-memoriam
photo gets pushed off the page, absolutely-positioned / vertically-centered
content drifts, etc.).

The NORMAL (non-print) rendering, however, is correct: reveal scales the deck
to fill the viewport and everything is where the author placed it. So instead
of asking Chrome to "print" the deck, this exporter simply SCREENSHOTS the
normal rendering, one click at a time, and stitches the images into a PDF.

HOW IT WORKS
------------
1. Launch the installed Chrome headless and talk to it over the DevTools
   Protocol (websocket boilerplate borrowed from tools/capture_slides.py).
2. Open ``file://.../slides.html`` in NORMAL mode (no ?print-pdf).
3. Pin a deterministic 1280x720 viewport at deviceScaleFactor 2 via
   ``Emulation.setDeviceMetricsOverride``. The deck's native size is 1280x720
   (see _quarto.yml), so reveal scales to exactly 1.0 and each screenshot is
   the true, pixel-faithful slide -- rendered at 2560x1440 for crisp text.
4. Wait for ``Reveal.isReady()``, disable looping, and jump to the absolute
   beginning (slide 0, zero fragments revealed).
5. Walk the whole deck with ``Reveal.next()`` -- exactly like tapping the
   space/right key -- capturing a screenshot BEFORE each advance. Because we
   capture-then-advance, the first page is the title slide with no fragments
   and every subsequent click becomes its own page (beamer-style). We stop
   when ``Reveal.getState()`` stops changing (end of deck), with a hard safety
   cap against infinite loops.
6. Assemble the PNGs, in order, full-bleed into a single PDF with PyMuPDF.

Determinism: fixed viewport + device metrics (independent of the host screen),
fixed settle time, and navigation purely via the Reveal API (never by guessing
slide indices). Running it twice on the same HTML yields the same page count
and equivalent output.

Usage:
  python3 tools/deck_to_pdf.py _output/slides.html slides.pdf [settle_seconds]
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket  # websocket-client
import fitz  # PyMuPDF

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9224

# Deck native size (must match _quarto.yml width/height).
DECK_W = 1280
DECK_H = 720
# 2x oversampling so text stays crisp when the PDF is viewed/printed.
SCALE = 2
# JPEG quality for the captured frames. Photos dominate the deck, so JPEG keeps
# the PDF a few MB (PNG frames ballooned it to ~300 MB) with no visible loss.
JPEG_QUALITY = 90
# Default per-step settle time (seconds) for fragment/slide transitions.
DEFAULT_SETTLE = 0.45
# Hard cap on advances so a misbehaving deck can never loop forever.
MAX_STEPS = 300


def main():
    html = os.path.abspath(sys.argv[1])
    out = os.path.abspath(sys.argv[2])
    settle = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SETTLE
    url = "file://" + html

    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    prof = tempfile.mkdtemp(prefix="deck2pdf-")
    png_dir = tempfile.mkdtemp(prefix="deck2pdf-pngs-")
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
         "--no-default-browser-check", "--remote-allow-origins=*",
         "--hide-scrollbars", "--force-device-scale-factor=1",
         f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
         f"--window-size={DECK_W},{DECK_H}", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                pages = [t for t in tabs if t.get("type") == "page" and t.get("webSocketDebuggerUrl")]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.25)
        if not ws_url:
            raise RuntimeError("Chrome DevTools endpoint never came up")

        ws = websocket.create_connection(ws_url, max_size=None)
        mid = [0]

        def call(method, params=None):
            mid[0] += 1
            i = mid[0]
            ws.send(json.dumps({"id": i, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == i:
                    if "error" in msg:
                        raise RuntimeError(f"{method} failed: {msg['error']}")
                    return msg

        def evaluate(expr, await_promise=False):
            res = call("Runtime.evaluate", {
                "expression": expr,
                "returnByValue": True,
                "awaitPromise": await_promise,
            })
            return res["result"].get("result", {}).get("value")

        call("Page.enable")
        call("Runtime.enable")

        # Pin a deterministic viewport independent of the host display. With the
        # deck's native 1280x720 and scale factor 2, reveal scales to 1.0 and
        # each capture is the real slide at 2560x1440.
        call("Emulation.setDeviceMetricsOverride", {
            "width": DECK_W, "height": DECK_H,
            "deviceScaleFactor": SCALE, "mobile": False,
        })

        # Wait for reveal to finish building.
        for _ in range(120):
            ready = evaluate("typeof Reveal !== 'undefined' && Reveal.isReady && Reveal.isReady()")
            if ready:
                break
            time.sleep(0.25)
        else:
            raise RuntimeError("Reveal never became ready")

        # No looping; keep fragments as discrete steps; go to the absolute start.
        evaluate("Reveal.configure({loop:false, fragments:true}); true")
        evaluate("Reveal.slide(0,0,0); true")
        time.sleep(settle)
        # Guarantee we are truly at the beginning (slide 0, no fragments shown).
        # Reveal treats indexf === -1 (or undefined) as "before the first
        # fragment", which is the beamer-style opening page we want.
        evaluate("Reveal.slide(0,0); true")
        time.sleep(settle)

        def state():
            return evaluate("JSON.stringify(Reveal.getState())")

        pngs = []

        def capture():
            res = call("Page.captureScreenshot", {
                "format": "jpeg",
                "quality": JPEG_QUALITY,
                "fromSurface": True,
                "captureBeyondViewport": False,
                "clip": {"x": 0, "y": 0, "width": DECK_W, "height": DECK_H, "scale": 1},
            })
            path = os.path.join(png_dir, f"page-{len(pngs):04d}.jpg")
            with open(path, "wb") as f:
                f.write(base64.b64decode(res["result"]["data"]))
            pngs.append(path)

        # Capture-then-advance: first page = title slide, zero fragments.
        for _ in range(MAX_STEPS):
            capture()
            before = state()
            evaluate("Reveal.next(); true")
            time.sleep(settle)
            after = state()
            if after == before:
                # Advancing changed nothing -> we are at the end of the deck.
                break

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)

    if not pngs:
        shutil.rmtree(png_dir, ignore_errors=True)
        raise RuntimeError("No pages captured")

    # Stitch PNGs full-bleed into a single PDF, one image per page.
    doc = fitz.open()
    for png in pngs:
        img = fitz.open(png)
        w, h = img[0].rect.width, img[0].rect.height
        page = doc.new_page(width=w, height=h)
        page.insert_image(fitz.Rect(0, 0, w, h), filename=png)
        img.close()
    doc.save(out)
    doc.close()

    n = len(pngs)
    shutil.rmtree(png_dir, ignore_errors=True)
    print(f"wrote {out} ({os.path.getsize(out)} bytes, {n} pages)")


if __name__ == "__main__":
    main()
