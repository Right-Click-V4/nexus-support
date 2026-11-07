"""Help filter + chat images + light contrast (umbrella)."""
import runpy
from pathlib import Path
for name in ('patch_help_filter.py', 'patch_chat_images.py', 'patch_light_contrast.py'):
    p = Path('scripts') / name
    if p.exists():
        print('running', name)
        runpy.run_path(str(p))
    else:
        print('missing', name)
