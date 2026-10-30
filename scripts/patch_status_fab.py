#!/usr/bin/env python3
"""Sidebar status colors match Active Now; floating status shortcut bottom-right."""
from pathlib import Path
import re

SIDEBAR = Path("src/components/Sidebar.tsx")
SA = Path("src/SystemApp.tsx")

STATUS_DOT_HELPER = '''
function statusDotClass(status?: string) {
  switch ((status || 'online').toLowerCase()) {
    case 'online':
      return 'bg-emerald-400';
    case 'away':
      return 'bg-sky-400';
    case 'busy':
      return 'bg-amber-300';
    case 'in_call':
      return 'bg-orange-400';
    case 'custom':
      return 'bg-white';
    case 'offline':
      return 'bg-zinc-500';
    default:
      return 'bg-emerald-400';
  }
}

function statusLabel(status?: string) {
  switch ((status || 'online').toLowerCase()) {
    case 'online':
      return 'Available';
    case 'away':
      return 'Away';
    case 'busy':
      return 'Busy';
    case 'in_call':
      return 'In a call';
    case 'custom':
      return 'Custom';
    case 'offline':
      return 'Offline';
    default:
      return status || 'Available';
  }
}
'''

if SIDEBAR.exists():
    t = SIDEBAR.read_text()
    if "status-dot-match-v1" not in t:
        if "function statusDotClass" not in t:
            idx = t.find("interface SidebarProps")
            if idx > 0:
                t = t[:idx] + STATUS_DOT_HELPER + "\n" + t[idx:]
            else:
                t = STATUS_DOT_HELPER + "\n" + t
        old_span = """            <span
              className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-zinc-950 ${
                agentStatus === 'online' ? 'bg-emerald-400' : agentStatus === 'busy' ? 'bg-amber-400' : agentStatus === 'away' ? 'bg-orange-400' : 'bg-zinc-500'
              }`}
              title={agentStatus}
            />"""
        new_span = """            <span
              className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-zinc-950 ${statusDotClass(agentStatus)}`}
              title={statusLabel(agentStatus)}
            />"""
        if old_span in t:
            t = t.replace(old_span, new_span, 1)
        else:
            t2, n = re.subn(
                r'<span\s+className=\{`absolute -bottom-0\.5 -right-0\.5 w-3 h-3 rounded-full border-2 border-zinc-950 \$\{[^`]+\}`\}\s+title=\{agentStatus\}\s*/>',
                '<span className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-zinc-950 ${statusDotClass(agentStatus)}`} title={statusLabel(agentStatus)} />',
                t, count=1,
            )
            if n:
                t = t2
        old_meta = """          <div className="flex-1 min-w-0 text-left">
            <div className="text-sm font-medium text-zinc-100 truncate">{resolvedName}</div>
            <div className="text-[11px] text-zinc-500 truncate">{userEmail}</div>
          </div>"""
        new_meta = """          <div className="flex-1 min-w-0 text-left">
            <div className="text-sm font-medium text-zinc-100 truncate">{resolvedName}</div>
            <div className="text-[11px] text-zinc-500 truncate">{userEmail}</div>
            <div className="text-[10px] mt-0.5 font-medium truncate">
              <span className="text-zinc-400">Online · </span>
              <span className={
                agentStatus === 'away' ? 'text-sky-400' :
                agentStatus === 'busy' ? 'text-amber-300' :
                agentStatus === 'in_call' ? 'text-orange-400' :
                agentStatus === 'custom' ? 'text-white' :
                agentStatus === 'offline' ? 'text-zinc-500' :
                'text-emerald-400'
              }>{statusLabel(agentStatus)}</span>
            </div>
          </div>"""
        if old_meta in t:
            t = t.replace(old_meta, new_meta, 1)
        t = "/* status-dot-match-v1 */\n" + t
        SIDEBAR.write_text(t)

if SA.exists():
    s = SA.read_text()
    if "status-fab-v1" not in s:
        if "const [statusFabOpen, setStatusFabOpen]" not in s:
            if "const [agentToast, setAgentToast]" in s:
                s = s.replace(
                    "const [agentToast, setAgentToast] = useState<{ title: string; body: string } | null>(null);",
                    "const [agentToast, setAgentToast] = useState<{ title: string; body: string } | null>(null);\n  const [statusFabOpen, setStatusFabOpen] = useState(false);",
                    1,
                )
            else:
                s = s.replace(
                    "const [activeNav, setActiveNav] = useState('dashboard');",
                    "const [activeNav, setActiveNav] = useState('dashboard');\n  const [statusFabOpen, setStatusFabOpen] = useState(false);",
                    1,
                )
        fab_jsx = '''
      {/* Floating status shortcut — bottom right */}
      <div className="fixed bottom-5 right-5 z-[80] flex flex-col items-end gap-2">
        {statusFabOpen && (
          <div className="mb-1 w-56 rounded-2xl border border-white/15 bg-zinc-950/95 backdrop-blur-md shadow-2xl shadow-black/40 p-2 space-y-1">
            <div className="px-2 py-1 text-[10px] uppercase tracking-wide text-zinc-500 font-semibold">Set status</div>
            {([
              ['online', 'Available', 'bg-emerald-400'],
              ['away', 'Away', 'bg-sky-400'],
              ['busy', 'Busy', 'bg-amber-300'],
              ['in_call', 'In a Call / Meeting', 'bg-orange-400'],
            ] as const).map(([id, label, dot]) => (
              <button
                key={id}
                type="button"
                onClick={() => {
                  void setPresenceStatus(id);
                  setStatusFabOpen(false);
                }}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left text-sm transition-colors ${
                  (currentAgent?.status || 'online') === id
                    ? 'bg-white/10 text-white'
                    : 'text-zinc-300 hover:bg-white/5'
                }`}
              >
                <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${dot}`} />
                {label}
              </button>
            ))}
            <button
              type="button"
              onClick={() => {
                setStatusFabOpen(false);
                setActiveNav('profile');
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left text-sm text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
            >
              <span className="w-2.5 h-2.5 rounded-full shrink-0 bg-white" />
              Custom status…
            </button>
          </div>
        )}
        <button
          type="button"
          onClick={() => setStatusFabOpen((o) => !o)}
          className="flex items-center gap-2 pl-3 pr-4 py-2.5 rounded-full border border-white/20 bg-zinc-950/90 backdrop-blur-md shadow-lg shadow-black/30 text-sm font-medium text-white hover:bg-zinc-900 transition-colors"
          title="Change status"
        >
          <span
            className={`w-3 h-3 rounded-full shrink-0 ${
              (currentAgent?.status || 'online') === 'away'
                ? 'bg-sky-400'
                : (currentAgent?.status || 'online') === 'busy'
                  ? 'bg-amber-300'
                  : (currentAgent?.status || 'online') === 'in_call'
                    ? 'bg-orange-400'
                    : (currentAgent?.status || 'online') === 'custom'
                      ? 'bg-white'
                      : (currentAgent?.status || 'online') === 'offline'
                        ? 'bg-zinc-500'
                        : 'bg-emerald-400'
            }`}
          />
          {(currentAgent?.status || 'online') === 'away'
            ? 'Away'
            : (currentAgent?.status || 'online') === 'busy'
              ? 'Busy'
              : (currentAgent?.status || 'online') === 'in_call'
                ? 'In a call'
                : (currentAgent?.status || 'online') === 'custom'
                  ? (currentAgent?.status_message || 'Custom')
                  : (currentAgent?.status || 'online') === 'offline'
                    ? 'Offline'
                    : 'Available'}
        </button>
      </div>
'''
        if '{/* Floating status shortcut' not in s:
            marker = '<div className="app-cosmos flex min-h-screen">'
            if marker in s:
                s = s.replace(marker, fab_jsx + "\n      " + marker, 1)
        s = "/* status-fab-v1 */\n" + s
        SA.write_text(s)
print("done")
