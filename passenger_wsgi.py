import os
import sys
import glob
import site
from pathlib import Path

# Add project root to sys.path
cwd = Path(__file__).resolve().parent
sys.path.insert(0, str(cwd))

# ── Add virtual environment site-packages ────────────────────────────────────
# site.addsitedir() is more reliable than sys.path.insert — it processes .pth files too
_found_venv = False
for _pattern in [
    str(cwd / 'env' / 'lib' / 'python*' / 'site-packages'),   # Linux
    str(cwd / 'env' / 'Lib' / 'site-packages'),                # Windows
    str(cwd / 'venv' / 'lib' / 'python*' / 'site-packages'),  # Linux alt
    str(cwd / 'venv' / 'Lib' / 'site-packages'),               # Windows alt
]:
    _matches = glob.glob(_pattern)
    if _matches:
        site.addsitedir(_matches[0])
        _found_venv = True
        break

# ── Write debug info to help diagnose production issues ──────────────────────
try:
    _debug_path = cwd / 'tmp' / 'wsgi_debug.txt'
    _debug_path.parent.mkdir(exist_ok=True)
    with open(_debug_path, 'w') as _f:
        _f.write(f"Python: {sys.version}\n")
        _f.write(f"cwd: {cwd}\n")
        _f.write(f"venv found: {_found_venv}\n")
        _f.write("sys.path:\n")
        for _p in sys.path:
            _f.write(f"  {_p}\n")
except Exception:
    pass

# Point to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')

# Get Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
