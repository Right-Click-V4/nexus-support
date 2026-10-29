#!/usr/bin/env python3
"""Copy icon on My Tickets IDs; Live Chat locked email + required ticket number."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-copy-id-v1" not in c:
    if "Copy" not in c.split("from 'lucide-react'")[0][-200:]:
        c = c.replace(
            "MoreVertical, Info, Send, Bell,",
            "MoreVertical, Info, Send, Bell, Copy, Check,",
            1,
        )
        print("cp import")

    if "copiedTicketId" not in c:
        c = c.replace(
            "const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);",
            "const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);\n"
            "  const [copiedTicketId, setCopiedTicketId] = useState<string | null>(null);",
            1,
        )
        print("cp state")

    old_td = """                              <td className="px-4 py-3 font-mono text-xs text-zinc-600 dark:text-zinc-300 whitespace-nowrap">{t.id}</td>"""
    new_td = """                              <td className="px-4 py-3 font-mono text-xs text-zinc-600 dark:text-zinc-300 whitespace-nowrap">
                                <span className="inline-flex items-center gap-1.5">
                                  <span>{t.id}</span>
                                  <button
                                    type="button"
                                    title="Copy ticket ID"
                                    aria-label={`Copy ${t.id}`}
                                    className="inline-flex p-1 rounded-md text-zinc-400 hover:text-violet-600 dark:hover:text-violet-300 hover:bg-violet-500/10 transition-colors"
                                    onClick={async (e) => {
                                      e.stopPropagation();
                                      try {
                                        await navigator.clipboard.writeText(t.id);
                                        setCopiedTicketId(t.id);
                                        window.setTimeout(() => setCopiedTicketId((cur) => (cur === t.id ? null : cur)), 1500);
                                      } catch {
                                        /* ignore */
                                      }
                                    }}
                                  >
                                    {copiedTicketId === t.id ? (
                                      <Check size={13} className="text-emerald-500" />
                                    ) : (
                                      <Copy size={13} />
                                    )}
                                  </button>
                                </span>
                              </td>"""
    if old_td in c:
        c = c.replace(old_td, new_td, 1)
        print("cp td ok")
    else:
        print("cp td miss")

    c = "/* mytickets-copy-id-v1 */\n" + c
    cp.write_text(c)
    print("cp done")
else:
    print("cp already")

plc = Path("src/components/PortalLiveChat.tsx")
p = plc.read_text()
if "livechat-ticket-required-v1" not in p:
    p = p.replace(
        "Connect with a support agent in real time. Your name is locked to your account.",
        "Connect with a support agent in real time.",
        1,
    )
    print("plc desc")

    old_email = """                  <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={field}
                    placeholder="you@email.com"
                  />"""
    new_email = """                  <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Email</label>
                  <input
                    type="email"
                    value={email}
                    readOnly
                    disabled
                    className={`${field} opacity-80 cursor-not-allowed`}
                    placeholder="you@email.com"
                  />
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">
                    Locked to your registered account email.
                  </p>"""
    if old_email in p:
        p = p.replace(old_email, new_email, 1)
        print("plc email")
    else:
        print("plc email miss")

    p = p.replace(
        """                    Ticket number <span className="font-normal text-zinc-400">(optional)</span>""",
        """                    Ticket number""",
        1,
    )
    p = p.replace(
        """                    Branch <span className="font-normal text-zinc-400">(optional)</span>""",
        """                    Branch""",
        1,
    )
    print("plc labels")

    old_ticket_input = """                  <input
                    value={ticketId}
                    onChange={(e) => setTicketId(e.target.value)}
                    placeholder="e.g. NX-2841"
                    className={`${field} font-mono`}
                  />"""
    new_ticket_input = """                  <input
                    value={ticketId}
                    onChange={(e) => setTicketId(e.target.value)}
                    placeholder="e.g. NX-2841"
                    required
                    className={`${field} font-mono`}
                  />"""
    if old_ticket_input in p:
        p = p.replace(old_ticket_input, new_ticket_input, 1)
        print("plc required attr")
    else:
        print("plc required miss")

    old_start = """    const nm = (accountName || name).trim();
    if (!nm) {
      setError('Account name is required — sign in again if this is empty.');
      return;
    }
    setStarting(true);
    setError('');
    try {
      const br = branch.trim() || undefined;
      const c = await createChat(nm, email.trim() || undefined, {
        branch: br,
        ticket_id: ticketId.trim() || undefined,
      });"""
    new_start = """    const nm = (accountName || name).trim();
    if (!nm) {
      setError('Account name is required — sign in again if this is empty.');
      return;
    }
    const tid = ticketId.trim();
    if (!tid) {
      setError('Ticket number is required.');
      return;
    }
    setStarting(true);
    setError('');
    try {
      const br = branch.trim() || undefined;
      const c = await createChat(nm, (user?.email || email).trim() || undefined, {
        branch: br,
        ticket_id: tid,
      });"""
    if old_start in p:
        p = p.replace(old_start, new_start, 1)
        print("plc start")
    else:
        print("plc start miss")

    p = p.replace(
        "if (ticketId.trim()) parts.push(`Ticket: ${ticketId.trim()}.`);",
        "if (tid) parts.push(`Ticket: ${tid}.`);",
        1,
    )

    p = "/* livechat-ticket-required-v1 */\n" + p
    plc.write_text(p)
    print("plc done")
else:
    print("plc already")
print("done")
