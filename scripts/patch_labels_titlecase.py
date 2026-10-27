#!/usr/bin/env python3
"""Title-case nav labels; rename Submit request → Submit Ticket (sidebar, topbar, content)."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "labels-titlecase-v1" in c:
    print("cp already")
else:
    reps = [
        ("title: 'Submit a request'", "title: 'Submit Ticket'"),
        ("title: 'Track a ticket'", "title: 'Track a Ticket'"),
        ("title: 'Help articles'", "title: 'Help Articles'"),
        ("title: 'Live chat'", "title: 'Live Chat'"),
        ("title: 'My tickets'", "title: 'My Tickets'"),
        ("label: 'Submit request'", "label: 'Submit Ticket'"),
        ("label: 'Live chat'", "label: 'Live Chat'"),
        ("label: 'Track ticket'", "label: 'Track Ticket'"),
        ("label: 'My tickets'", "label: 'My Tickets'"),
        ("label: 'Help articles'", "label: 'Help Articles'"),
        (">Submit a request</h1>", ">Submit Ticket</h1>"),
        (">{saving ? 'Submitting…' : 'Submit request'}", ">{saving ? 'Submitting…' : 'Submit Ticket'}"),
        (">My tickets</h1>", ">My Tickets</h1>"),
        (">Help articles</h1>", ">Help Articles</h1>"),
        (">Track ticket</button>", ">Track Ticket</button>"),
    ]
    for a, b in reps:
        if a in c:
            c = c.replace(a, b)
            print(f"cp: {a[:48]}")
        else:
            print(f"cp miss: {a[:48]}")
    if "/* labels-titlecase-v1 */" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* labels-titlecase-v1 */\nexport default function CustomerPortal",
            1,
        )
    cp.write_text(c)
    print("cp done")

sb = Path("src/components/Sidebar.tsx")
if sb.exists():
    s = sb.read_text()
    if "labels-titlecase-v1" not in s:
        s = s.replace("label: 'Admin features'", "label: 'Admin Features'")
        if "/* labels-titlecase-v1 */" not in s:
            s = s.replace(
                "function BrandMark",
                "/* labels-titlecase-v1 */\nfunction BrandMark",
                1,
            )
        sb.write_text(s)
        print("sidebar done")
    else:
        print("sidebar already")

ph = Path("src/components/PortalHome.tsx")
if ph.exists():
    p = ph.read_text()
    p2 = (
        p.replace("Open Submit request.", "Open Submit Ticket.")
        .replace("Use Track ticket or My tickets", "Use Track Ticket or My Tickets")
        .replace("→ Live chat.", "→ Live Chat.")
        .replace("Submit request or Live chat", "Submit Ticket or Live Chat")
    )
    if p2 != p:
        ph.write_text(p2)
        print("portalhome done")
    else:
        print("portalhome unchanged")

print("done")
