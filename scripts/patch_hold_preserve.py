#!/usr/bin/env python3
"""HOLD_PRESERVE_V2 — keep on_hold when agent sends; block customer; notify new chats; badge."""
from pathlib import Path

def patch_platform():
    p = Path('src/context/PlatformContext.tsx')
    if not p.exists():
        print('skip PlatformContext')
        return
    s = p.read_text()

    old_send = (
        "  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {\n"
        "    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };\n"
        "    if (supabase) {\n"
        "      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });\n"
        "      await supabase.from('chat_conversations').update({ preview: msg.text.slice(0, 120), status: 'active', unread: sender === 'customer' ? 1 : 0, updated_at: new Date().toISOString() }).eq('id', conversationId);\n"
        "      await refreshPlatform();\n"
        "    } else {\n"
        "      setConversations((prev) => prev.map((c) => c.id === conversationId ? { ...c, messages: [...(c.messages || []), msg], preview: msg.text, status: 'active' as const, unread: sender === 'customer' ? (c.unread || 0) + 1 : 0 } : c));\n"
        "    }\n"
        "  };"
    )
    new_send = (
        "  const sendChatMessage = async (conversationId: string, text: string, sender: 'agent' | 'customer') => {\n"
        "    // HOLD_PRESERVE_V2 — never clear on_hold just because someone sent a message.\n"
        "    const current = conversations.find((c) => c.id === conversationId);\n"
        "    const curStatus = (current?.status || '').toLowerCase();\n"
        "    const held = curStatus === 'on_hold' || curStatus === 'on-hold' || curStatus === 'hold';\n"
        "    if (held && sender === 'customer') {\n"
        "      return;\n"
        "    }\n"
        "    let nextStatus: ChatConversation['status'] = (current?.status as ChatConversation['status']) || 'active';\n"
        "    if (held) {\n"
        "      nextStatus = 'on_hold';\n"
        "    } else if (curStatus === 'waiting' || !curStatus) {\n"
        "      nextStatus = 'active';\n"
        "    } else if (curStatus === 'ended' || curStatus === 'archived' || curStatus === 'closed') {\n"
        "      nextStatus = 'active';\n"
        "    } else {\n"
        "      nextStatus = (current?.status as ChatConversation['status']) || 'active';\n"
        "    }\n"
        "    const msg: ChatMessage = { id: `m-${Date.now()}`, text, sender, created_at: new Date().toISOString() };\n"
        "    if (supabase) {\n"
        "      await supabase.from('chat_messages').insert({ conversation_id: conversationId, text, sender });\n"
        "      await supabase\n"
        "        .from('chat_conversations')\n"
        "        .update({\n"
        "          preview: msg.text.slice(0, 120),\n"
        "          status: nextStatus,\n"
        "          unread: sender === 'customer' ? 1 : 0,\n"
        "          updated_at: new Date().toISOString(),\n"
        "        })\n"
        "        .eq('id', conversationId);\n"
        "      await refreshPlatform();\n"
        "    } else {\n"
        "      setConversations((prev) =>\n"
        "        prev.map((c) =>\n"
        "          c.id === conversationId\n"
        "            ? {\n"
        "                ...c,\n"
        "                messages: [...(c.messages || []), msg],\n"
        "                preview: msg.text,\n"
        "                status: nextStatus,\n"
        "                unread: sender === 'customer' ? (c.unread || 0) + 1 : 0,\n"
        "              }\n"
        "            : c,\n"
        "        ),\n"
        "      );\n"
        "    }\n"
        "  };"
    )
    if 'HOLD_PRESERVE_V2' in s and 'const held =' in s:
        print('PlatformContext send already V2')
    elif old_send in s:
        s = s.replace(old_send, new_send, 1)
        print('PlatformContext send V2 applied')
    else:
        print('WARN: sendChatMessage pattern not found')

    old_fb = (
        "      if (error && nextStatus === 'on_hold') {\n"
        "        const retry = await supabase.from('chat_conversations').update({ status: 'waiting', updated_at: new Date().toISOString() }).eq('id', id);\n"
        "        error = retry.error;\n"
        "        if (!error) setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, status: 'waiting' as ChatConversation['status'] } : c)));\n"
        "      }"
    )
    new_fb = (
        "      if (error && nextStatus === 'on_hold') {\n"
        "        const retry = await supabase\n"
        "          .from('chat_conversations')\n"
        "          .update({ status: 'on-hold', updated_at: new Date().toISOString() })\n"
        "          .eq('id', id);\n"
        "        if (!retry.error) {\n"
        "          error = null;\n"
        "          setConversations((prev) =>\n"
        "            prev.map((c) => (c.id === id ? { ...c, status: 'on_hold' as ChatConversation['status'] } : c)),\n"
        "          );\n"
        "        } else {\n"
        "          console.warn('on_hold persist failed; keeping local hold', retry.error?.message || error?.message);\n"
        "          error = null;\n"
        "        }\n"
        "      }"
    )
    if 'keeping local hold' in s:
        print('setChatStatus already fixed')
    elif old_fb in s:
        s = s.replace(old_fb, new_fb, 1)
        print('setChatStatus hold fallback fixed')
    else:
        print('WARN: hold fallback not found')

    if 'NEW_LIVECHAT_NOTIF_V1' not in s:
        needle = 'const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {'
        insert = (
            'const createChat = async (customer_name: string, customer_email?: string, meta?: CreateChatMeta) => {\n'
            '    const notifyNewChat = () => {\n'
            '      // NEW_LIVECHAT_NOTIF_V1\n'
            '      try {\n'
            "        const title = 'New live chat';\n"
            '        const body = `${customer_name || \'Customer\'} is waiting for an agent`;\n'
            '        if (supabase) {\n'
            "          void supabase.from('notifications').insert({ title, body, link: '#/chat', read: false });\n"
            '        }\n'
            '        setNotifications((prev) => [\n'
            '          { id: `n-chat-${Date.now()}`, title, body, link: \'#/chat\', read: false, created_at: new Date().toISOString() },\n'
            '          ...prev,\n'
            '        ]);\n'
            '      } catch { /* ignore */ }\n'
            '    };'
        )
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
            print('createChat notification added')
        else:
            print('WARN: createChat inject failed')

    p.write_text(s)


def patch_portal():
    pv = Path('src/components/PortalLiveChatView.tsx')
    if not pv.exists():
        print('skip PortalLiveChatView')
        return
    t = pv.read_text()
    if 'HOLD_PRESERVE_V2' in t:
        print('PortalLiveChatView already V2')
        return
    t2 = t
    t2 = t2.replace(
        "const isOnHold = (conversation?.status || '').toLowerCase() === 'on_hold';",
        "const _holdSt = (conversation?.status || '').toLowerCase();\n  const isOnHold = _holdSt === 'on_hold' || _holdSt === 'on-hold' || _holdSt === 'hold'; // HOLD_PRESERVE_V2",
        1,
    )
    t2 = t2.replace("if (!chatId || chatEnded) return;", "if (!chatId || chatEnded || isOnHold) return;", 1)
    t2 = t2.replace("if (!file || !chatId) return;", "if (!file || !chatId || chatEnded || isOnHold) return;", 1)
    if t2 != t:
        pv.write_text(t2)
        print('PortalLiveChatView V2 applied')
    else:
        print('WARN: PortalLiveChatView unchanged')


def patch_shell():
    sc = Path('src/SystemAppCore.tsx')
    if not sc.exists():
        print('skip SystemAppCore')
        return
    t = sc.read_text()
    if 'waitingChatCount' in t:
        print('SystemAppCore badge already')
        return
    a = (
        "  const {\n"
        "    notifications,\n"
        "    unreadCount,\n"
        "    markNotificationRead,\n"
        "    markAllNotificationsRead,\n"
        "    deleteNotification,\n"
        "    deleteAllNotifications,\n"
        "  } = usePlatform();"
    )
    b = (
        "  const {\n"
        "    notifications,\n"
        "    unreadCount,\n"
        "    conversations,\n"
        "    markNotificationRead,\n"
        "    markAllNotificationsRead,\n"
        "    deleteNotification,\n"
        "    deleteAllNotifications,\n"
        "  } = usePlatform();\n"
        "  const waitingChatCount = (conversations || []).filter((c) => {\n"
        "    const st = (c.status || '').toLowerCase();\n"
        "    return st === 'waiting' || st === 'on_hold' || st === 'on-hold' || (c.unread || 0) > 0;\n"
        "  }).length;"
    )
    if a not in t:
        print('WARN: usePlatform destructure not found')
        return
    t = t.replace(a, b, 1)
    a2 = "        isAdmin={!!isAdmin}\n      />"
    b2 = "        isAdmin={!!isAdmin}\n        chatBadge={waitingChatCount || undefined}\n      />"
    if a2 in t:
        t = t.replace(a2, b2, 1)
        print('SystemAppCore chatBadge wired')
    else:
        print('WARN: Sidebar props not found')
    sc.write_text(t)


patch_platform()
patch_portal()
patch_shell()
print('DONE')
