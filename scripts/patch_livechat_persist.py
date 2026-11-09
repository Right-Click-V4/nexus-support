#!/usr/bin/env python3
"""Surgical livechat fixes: persist chatId + ticket->branch."""
from pathlib import Path
p = Path("src/components/PortalLiveChatView.tsx")
if not p.exists():
    print("no PLV"); raise SystemExit(0)
t = p.read_text()
if "CHAT_ID_KEY" in t:
    print("already patched"); raise SystemExit(0)

if "const QUICK_REPLIES" in t and "CHAT_ID_KEY" not in t:
    t = t.replace(
        "const QUICK_REPLIES = [",
        "const CHAT_ID_KEY = 'nexus-portal-live-chat-id';\n\nconst QUICK_REPLIES = [",
    )

t = t.replace("const { agents } = useTickets();", "const { agents, tickets } = useTickets();")

old = "const [chatId, setChatId] = useState<string | null>(null);"
new = """const [chatId, setChatId] = useState<string | null>(() => {
    try { return sessionStorage.getItem(CHAT_ID_KEY); } catch { return null; }
  });"""
if old in t:
    t = t.replace(old, new)

marker = """  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);"""
extra = """  useEffect(() => {
    void refreshPlatform();
  }, [refreshPlatform]);

  useEffect(() => {
    try {
      if (chatId) sessionStorage.setItem(CHAT_ID_KEY, chatId);
      else sessionStorage.removeItem(CHAT_ID_KEY);
    } catch { /* ignore */ }
  }, [chatId]);

  useEffect(() => {
    if (chatId) return;
    const em = (user?.email || email || '').trim().toLowerCase();
    if (!em || !conversations?.length) return;
    const open = conversations.find((c) => {
      const st = (c.status || '').toLowerCase();
      if (st === 'ended' || st === 'archived') return false;
      return (c.customer_email || '').toLowerCase() === em;
    });
    if (open?.id) setChatId(open.id);
  }, [conversations, chatId, user?.email, email]);

  useEffect(() => {
    const raw = ticketId.trim();
    if (!raw) return;
    const lower = raw.toLowerCase();
    const match = (tickets || []).find((tk) => {
      const id = String(tk.id || '').toLowerCase();
      const num = String((tk as { ticket_number?: string }).ticket_number || '').toLowerCase();
      return id === lower || num === lower || id.endsWith(lower);
    });
    if (!match) return;
    if (match.branch && match.branch.trim()) setBranch(match.branch.trim());
    if (match.id && match.id !== ticketId) setTicketId(match.id);
  }, [ticketId, tickets]);"""
if marker in t and "sessionStorage.setItem(CHAT_ID_KEY" not in t:
    t = t.replace(marker, extra)

p.write_text(t)
print("PLV patched", "CHAT_ID_KEY" in t, p.stat().st_size)
