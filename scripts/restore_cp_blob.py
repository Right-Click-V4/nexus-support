#!/usr/bin/env python3
"""Restore CustomerPortal from blob or known-good GitHub raw if truncated."""
import base64, zlib, urllib.request
from pathlib import Path

target = Path("src/components/CustomerPortal.tsx")
blob = Path("scripts/blobs/cp.b64")
GOOD = "c3edde907e5e5be48439b7fea0df6dbe3dca6611"

def healthy(text: str) -> bool:
    return (
        bool(text)
        and "PLACEHOLDER" not in text
        and "Loading portal update" not in text
        and len(text) > 50000
        and ("PortalLiveChat" in text or "Live Chat" in text or "export default function CustomerPortal" in text)
    )

def write(data: bytes, source: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"CustomerPortal restored from {source}: {len(data)} bytes")

cur = target.read_text() if target.exists() else ""
if healthy(cur):
    print("CustomerPortal already healthy", len(cur))
    raise SystemExit(0)

if blob.exists() and blob.stat().st_size > 1000:
    try:
        data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
        if healthy(data.decode("utf-8", "replace")):
            write(data, "cp.b64")
            raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        print("cp blob failed:", e)

url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{GOOD}/src/components/CustomerPortal.tsx"
try:
    data = urllib.request.urlopen(url, timeout=25).read()
    if healthy(data.decode("utf-8", "replace")):
        write(data, GOOD)
        raise SystemExit(0)
    print("remote portal not healthy", len(data))
except Exception as e:
    print("remote portal restore failed:", e)

print("WARN: CustomerPortal still truncated")
