#!/usr/bin/env python3
"""HOLD_PRESERVE_V3 — durable hold via status + __HOLD__ preview marker; block customer; notify; badge."""
from pathlib import Path

def patch_platform():
    p = Path('src/context/PlatformContext.tsx')
    if not p.exists():
        print('skip PlatformContext')
        return
    s = p.read_text()
    if 'HOLD_PRESERVE_V3' in s and 'previewIsHeld' in s:
        print('PlatformContext already V3')
        return

    if 'CHAT_HOLD_KEY' not in s:
        helpers = r'''
const CHAT_HOLD_KEY = 'nexus-chat-hold-v1';
const HOLD_MARK = '__HOLD__';
function previewIsHeld(preview?: string | null) {
  return String(preview || '').startsWith(HOLD_MARK);
}
function withHoldMark(preview?: string | null) {
  const t = String(preview || '');
  return t.startsWith(HOLD_MARK) ? t : HOLD_MARK + t;
}
function stripHoldMark(preview?: string | null) {
  const t = String(preview || '');
  return t.startsWith(HOLD_MARK) ? t.slice(HOLD_MARK.length) : t;
}
function readChatHeld(): Set<string> {
  try {
    const raw = localStorage.getItem(CHAT_HOLD_KEY);
    const arr = raw ? (JSON.parse(raw) as string[]) : [];
    return new Set(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set();
  }
}
function writeChatHeld(ids: Set<string>) {
  try {
    localStorage.setItem(CHAT_HOLD_KEY, JSON.stringify([...ids]));
  } catch { /* ignore */ }
}
function markChatHeld(id: string) {
  const s = readChatHeld();
  s.add(id);
  writeChatHeld(s);
}
function clearChatHeld(id: string) {
  const s = readChatHeld();
  if (s.delete(id)) writeChatHeld(s);
}
function isChatHeld(id: string): boolean {
  return readChatHeld().has(id);
}

'''
        s = s.replace("const CHAT_DELETED_KEY = 'nexus-chat-deleted-v1';", helpers + "const CHAT_DELETED_KEY = 'nexus-chat-deleted-v1';", 1)

    old_send = """  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));
    }
  };"""
    new_send = """  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {
    // HOLD_PRESERVE_V3
    const current = conversations.find((c) => c.id === conversationId);
    const curStatus = (current?.status || '').toLowerCase();
    const held =
      curStatus === 'on_hold' ||
      curStatus === 'on-hold' ||
      curStatus === 'hold' ||
      isChatHeld(conversationId) ||
      previewIsHeld(current?.preview);
    if (held && sender === 'customer') {
      return;
    }
    let nextStatus: ChatConversation['status'] = (current?.status as ChatConversation['status']) || 'active';
    if (held) {
      nextStatus = 'on_hold';
    } else if (curStatus === 'waiting' || !curStatus) {
      nextStatus = 'active';
    } else if (curStatus === 'ended' || curStatus === 'archived' || curStatus === 'closed') {
      nextStatus = 'active';
    } else {
      nextStatus = (current?.status as ChatConversation['status']) || 'active';
    }
    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };
    const nextPreview = held ? withHoldMark(msg.text.slice(0, 120)) : stripHoldMark(msg.text.slice(0, 120));
    if (supabase) {
      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });
      await supabase
        .from('chat_conversations')
        .update({
          preview: nextPreview,
          status: nextStatus,
          unread: sender === 'customer' ? 1 : 0,
          updated_at: new Date().toISOString(),
        })
        .eq('id', conversationId);
      await refreshPlatform();
    } else {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === conversationId
            ? {
                ...c,
                messages: [...(c.messages || []), msg],
                preview: nextPreview,
                status: nextStatus,
                unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,
              }
            : c,
        ),
      );
    }
  };"""
    if old_send in s:
        s = s.replace(old_send, new_send, 1)
        print('sendChatMessage V3')
    elif 'HOLD_PRESERVE_V3' in s:
        print('send already V3')
    else:
        print('WARN send not patched')

    if 'withHoldMark(prevPreview)' not in s and 'nextPreview = withHoldMark' not in s:
        s = s.replace(
            "if (status === 'active' || nextStatus === 'active') clearChatArchived(id);",
            "if (status === 'active' || nextStatus === 'active') { clearChatArchived(id); clearChatHeld(id); }\n    if (status === 'on_hold' || nextStatus === 'on_hold') markChatHeld(id);",
            1,
        )
        s = s.replace(
            "const patch: Record<string, unknown> = { status: nextStatus, updated_at: new Date().toISOString() };",
            "const currentHold = conversations.find((c) => c.id === id);\n    const prevPreview = String(currentHold?.preview || '');\n    let nextPreview = prevPreview;\n    if (status === 'on_hold' || nextStatus === 'on_hold') nextPreview = withHoldMark(prevPreview);\n    else if (status === 'active' || nextStatus === 'active') nextPreview = stripHoldMark(prevPreview);\n    const patch: Record<string, unknown> = { status: nextStatus, updated_at: new Date().toISOString(), preview: nextPreview };",
            1,
        )
        print('setChatStatus marks')

    old_fb = """      if (error && nextStatus === 'on_hold') {
        const retry = await supabase.from('chat_conversations').update({ status: 'waiting', updated_at: new Date().toISOString() }).eq('id', id);
        error = retry.error;
        if (!error) setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, status: 'waiting' as ChatConversation['status'] } : c)));
      }"""
    new_fb = """      if (error && nextStatus === 'on_hold') {
        const retry = await supabase
          .from('chat_conversations')
          .update({ preview: withHoldMark(String(patch.preview || '')), updated_at: new Date().toISOString() })
          .eq('id', id);
        if (retry.error) console.warn('hold marker persist failed', retry.error?.message);
        error = null;
      }"""
    if old_fb in s:
        s = s.replace(old_fb, new_fb, 1)
        print('fallback fixed')

    if 'previewIsHeld((c as { preview?: string }).preview)' not in s and 'previewIsHeld(c.preview)' not in s:
        needle = """      setConversations(
        (chats.data as ChatConversation[]).map((c) => ({
          ...c,
          messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
            ...mm,
            text: mm.text || mm.body || '',
            body: mm.body || mm.text || '',
          })),
        })),
      );"""
        repl = """      const heldIds = readChatHeld();
      setConversations(
        (chats.data as ChatConversation[]).map((c) => {
          const st = (c.status || '').toLowerCase();
          const forcedHold =
            (heldIds.has(c.id) || previewIsHeld((c as { preview?: string }).preview)) &&
            st !== 'ended' &&
            st !== 'archived' &&
            st !== 'closed';
          return {
            ...c,
            status: forcedHold ? ('on_hold' as ChatConversation['status']) : c.status,
            messages: (byConv[c.id] || c.messages || []).map((mm: ChatMessage & { body?: string }) => ({
              ...mm,
              text: mm.text || mm.body || '',
              body: mm.body || mm.text || '',
            })),
          };
        }),
      );"""
        if needle in s:
            s = s.replace(needle, repl, 1)
            print('refresh overlay')

    if 'NEW_LIVECHAT_NOTIF_V1' not in s:
        needle = 'const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {'
        insert = """const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {
    const notifyNewChat = () => {
      // NEW_LIVECHAT_NOTIF_V1
      try {
        const title = 'New live chat';
        const body = `${customer_name || 'Customer'} is waiting for an agent`;
        if (supabase) {
          void supabase.from('notifications').insert({ title, body, link: '#/chat', read: false });
        }
        setNotifications((prev) => [
          { id: `n-chat-${Date.now()}`, title, body, link: '#/chat', read: false, created_at: new Date().toISOString() },
          ...prev,
        ]);
      } catch { /* ignore */ }
    };"""
        if needle in s:
            s = s.replace(needle, insert, 1)
            s = s.replace(
                'await refreshPlatform();\n        return d2 as ChatConversation;',
                'await refreshPlatform();\n        notifyNewChat();\n        return d2 as ChatConversation;',
                1,
            )
            s = s.replace(
                'await refreshPlatform();\n      return data as ChatConversation;',
                'await refreshPlatform();\n      notifyNewChat();\n      return data as ChatConversation;',
                1,
            )
            s = s.replace(
                'setConversations((p) => [c, ...p]);\n    return c;',
                'setConversations((p) => [c, ...p]);\n    notifyNewChat();\n    return c;',
                1,
            )
            print('notif')

    if 'HOLD_PRESERVE_V3' not in s:
        s = s.replace('/* delete-hold-v1 */', '/* delete-hold-v1 */\n/* HOLD_PRESERVE_V3 */', 1)
    p.write_text(s)
    print('PlatformContext done')


def patch_portal():
    pv = Path('src/components/PortalLiveChatView.tsx')
    if not pv.exists():
        return
    t = pv.read_text()
    if "__HOLD__" not in t:
        t = t.replace(
            "const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';",
            "const _holdSt = (conversation?.status || '').toLowerCase();\n  const _prev = String(conversation?.preview || '');\n  const isOnHold =\n    _holdSt === 'on_hold' || _holdSt === 'on-hold' || _holdSt === 'hold' || _prev.startsWith('__HOLD__'); // HOLD_PRESERVE_V3",
            1,
        )
    t = t.replace("if (!chatId || chatEnded) return;", "if (!chatId || chatEnded || isOnHold) return;", 1)
    t = t.replace("if (!file || !chatId) return;", "if (!file || !chatId || chatEnded || isOnHold) return;", 1)
    pv.write_text(t)
    print('portal V3')


def patch_shell():
    sc = Path('src/SystemAppCore.tsx')
    if not sc.exists() or 'waitingChatCount' in sc.read_text():
        print('shell skip/ok')
        return
    t = sc.read_text()
    a = """  const {
    notifications,
    unreadCount,
    markNotificationRead,
    markAllNotificationsRead,
    deleteNotification,
    deleteAllNotifications,
  } = usePlatform();"""
    b = """  const {
    notifications,
    unreadCount,
    conversations,
    markNotificationRead,
    markAllNotificationsRead,
    deleteNotification,
    deleteAllNotifications,
  } = usePlatform();
  const waitingChatCount = (conversations || []).filter((c) => {
    const st = (c.status || '').toLowerCase();
    return st === 'waiting' || st === 'on_hold' || st === 'on-hold' || String(c.preview || '').startsWith('__HOLD__') || (c.unread || 0) > 0;
  }).length;"""
    if a in t:
        t = t.replace(a, b, 1)
        t = t.replace(
            "        isAdmin={!!isAdmin}\n      />",
            "        isAdmin={!!isAdmin}\n        chatBadge={waitingChatCount || undefined}\n      />",
            1,
        )
        sc.write_text(t)
        print('shell badge')


def patch_livechat_page():
    p = Path('src/components/LiveChatPage.tsx')
    if not p.exists():
        return
    t = p.read_text()
    if 'isConvOnHold' in t:
        print('LiveChatPage ok')
        return
    t = t.replace(
        'export default function LiveChatPage',
        "function isConvOnHold(c: { status?: string; preview?: string } | null | undefined) {\n  const st = (c?.status || '').toLowerCase();\n  if (st === 'on_hold' || st === 'on-hold' || st === 'hold') return true;\n  return String(c?.preview || '').startsWith('__HOLD__');\n}\n\nexport default function LiveChatPage",
        1,
    )
    t = t.replace(
        "(c.status || '').toLowerCase() === 'on_hold' || (c.status || '').toLowerCase() === 'waiting'",
        "isConvOnHold(c) || (c.status || '').toLowerCase() === 'waiting'",
    )
    t = t.replace(
        "(selected.status || '').toLowerCase() === 'on_hold' || (selected.status || '').toLowerCase() === 'waiting'",
        "isConvOnHold(selected) || (selected.status || '').toLowerCase() === 'waiting'",
    )
    p.write_text(t)
    print('LiveChatPage hold UI')


patch_platform()
patch_portal()
patch_shell()
patch_livechat_page()
print('DONE V3')
