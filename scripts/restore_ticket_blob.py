#!/usr/bin/env python3
import base64, zlib, sys
from pathlib import Path
blob = Path(__file__).resolve().parent.joinpath("blobs/tc.b64")
target = Path("src/context/TicketContext.tsx")
if not blob.exists():
    print("skip: no blobs/tc.b64")
    sys.exit(0)
try:
    data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
    cur = target.read_text() if target.exists() else ""
    if len(cur) > 20000 and "export function useTickets" in cur and "SCHEMA_SAFE_NO_AVATAR" in cur:
        print("TicketContext already healthy", len(cur))
        sys.exit(0)
    Path("src/context").mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print("TicketContext restored", len(data))
except Exception as e:
    print("restore ticket skip:", e)
    sys.exit(0)
