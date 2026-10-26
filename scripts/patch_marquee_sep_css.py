#!/usr/bin/env python3
from pathlib import Path
css_path = Path("src/portal-lounge.css")
if not css_path.exists():
    print("no css"); raise SystemExit(0)
css = css_path.read_text()
if ".portal-marquee-sep" in css:
    print("sep already")
    raise SystemExit(0)
needle = ".portal-marquee-text {"
insert = """.portal-marquee-item {
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}
.portal-marquee-sep {
  display: inline-block;
  opacity: 0.55;
  font-weight: 700;
  letter-spacing: 0.12em;
  padding: 0 0.35rem;
  user-select: none;
}
.portal-marquee-text {"""
if needle in css:
    css = css.replace(needle, insert, 1)
    css = css.replace(
        """.portal-marquee-segment {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  white-space: nowrap;
}""",
        """.portal-marquee-segment {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  white-space: nowrap;
  padding-right: 0.5rem;
}""",
        1,
    )
    css_path.write_text(css)
    print("sep css added")
else:
    print("needle miss")
