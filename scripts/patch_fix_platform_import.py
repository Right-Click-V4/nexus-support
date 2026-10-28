#!/usr/bin/env python3
"""Fix notifyCustomer import broken inside import type block."""
from pathlib import Path

p = Path("src/context/PlatformContext.tsx")
c = p.read_text()
if "fix-platform-import-v1" in c:
    print("already")
    raise SystemExit(0)

broken = """import type {
import { notifyCustomer } from '../lib/agentNotify';
  KnowledgeArticle,"""
fixed = """import { notifyCustomer } from '../lib/agentNotify';
import type {
  KnowledgeArticle,"""
if broken in c:
    c = c.replace(broken, fixed, 1)
    print("import fixed")
elif "import type {\nimport { notifyCustomer }" in c:
    c = c.replace(
        "import type {\nimport { notifyCustomer } from '../lib/agentNotify';\n",
        "import { notifyCustomer } from '../lib/agentNotify';\nimport type {\n",
        1,
    )
    print("import fixed alt")
else:
    print("pattern miss or already ok")

c = "/* fix-platform-import-v1 */\n" + c
p.write_text(c)
print("done")
