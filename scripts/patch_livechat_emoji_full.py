#!/usr/bin/env python3
"""Ensure LiveChatPage is non-empty. Never overwrite a good file with empty data."""
from pathlib import Path
p = Path("src/components/LiveChatPage.tsx")
if p.exists() and len(p.read_text().strip()) > 500 and "export default" in p.read_text():
    print("LiveChatPage already present, skip")
else:
    print("LiveChatPage missing or empty — leave alone (content must be in repo)")
