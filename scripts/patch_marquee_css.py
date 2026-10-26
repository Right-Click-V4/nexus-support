#!/usr/bin/env python3
"""Ensure marquee CSS uses seamless full-width LTR segments (no mid-bar gaps)."""
from pathlib import Path

p = Path("src/portal-lounge.css")
t = p.read_text()

if "portal-marquee-segment" in t and "portal-marquee-probe" in t:
    print("marquee css already patched")
    raise SystemExit(0)

marker = ".portal-marquee-viewport {"
idx = t.find(marker)
if idx < 0:
    raise SystemExit("portal-marquee-viewport not found")

# Replace from viewport block through keyframes portal-marquee-scroll
end_marker = ".portal-marquee-toggle {"
end = t.find(end_marker, idx)
if end < 0:
    raise SystemExit("portal-marquee-toggle not found")

block = '''.portal-marquee-viewport {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  position: relative;
  mask-image: linear-gradient(90deg, transparent 0, #000 12px, #000 calc(100% - 12px), transparent);
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 12px, #000 calc(100% - 12px), transparent);
}
.portal-marquee-track {
  display: inline-flex;
  align-items: center;
  flex-wrap: nowrap;
  width: max-content;
  will-change: transform;
  animation-name: portal-marquee-scroll;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  --marquee-shift: 0px;
  opacity: 0;
}
.portal-marquee-track.is-ready {
  opacity: 1;
}
.portal-marquee-track.is-paused {
  animation-play-state: paused;
}
.portal-marquee-segment {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  white-space: nowrap;
}
.portal-marquee-text {
  display: inline-block;
  font-size: 12px;
  font-weight: 550;
  letter-spacing: 0.01em;
  white-space: nowrap;
}
.portal-marquee-probe {
  position: absolute;
  visibility: hidden;
  pointer-events: none;
  left: 0;
  top: 0;
  white-space: nowrap;
}
@keyframes portal-marquee-scroll {
  0% { transform: translate3d(calc(-1 * var(--marquee-shift)), 0, 0); }
  100% { transform: translate3d(0, 0, 0); }
}
'''

t = t[:idx] + block + t[end:]
p.write_text(t)
print("marquee css patched")
