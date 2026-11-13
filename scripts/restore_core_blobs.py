#!/usr/bin/env python3
"""Restore critical source files if they are stubs/placeholders."""
import base64, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLOBS = ROOT / 'blobs'

def is_stub(path: Path, min_bytes: int, must_contain: str) -> bool:
    if not path.exists():
        return True
    try:
        text = path.read_text(errors='ignore')
    except Exception:
        return True
    if len(text) < min_bytes:
        return True
    if 'PLACEHOLDER' in text or 'SEE_LOCAL_FILE' in text:
        return True
    if must_contain and must_contain not in text:
        return True
    return False

def restore(blob_name: str, target: str, min_bytes: int, must_contain: str) -> None:
    blob = BLOBS / blob_name
    path = Path(target)
    if not is_stub(path, min_bytes, must_contain):
        print(f'OK {target} ({path.stat().st_size} bytes)')
        return
    if not blob.exists():
        print(f'MISS blob {blob_name} for {target}')
        return
    try:
        data = zlib.decompress(base64.b64decode(blob.read_text().strip()))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f'RESTORED {target} ({len(data)} bytes)')
    except Exception as e:
        print(f'FAIL {target}: {e}')

restore('pc.b64', 'src/context/PlatformContext.tsx', 10000, 'export function usePlatform')
restore('tc.b64', 'src/context/TicketContext.tsx', 15000, 'export function useTickets')
restore('plv.b64', 'src/components/PortalLiveChatView.tsx', 5000, 'export default')
restore('lcp.b64', 'src/components/LiveChatPage.tsx', 5000, 'export default')
print('core blob restore done')
