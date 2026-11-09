#!/usr/bin/env python3
"""NUCLEAR_HOLD_FIX_V1 — last-line defense: never let send clear hold."""
from pathlib import Path

def main():
    p = Path("src/context/PlatformContext.tsx")
    if not p.exists():
        print("skip PlatformContext")
        return
    s = p.read_text()
    a = (
        "await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), "
        "status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() })"
        ".eq('id', conversationId);"
    )
    b = (
        "const _cur = conversations.find((c) => c.id === conversationId);\n"
        "      const _st = String(_cur?.status || '').toLowerCase();\n"
        "      const _held = _st === 'on_hold' || _st === 'on-hold' || _st === 'hold' "
        "|| String(_cur?.preview || '').startsWith('__HOLD__');\n"
        "      if (_held && sender === 'customer') return;\n"
        "      const _ns = _held ? 'on_hold' : 'active';\n"
        "      const _pv = _held ? '__HOLD__' + msg.text.slice(0, 120) : msg.text.slice(0, 120);\n"
        "      await supabase.from('chat_conversations').update({ preview: _pv, status: _ns, "
        "unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() })"
        ".eq('id', conversationId);"
    )
    if a in s:
        s = s.replace(a, b, 1)
        print("NUCLEAR: supabase send hold-safe")
    else:
        print("NUCLEAR: supabase send pattern already changed or missing")

    a2 = (
        "setConversations((prev) => prev.map((c) => c.id === conversationId ? "
        "{ ...c, messages: [...(c.messages || []), msg], preview: msg.text, "
        "status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));"
    )
    b2 = (
        "setConversations((prev) => prev.map((c) => {\n"
        "        if (c.id !== conversationId) return c;\n"
        "        const _st = String(c.status || '').toLowerCase();\n"
        "        const _held = _st === 'on_hold' || _st === 'on-hold' || _st === 'hold' "
        "|| String(c.preview || '').startsWith('__HOLD__');\n"
        "        if (_held && sender === 'customer') return c;\n"
        "        const _ns = _held ? 'on_hold' : 'active';\n"
        "        const _pv = _held ? '__HOLD__' + msg.text : msg.text;\n"
        "        return { ...c, messages: [...(c.messages || []), msg], preview: _pv, "
        "status: _ns as ChatConversation['status'], "
        "unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 };\n"
        "      }));"
    )
    if a2 in s:
        s = s.replace(a2, b2, 1)
        print("NUCLEAR: local send hold-safe")

    if "NUCLEAR_HOLD_STATUS" not in s:
        old_patch = "const patch: Record<string, unknown> = { status: nextStatus, updated_at: new Date().toISOString() };"
        new_patch = (
            "// NUCLEAR_HOLD_STATUS\n"
            "    const _holdPrev = conversations.find((c) => c.id === id);\n"
            "    let _patchPreview = String(_holdPrev?.preview || '');\n"
            "    if (nextStatus === 'on_hold' && !_patchPreview.startsWith('__HOLD__')) "
            "_patchPreview = '__HOLD__' + _patchPreview;\n"
            "    if ((nextStatus === 'active' || status === 'active') && _patchPreview.startsWith('__HOLD__')) "
            "_patchPreview = _patchPreview.slice(8);\n"
            "    const patch: Record<string, unknown> = { status: nextStatus, updated_at: new Date().toISOString(), "
            "preview: _patchPreview };"
        )
        if old_patch in s:
            s = s.replace(old_patch, new_patch, 1)
            print("NUCLEAR: setChatStatus stamps preview")

    p.write_text(s)

    pv = Path("src/components/PortalLiveChatView.tsx")
    if pv.exists():
        t = pv.read_text()
        t2 = t
        if "startsWith('__HOLD__')" not in t and 'startsWith("__HOLD__")' not in t:
            t2 = t2.replace(
                "const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';",
                "const _hs = (conversation?.status || '').toLowerCase(); "
                "const isOnHold = _hs === 'on_hold' || _hs === 'on-hold' || _hs === 'hold' "
                "|| String(conversation?.preview || '').startsWith('__HOLD__');",
                1,
            )
        if "isOnHold) return" not in t2:
            t2 = t2.replace("if (!chatId || chatEnded) return;", "if (!chatId || chatEnded || isOnHold) return;", 1)
            t2 = t2.replace("if (!file || !chatId) return;", "if (!file || !chatId || chatEnded || isOnHold) return;", 1)
        if t2 != t:
            pv.write_text(t2)
            print("NUCLEAR: portal lock")
        else:
            print("NUCLEAR: portal already ok")
    print("NUCLEAR_DONE")

if __name__ == "__main__":
    main()
