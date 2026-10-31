#!/usr/bin/env python3
import base64
from pathlib import Path
# panel
p = Path("scripts/account_panel.b64")
if p.exists():
    Path("src/components/AccountProfilePanel.tsx").write_bytes(base64.b64decode(p.read_text().strip()))
    print("wrote AccountProfilePanel")
# patch
s = Path("scripts/patch_account_panel.b64")
if s.exists():
    Path("scripts/patch_account_panel.py").write_bytes(base64.b64decode(s.read_text().strip()))
    print("wrote patch_account_panel.py")
    import subprocess
    subprocess.check_call(["python3", "scripts/patch_account_panel.py"])
