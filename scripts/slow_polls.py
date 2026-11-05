#!/usr/bin/env python3
"""CI safety net: cut PlatformContext egress (polls + select *)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "src" / "context" / "PlatformContext.tsx"
if not p.exists():
    raise SystemExit(0)

t = p.read_text(encoding="utf-8")
orig = t

# --- intervals ---
t = t.replace(
    "window.setInterval(() => { void refreshPlatform(); }, 3000)",
    "window.setInterval(() => { void refreshPlatform(); }, 180000)",
)
t = t.replace(
    "window.setInterval(() => { void refreshPlatform(); }, 3000);",
    "window.setInterval(() => { void refreshPlatform(); }, 180000);",
)
t = re.sub(
    r"void refreshAnnouncementsLight\(\);\s*\}, 2000\);",
    "void refreshAnnouncementsLight();\n    }, 90000);",
    t,
)
t = t.replace("const tick = window.setInterval(pull, 500);", "const tick = window.setInterval(pull, 5000);")
t = t.replace("}, 700);", "}, 8000);")

# --- narrow select('*') on heavy tables ---
replacements = [
    (
        "supabase.from('knowledge_articles').select('*').order('created_at', { ascending: false })",
        "supabase.from('knowledge_articles').select('id,title,category,body,published,created_at').order('created_at', { ascending: false }).limit(80)",
    ),
    (
        "supabase.from('chat_conversations').select('*').order('updated_at', { ascending: false })",
        "supabase.from('chat_conversations').select('id,customer_name,customer_email,status,preview,unread,updated_at,created_at,assignee_id,archived_at').order('updated_at', { ascending: false }).limit(60)",
    ),
    (
        "supabase.from('chat_messages').select('*').order('created_at', { ascending: true })",
        "supabase.from('chat_messages').select('id,conversation_id,sender,text,body,created_at').order('created_at', { ascending: false }).limit(200)",
    ),
    (
        "supabase.from('automations').select('*')",
        "supabase.from('automations').select('id,name,enabled,active,trigger,condition_field,condition_op,condition_value,action,action_value,actions,description').limit(80)",
    ),
    (
        "supabase.from('canned_responses').select('*')",
        "supabase.from('canned_responses').select('id,title,body,shortcut,category').limit(80)",
    ),
    (
        "supabase.from('survey_responses').select('*').order('created_at', { ascending: false })",
        "supabase.from('survey_responses').select('id,ticket_id,score,comment,created_at').order('created_at', { ascending: false }).limit(50)",
    ),
    (
        "supabase.from('quality_reviews').select('*').order('created_at', { ascending: false })",
        "supabase.from('quality_reviews').select('id,ticket_id,score,notes,created_at').order('created_at', { ascending: false }).limit(50)",
    ),
    (
        "supabase.from('announcements').select('*').order('created_at', { ascending: false })",
        "supabase.from('announcements').select('id,title,body,active,created_at').order('created_at', { ascending: false }).limit(40)",
    ),
    (
        "supabase.from('forms').select('*')",
        "supabase.from('forms').select('id,name,description,fields,active').limit(40)",
    ),
    (
        "supabase.from('releases').select('*').order('released_at', { ascending: false })",
        "supabase.from('releases').select('id,title,body,released_at').order('released_at', { ascending: false }).limit(30)",
    ),
]
for a, b in replacements:
    if a in t:
        t = t.replace(a, b)

if t != orig:
    p.write_text(t, encoding="utf-8")
    print("slow_polls: patched PlatformContext")
else:
    print("slow_polls: already optimized or patterns missing")
