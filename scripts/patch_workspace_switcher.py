#!/usr/bin/env python3
"""Allow Agent/Admin portal preview; bidirectional switcher; match light topbar to sidebar."""
from pathlib import Path
import re

pag = Path("src/components/PortalAuthGate.tsx")
if "agent-portal-preview-v1" not in pag.read_text():
    pag.write_text(Path(__file__).with_name("../components/PortalAuthGate.tsx").read_text() if False else open("src/components/PortalAuthGate.tsx").read_text())
    # file already deployed via direct push; keep gate idempotent
    print("gate skip-write")
else:
    print("gate already")

sysp = Path("src/SystemApp.tsx")
sc = sysp.read_text()
if "workspace-switcher-v1" not in sc:
    old_shell = """  return (
    <PortalAuthGate
      onOpenAgent={() => {
        window.location.hash = '';
      }}
    >
      <CustomerPortal />
    </PortalAuthGate>
  );
}"""
    new_shell = """  const goAgent = () => {
    window.location.hash = 'agent';
  };

  return (
    <PortalAuthGate onOpenAgent={goAgent} onBackToAgent={goAgent}>
      <CustomerPortal
        onBackToAgent={
          accountRole === 'agent' || accountRole === 'admin' || admin
            ? goAgent
            : undefined
        }
      />
    </PortalAuthGate>
  );
}"""
    if old_shell in sc:
        sc = sc.replace(old_shell, new_shell, 1)
        print("PortalShell ok")
    else:
        print("PortalShell miss")

    new_btn_block = """              {(accountRole === 'agent' || accountRole === 'admin' || admin) && (
                <button
                  type="button"
                  onClick={() => {
                    window.location.hash = 'portal';
                  }}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-white px-3 py-1.5 rounded-lg border border-violet-700/40 bg-violet-600 hover:bg-violet-700 shadow-md shadow-violet-600/25 transition-colors"
                  title="Preview Customer Portal"
                >
                  <ExternalLink size={14} className="text-white" />
                  <span className="hidden sm:inline">Customer Portal</span>
                </button>
              )}"""

    m = re.search(
        r"<button\s+type=\"button\"\s+onClick=\{\(\) => \{\s*window\.location\.hash = 'portal';\s*\}\}[\s\S]*?Customer Portal</span>\s*</button>",
        sc,
    )
    if m:
        sc = sc[: m.start()] + new_btn_block + sc[m.end() :]
        print("agent btn ok")
    elif "Preview Customer Portal" in sc:
        print("agent btn already")
    else:
        print("agent btn miss")

    sc = "/* workspace-switcher-v1 */\n" + sc
    sysp.write_text(sc)
    print("SystemApp done")
else:
    print("SystemApp already")

cp = Path("src/components/CustomerPortal.tsx")
cc = cp.read_text()
if "workspace-switcher-portal-v1" not in cc:
    old_side = """          {onBackToAgent && (
            <button type="button" onClick={onBackToAgent} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-500 hover:bg-white/5 hover:text-zinc-200">
              <ExternalLink size={16} /> Agent desk
            </button>
          )}"""
    new_side = """          {onBackToAgent && (
            <button
              type="button"
              onClick={onBackToAgent}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold text-violet-800 dark:text-violet-100 bg-violet-100/90 dark:bg-violet-500/20 border border-violet-400/40 hover:bg-violet-200 dark:hover:bg-violet-500/30"
            >
              <ExternalLink size={16} /> Agent Workspace
            </button>
          )}"""
    if old_side in cc:
        cc = cc.replace(old_side, new_side, 1)
        print("cp sidebar switch ok")
    else:
        print("cp sidebar miss")

    if "switch-to-agent-top" not in cc:
        marker = 'title="Sign out"'
        if marker in cc:
            idx = cc.find(marker)
            chunk_start = cc.rfind("<button", 0, idx)
            if chunk_start > 0:
                insert = """              {onBackToAgent && (
                <button
                  type="button"
                  onClick={onBackToAgent}
                  className="switch-to-agent-top inline-flex items-center gap-1.5 text-xs font-bold text-white px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 border border-violet-500/50 shadow-md"
                  title="Back to Agent Workspace"
                >
                  <ExternalLink size={14} />
                  <span className="hidden sm:inline">Agent Workspace</span>
                </button>
              )}
"""
                cc = cc[:chunk_start] + insert + cc[chunk_start:]
                print("cp topbar switch ok")
            else:
                print("cp topbar insert miss")
        else:
            print("cp topbar skip")

    if "ExternalLink" not in cc.split("from 'lucide-react'")[0]:
        cc2 = re.sub(
            r"import \{([^}]+)\} from 'lucide-react'",
            lambda m: (
                m.group(0)
                if "ExternalLink" in m.group(1)
                else "import {" + m.group(1).rstrip() + ", ExternalLink } from 'lucide-react'"
            ),
            cc,
            count=1,
        )
        cc = cc2
        print("ExternalLink import")

    cc = "/* workspace-switcher-portal-v1 */\n" + cc
    cp.write_text(cc)
    print("CustomerPortal done")
else:
    print("CustomerPortal already")

css = Path("src/index.css")
s = css.read_text() if css.exists() else ""
if "workspace-switcher-chrome-v1" not in s:
    block = r"""
/* workspace-switcher-chrome-v1 — light topbar matches sidebar; solid switcher */
html.nexus-light .app-cosmos .nexus-topbar,
html.nexus-light .nexus-topbar {
  background: linear-gradient(180deg, rgba(196, 181, 253, 0.92) 0%, rgba(167, 139, 250, 0.88) 45%, rgba(196, 181, 253, 0.90) 100%) !important;
  border-bottom: 1px solid rgba(76, 29, 149, 0.55) !important;
}
html.nexus-light .app-cosmos aside,
html.nexus-light .app-cosmos aside.portal-sidebar,
html.nexus-light .app-cosmos > aside {
  background: linear-gradient(180deg, rgba(196, 181, 253, 0.92) 0%, rgba(167, 139, 250, 0.88) 45%, rgba(196, 181, 253, 0.90) 100%) !important;
}
"""
    css.write_text(s + "\n" + block)
    print("css ok")
else:
    print("css already")
print("done")
