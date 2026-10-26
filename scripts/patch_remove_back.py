#!/usr/bin/env python3
from pathlib import Path

p = Path("src/components/CustomerPortal.tsx")
t = p.read_text()
replacements = [
(
"""                <button type="button" onClick={() => setView('home')} className="flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700 mb-3">
                  <ArrowLeft size={16} /> Back
                </button>
""",
""
),
(
"""                <button type="button" onClick={() => setView('home')} className="flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700 mb-3"><ArrowLeft size={16} /> Back</button>
""",
""
),
]
count = 0
for a, b in replacements:
    n = t.count(a)
    if n:
        t = t.replace(a, b)
        count += n
        print(f"removed {n} block")
p.write_text(t)
print("CP ArrowLeft+Back remaining:", t.count("ArrowLeft size={16} /> Back"))

lp = Path("src/components/PortalLiveChat.tsx")
if lp.exists():
    lt = lp.read_text()
    for a in [
"""        <button type="button" onClick={onBack} className="flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700 mb-6">
          <ArrowLeft size={16} /> Back
        </button>
""",
"""        <button type="button" onClick={onBack} className="flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700">
          <ArrowLeft size={16} /> Back
        </button>
""",
    ]:
        if a in lt:
            lt = lt.replace(a, "")
            print("removed livechat back")
    lt = lt.replace(
"""      <div className="flex items-center justify-between mb-3">

        <button type="button" onClick={endAndLeave} className="text-xs text-zinc-400 hover:text-rose-600">
          End session
        </button>
      </div>
""",
"""      <div className="flex items-center justify-end mb-3">
        <button type="button" onClick={endAndLeave} className="text-xs text-zinc-400 hover:text-rose-600">
          End session
        </button>
      </div>
"""
    )
    lp.write_text(lt)
    print("LiveChat Back remaining:", lt.count("/> Back"))
