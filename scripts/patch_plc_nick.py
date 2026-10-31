#!/usr/bin/env python3
"""Use Name (Nickname) in customer Live Chat labels."""
from pathlib import Path
import re

p = Path("src/components/PortalLiveChat.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
if "nickname-chat-v1" in t:
    print("plc already")
    raise SystemExit(0)

new = """  const legalChatName =
    (user?.user_metadata?.full_name as string | undefined)?.trim() ||
    (user?.user_metadata?.name as string | undefined)?.trim() ||
    user?.email?.split('@')[0] ||
    '';
  const nickChat = (user?.user_metadata?.nickname as string | undefined)?.trim() || '';
  const accountName = nickChat && legalChatName ? `${legalChatName} (${nickChat})` : legalChatName;"""

t2, n = re.subn(
    r"const accountName =\s*\n?\s*\(user\?\.user_metadata\?\.full_name as string \| undefined\)\?\.trim\(\) \|\|\s*\n?\s*\(user\?\.user_metadata\?\.name as string \| undefined\)\?\.trim\(\) \|\|\s*\n?\s*user\?\.email\?\.split\('@'\)\[0\] \|\|\s*\n?\s*'';",
    new,
    t,
    count=1,
)
if n != 1:
    t2, n = re.subn(
        r"const accountName =[\s\S]{20,220}?user\?\.email\?\.split\('@'\)\[0\][\s\S]{0,40}?'';",
        new,
        t,
        count=1,
    )
print("accountName", n)
t = t2 if n else t

if "nickname-chat-v1" not in t:
    t = "/* nickname-chat-v1 */\n" + t
p.write_text(t)
print("plc braces", t.count("{") - t.count("}"))
