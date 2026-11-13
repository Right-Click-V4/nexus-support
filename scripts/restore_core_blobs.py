#!/usr/bin/env python3
"""Restore critical source files if they are stubs/placeholders.

Order:
1) local scripts/blobs/*.b64 if valid
2) git show from known SHAs (when available in checkout)
3) raw.githubusercontent.com download
"""
from __future__ import annotations

import base64
import subprocess
import sys
import urllib.request
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = Path(__file__).resolve().parent / "blobs"

TARGETS = [
    # key, relpath, min_bytes, must_contain, git_sha
    ("pc", "src/context/PlatformContext.tsx", 10000, "export function usePlatform", "e3a5fd3"),
    ("tc", "src/context/TicketContext.tsx", 15000, "export function useTickets", "c3b543f"),
    ("plv", "src/components/PortalLiveChatView.tsx", 5000, "export default", "24910bd"),
    ("lcp", "src/components/LiveChatPage.tsx", 5000, "export default", "24910bd"),
    ("login_scene", "src/components/LoginScene.tsx", 8000, "CosmicFallBackground", "def5916"),
    ("login_page", "src/components/LoginPage.tsx", 8000, "CosmicFallBackground", "e889ef3"),
]


def is_stub(path: Path, min_bytes: int, must_contain: str) -> bool:
    if not path.exists():
        return True
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return True
    if len(text) < min_bytes:
        return True
    if "PLACEHOLDER" in text or "SEE_LOCAL_FILE" in text:
        return True
    if must_contain and must_contain not in text:
        return True
    return False


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"WROTE {path} ({len(data)} bytes)")


def try_blob(key: str, path: Path) -> bool:
    blob = BLOBS / f"{key}.b64"
    if not blob.exists():
        return False
    try:
        raw = blob.read_text().strip()
        if len(raw) < 200 or raw.startswith("PLACEHOLDER"):
            return False
        data = zlib.decompress(base64.b64decode(raw))
        if len(data) < 1000:
            return False
        write_bytes(path, data)
        return True
    except Exception as e:
        print(f"blob {key} skip: {e}")
        return False


def try_git(sha: str, rel: str, path: Path) -> bool:
    try:
        proc = subprocess.run(
            ["git", "show", f"{sha}:{rel}"],
            cwd=str(ROOT),
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0 or len(proc.stdout) < 1000:
            return False
        write_bytes(path, proc.stdout)
        return True
    except Exception as e:
        print(f"git {sha}:{rel} skip: {e}")
        return False


def try_curl(sha: str, rel: str, path: Path) -> bool:
    url = f"https://raw.githubusercontent.com/Right-Click-V4/nexus-support/{sha}/{rel}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
        if len(data) < 1000 or b"SEE_LOCAL_FILE" in data[:80]:
            return False
        write_bytes(path, data)
        return True
    except Exception as e:
        print(f"curl {url} skip: {e}")
        return False


def main() -> int:
    failed = []
    for key, rel, min_b, needle, sha in TARGETS:
        path = ROOT / rel
        if not is_stub(path, min_b, needle):
            print(f"OK {rel} ({path.stat().st_size} bytes)")
            continue
        print(f"RESTORE {rel} ...")
        ok = try_blob(key, path) or try_git(sha, rel, path) or try_curl(sha, rel, path)
        if not ok or is_stub(path, min_b, needle):
            print(f"FAIL {rel}")
            failed.append(rel)
        else:
            print(f"OK after restore {rel} ({path.stat().st_size} bytes)")
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    print("core restore done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
