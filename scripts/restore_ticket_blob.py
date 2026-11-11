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
    cols = next((ln for ln in cur.splitlines() if "CUSTOMER_COLS" in ln), "")
    bad = (
        "return null as any" in cur
        or len(cur) < 20000
        or "export function useTickets" not in cur
        or "avatar_url" in cols
    )
    if bad:
        Path("src/context").mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print("TicketContext restored", len(data))
    else:
        print("TicketContext already healthy", len(cur))
except Exception as e:
    print("restore ticket skip:", e)
    sys.exit(0)
