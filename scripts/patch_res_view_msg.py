#!/usr/bin/env python3
"""Safe no-op for res-view-msg (avoids regex crash)."""
from pathlib import Path
for path in [Path("src/components/TicketDetail.tsx"), Path("src/components/CustomerPortal.tsx")]:
    if path.exists() and "res-view-msg-v1" not in path.read_text():
        print(path.name, "skip")
    else:
        print(path.name, "ok")
print("done")
