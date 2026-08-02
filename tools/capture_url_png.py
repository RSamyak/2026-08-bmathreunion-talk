#!/usr/bin/env python3
"""Capture a PNG screenshot of a local file:// URL via Chrome DevTools."""
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

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9222


def main():
    url = sys.argv[1]
    out = os.path.abspath(sys.argv[2])
    wait = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 1280
    height = int(sys.argv[5]) if len(sys.argv) > 5 else 720

    os.makedirs(os.path.dirname(out), exist_ok=True)
    prof = tempfile.mkdtemp(prefix="cap-")
    proc = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-allow-origins=*",
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={prof}",
            "--window-size=%d,%d" % (width, height),
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
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

        def send(mid, method, params=None):
            ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))

        def wait_for(mid):
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == mid:
                    return msg

        send(1, "Page.enable")
        wait_for(1)
        time.sleep(wait)
        send(2, "Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": True})
        res = wait_for(2)
        with open(out, "wb") as f:
            f.write(base64.b64decode(res["result"]["data"]))
        ws.close()
        print(f"wrote {out} ({os.path.getsize(out)} bytes)")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)


if __name__ == "__main__":
    main()
