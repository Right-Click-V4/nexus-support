#!/usr/bin/env python3
"""Fix follow-up modal placed outside root div (build break)."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-jsx-fix-v1" in c:
    print("already")
    raise SystemExit(0)

old = """                  </aside>
                </div>
              </div>

                {followUpTicket && ("""
new = """                  </aside>
                </div>

                {followUpTicket && ("""
if old in c:
    c = c.replace(old, new, 1)
    print("opened parent ok")
else:
    print("pattern1 miss or already fixed")

idx = c.find("{followUpTicket && (")
if idx > 0:
    end = c.find("            })()}", idx)
    region = c[idx:end]
    if "                )}\n              );" in region and "                )}\n              </div>\n              );" not in region:
        c = c[:idx] + region.replace(
            "                )}\n              );",
            "                )}\n              </div>\n              );",
            1,
        ) + c[end:]
        print("close root ok")
    else:
        print("close check done")

if "mytickets-jsx-fix-v1" not in c:
    c = "/* mytickets-jsx-fix-v1 */\n" + c
cp.write_text(c)
print("done")
