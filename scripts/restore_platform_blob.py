#!/usr/bin/env python3
"""Restore PlatformContext from blob or known-good GitHub raw if truncated."""
import base64, zlib, urllib.request
from pathlib import Path

target = Path("src/context/PlatformContext.tsx")
blob = Path("scripts/blobs/pc.b64")
GOOD = "e3a5fd3"

def healthy(text: str) -> bool:
    return (
        bool(text)
        and "PLACEHOLDER" not in text
        and len(text) > 5000
        and "export function usePlatform" in text
        and "sendChatMessage" in text
    )

def write(data: bytes, source: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"PlatformContext restored from {source}: {len(data)} bytes")

cur = target.read_text() if target.exists() else ""
if healthy(cur):
    print("PlatformContext already healthy", len(cur))
    raise SystemExit(0)

if blob.exists() and blob.stat().st_size > 1000:
    try:
        data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
        if healthy(data.decode("utf-8", "replace")):
            write(data, "pc.b64")
            raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        print("blob failed:", e)

url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{GOOD}/src/context/PlatformContext.tsx"
try:
    data = urllib.request.urlopen(url, timeout=25).read()
    if healthy(data.decode("utf-8", "replace")):
        write(data, GOOD)
        raise SystemExit(0)
    print("remote not healthy", len(data))
except Exception as e:
    print("remote restore failed:", e)

print("WARN: PlatformContext still truncated")
