#!/usr/bin/env python3
"""Restore CustomerPortal to last good full UI (no Track Ticket, full Submit/My Tickets)."""
from pathlib import Path
import urllib.request

GOOD_SHA = "0c977a47df06c6e8beaf8deec011ea0b31b429ca"
URL = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{GOOD_SHA}/src/components/CustomerPortal.tsx"

p = Path("src/components/CustomerPortal.tsx")
text = p.read_text() if p.exists() else ""
bad = (
    "Status Guidelines" not in text
    or "id: 'track'" in text
    or "label: 'Track Ticket'" in text
    or "Priority Guide" not in text
    or len(text.splitlines()) < 1000
)
if not bad and "cp-full-restore-v2" in text:
    print("customer portal already good", len(text.splitlines()))
else:
    print("restoring CustomerPortal from", GOOD_SHA)
    content = urllib.request.urlopen(URL, timeout=45).read().decode()
    if "Status Guidelines" not in content or "Priority Guide" not in content:
        raise SystemExit("fetched CustomerPortal invalid")
    content = content.replace(
        "    { id: 'track', label: 'Track Ticket', icon: Search },\n",
        "",
    )
    content = content.replace(
        "    { id: 'track', label: 'Track Ticket', icon: Search },",
        "",
    )
    if "cp-full-restore-v2" not in content:
        content = "/* cp-full-restore-v2 */\n" + content
    p.write_text(content)
    print("restored", len(content.splitlines()), "lines")
