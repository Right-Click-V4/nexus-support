#!/usr/bin/env python3
"""Write public/git-changelog-draft.json from recent git commits (build-time)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "git-changelog-draft.json"
N = 20


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def main() -> None:
    fmt = "%s%x1f%h%x1f%an%x1f%cI%x1f%b%x1e"
    raw = run(["git", "log", f"-n{N}", f"--pretty=format:{fmt}"])
    commits = []
    for chunk in (raw or "").split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split("\x1f")
        while len(parts) < 5:
            parts.append("")
        subject, short, author, date, body = parts[:5]
        subject = (subject or "").strip()
        if not subject:
            continue
        commits.append(
            {
                "subject": subject,
                "sha": (short or "").strip(),
                "author": (author or "").strip(),
                "date": (date or "").strip(),
                "body": (body or "").strip()[:500],
            }
        )

    head = run(["git", "rev-parse", "--short", "HEAD"]) or (commits[0]["sha"] if commits else "")
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "main"

    now = datetime.now(timezone.utc)
    version = now.strftime("%Y.%m.%d")
    title = f"Build {head}" if head else "Latest build"
    notes_lines = []
    for c in commits[:12]:
        line = f"• {c['subject']}"
        if c.get("sha"):
            line += f" ({c['sha']})"
        notes_lines.append(line)
    notes = "\n".join(notes_lines) if notes_lines else "No recent commits found."

    payload = {
        "generated_at": now.isoformat(),
        "branch": branch,
        "head": head,
        "suggested": {
            "version": version,
            "title": title,
            "notes": notes,
        },
        "commits": commits,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(commits)} commits, head={head})")


if __name__ == "__main__":
    main()
