#!/usr/bin/env python3
"""Wire customer Help Articles to Platform knowledge base (published only)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CP = ROOT / "src" / "components" / "CustomerPortal.tsx"

IMPORT = "import PortalHelpArticles from './PortalHelpArticles';\n"

def main() -> None:
    if not CP.exists():
        print("CustomerPortal.tsx missing")
        return
    text = CP.read_text(encoding="utf-8")
    if "PortalHelpArticles" in text and "view === 'help'" in text and "<PortalHelpArticles" in text:
        print("already wired")
        return

    if "import PortalHelpArticles" not in text:
        # after usePlatform import if present
        if "from '../context/PlatformContext'" in text:
            text = text.replace(
                "from '../context/PlatformContext';\n",
                "from '../context/PlatformContext';\n" + IMPORT,
                1,
            )
        else:
            text = IMPORT + text

    # Replace entire help view block with component
    start = text.find("{view === 'help' && (")
    if start < 0:
        start = text.find('view === "help" && (')
    if start < 0:
        print("help view not found")
        CP.write_text(text, encoding="utf-8")
        return

    # Find matching closing for this view block: )}
    # Look for next "{view ===" after start
    next_view = text.find("{view ===", start + 5)
    if next_view < 0:
        next_view = len(text)
    # Walk back to include the closing `)}` of help block
    block = text[start:next_view]
    # Replace block
    replacement = "{view === 'help' && (\n              <PortalHelpArticles />\n            )}\n\n            "
    text = text[:start] + replacement + text[next_view:]
    CP.write_text(text, encoding="utf-8")
    print("wired PortalHelpArticles into CustomerPortal")

if __name__ == "__main__":
    main()
