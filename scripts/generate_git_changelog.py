#!/usr/bin/env python3
"""Write public/git-changelog-draft.json — customer-readable drafts from recent commits.

Emits:
  - suggested: latest day (backward compatible)
  - history: up to 12 day-grouped patches (newest first) so agents can publish any of them
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "git-changelog-draft.json"
N = 80
MAX_HISTORY = 12
MAX_LINES_PER_PATCH = 8

TYPE_LABELS = {
    "feat": "New",
    "feature": "New",
    "fix": "Fixed",
    "bugfix": "Fixed",
    "ui": "Updated look",
    "style": "Updated look",
    "perf": "Faster",
    "refactor": "Improved",
    "docs": "Docs",
    "chore": "Maintenance",
    "ci": "Maintenance",
    "build": "Maintenance",
    "test": "Maintenance",
    "security": "Security",
}

SKIP_TYPES = {"ci", "build", "test", "chore"}

NOISE = re.compile(r"\b(wip|tmp|temp|debug|log|logs|typo|nit|misc)\b", re.I)


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def parse_subject(subject: str) -> tuple[str, str, str]:
    m = re.match(
        r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?!?:\s*(?P<rest>.+)$",
        subject.strip(),
    )
    if m:
        return (
            (m.group("type") or "").lower(),
            (m.group("scope") or "").strip(),
            (m.group("rest") or "").strip(),
        )
    return "", "", subject.strip()


def humanize(subject: str) -> str | None:
    typ, scope, rest = parse_subject(subject)
    if not rest:
        rest = subject.strip()
    if not rest:
        return None

    if typ in SKIP_TYPES:
        low = rest.lower()
        if not any(
            k in low
            for k in (
                "portal",
                "login",
                "chat",
                "ticket",
                "account",
                "profile",
                "avatar",
                "password",
                "overview",
                "help",
                "community",
                "sign out",
                "release",
                "patch",
            )
        ):
            return None

    rest = NOISE.sub("", rest)
    rest = re.sub(r"\s+", " ", rest).strip(" -–—:")
    if not rest:
        return None
    rest = rest[0].upper() + rest[1:]

    replacements = [
        (r"\bdeploy\.yml\b", "deployment setup"),
        (r"\bnpm cache\b", "install speed"),
        (r"\blockfile\b", "dependency list"),
        (r"\bSHA(s)?\b", "security pin"),
        (r"\bCI\b", "build"),
        (r"\bUI\b", "screen"),
        (r"\bautofill\b", "saved passwords on login"),
        (r"\bCustomerPortal\b", "Customer Portal"),
        (r"\bLiveChat\b", "Live Chat"),
        (r"\bAnnouncementsPage\b", "announcements"),
        (r"\bPortalHome\b", "Overview"),
        (r"\bReleasesPage\b", "Releases"),
        (r"\bPlatformContext\b", "platform data"),
    ]
    for pat, rep in replacements:
        rest = re.sub(pat, rep, rest, flags=re.I)

    label = TYPE_LABELS.get(typ, "Updated")
    scope_map = {
        "portal": "Customer Portal",
        "login": "Login",
        "chat": "Live Chat",
        "livechat": "Live Chat",
        "agent": "Agent Workspace",
        "account": "Account",
        "releases": "Updates",
    }
    scope_hint = scope_map.get(scope.lower(), "") if scope else ""
    if scope_hint and scope_hint.lower() not in rest.lower():
        line = f"{label}: {rest} ({scope_hint})"
    else:
        line = f"{label}: {rest}"
    if len(line) > 120:
        line = line[:117].rstrip() + "…"
    return line


def pick_title(lines: list[str], date_str: str) -> str:
    if not lines:
        return f"System update — {date_str}"
    for pref in ("New:", "Fixed:", "Updated look:", "Security:", "Improved:", "Faster:"):
        for ln in lines:
            if ln.startswith(pref):
                body = ln.split(":", 1)[-1].strip()
                if len(body) > 72:
                    body = body[:69].rstrip() + "…"
                return body
    body = lines[0].split(":", 1)[-1].strip() if ":" in lines[0] else lines[0]
    if len(body) > 72:
        body = body[:69].rstrip() + "…"
    return body or f"System update — {date_str}"


def day_key(iso: str) -> str:
    if not iso:
        return ""
    return iso[:10]


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

    by_day: dict[str, list[dict]] = defaultdict(list)
    for c in commits:
        dk = day_key(c.get("date") or "")
        if not dk:
            continue
        by_day[dk].append(c)

    day_keys = sorted(by_day.keys(), reverse=True)[:MAX_HISTORY]

    history: list[dict] = []
    for dk in day_keys:
        day_commits = by_day[dk]
        customer_lines: list[str] = []
        seen = set()
        for c in day_commits:
            line = humanize(c["subject"])
            if not line:
                continue
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            customer_lines.append(line)
            if len(customer_lines) >= MAX_LINES_PER_PATCH:
                break
        if not customer_lines:
            continue

        try:
            dt = datetime.fromisoformat(dk)
            date_str = dt.strftime("%b %d, %Y")
            version = dt.strftime("%Y.%m.%d")
        except Exception:
            date_str = dk
            version = dk.replace("-", ".")

        title = pick_title(customer_lines, date_str)
        notes = "\n".join(f"• {ln}" for ln in customer_lines)
        top_sha = day_commits[0].get("sha") or ""
        history.append(
            {
                "id": f"draft-{dk}-{top_sha}",
                "version": version,
                "title": title,
                "notes": notes,
                "customer_lines": customer_lines,
                "date": dk,
                "head": top_sha,
                "commit_count": len(day_commits),
            }
        )

    if not history:
        version = now.strftime("%Y.%m.%d")
        title = f"System update — {now.strftime('%b %d, %Y')}"
        notes = "• Improved: General stability and performance of the support portal."
        history = [
            {
                "id": f"draft-{version}",
                "version": version,
                "title": title,
                "notes": notes,
                "customer_lines": ["Improved: General stability and performance of the support portal."],
                "date": now.strftime("%Y-%m-%d"),
                "head": head,
                "commit_count": 0,
            }
        ]

    latest = history[0]
    payload = {
        "generated_at": now.isoformat(),
        "branch": branch,
        "head": head,
        "suggested": {
            "version": latest["version"],
            "title": latest["title"],
            "notes": latest["notes"],
        },
        "history": history,
        "commits": commits[:25],
        "customer_lines": latest.get("customer_lines") or [],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {OUT} ({len(commits)} commits, {len(history)} history patches, head={head})"
    )


if __name__ == "__main__":
    main()
