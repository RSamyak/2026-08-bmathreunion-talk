#!/usr/bin/env python3
"""Screenshot specific reveal.js slides by driving Reveal.slide() over DevTools.

Usage:
  python3 tools/capture_slides.py _output/slides.html out_prefix idx[,idx...]

Writes out_prefix-<idx>.png for each horizontal slide index.
"""
import base64, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
import websocket  # websocket-client

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9223


def main():
    html = os.path.abspath(sys.argv[1])
    prefix = sys.argv[2]
    idxs = [int(x) for x in sys.argv[3].split(",")]
    url = "file://" + html
    prof = tempfile.mkdtemp(prefix="capslides-")
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
         "--no-default-browser-check", "--remote-allow-origins=*",
         f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
         "--window-size=1280,720", url],
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
                    return msg

        call("Page.enable")
        call("Runtime.enable")
        time.sleep(3.0)  # let reveal build
        for idx in idxs:
            call("Runtime.evaluate", {"expression": f"Reveal.slide({idx},0);", "awaitPromise": False})
            time.sleep(0.8)
            res = call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
            out = f"{prefix}-{idx}.png"
            with open(out, "wb") as f:
                f.write(base64.b64decode(res["result"]["data"]))
            print(f"wrote {out} ({os.path.getsize(out)} bytes)")
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)


if __name__ == "__main__":
    main()
