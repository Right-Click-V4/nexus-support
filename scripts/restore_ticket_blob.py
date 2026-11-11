#!/usr/bin/env python3
"""Restore TicketContext from blob or known-good GitHub raw if truncated."""
import base64, zlib, urllib.request
from pathlib import Path

target = Path("src/context/TicketContext.tsx")
blob = Path("scripts/blobs/tc.b64")
GOOD = "e3a5fd3"

def healthy(text: str) -> bool:
    return (
        bool(text)
        and "return null as any" not in text
        and len(text) > 18000
        and "export function useTickets" in text
    )

def write(data: bytes, source: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"TicketContext restored from {source}: {len(data)} bytes")

cur = target.read_text() if target.exists() else ""
if healthy(cur):
    print("TicketContext already healthy", len(cur))
    raise SystemExit(0)

if blob.exists() and blob.stat().st_size > 1000:
    try:
        data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
        if healthy(data.decode("utf-8", "replace")):
            write(data, "tc.b64")
            raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        print("tc blob failed:", e)

url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{GOOD}/src/context/TicketContext.tsx"
try:
    data = urllib.request.urlopen(url, timeout=25).read()
    if healthy(data.decode("utf-8", "replace")):
        write(data, GOOD)
        raise SystemExit(0)
    print("remote not healthy", len(data))
except Exception as e:
    print("remote restore failed:", e)

print("WARN: TicketContext still truncated")
