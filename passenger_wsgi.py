import os
import sys
from pathlib import Path

# Add project root to sys.path
cwd = Path(__file__).resolve().parent
sys.path.insert(0, str(cwd))

# ── Activate virtual environment so all pip packages are available ──────────
# Tries common venv locations relative to project root
_venv_candidates = [
    cwd / 'env' / 'lib' / 'site-packages',          # Linux/macOS venv
    cwd / 'env' / 'Lib' / 'site-packages',          # Windows venv
    cwd / 'venv' / 'lib' / 'site-packages',
    cwd / 'venv' / 'Lib' / 'site-packages',
]
for _venv_site in _venv_candidates:
    if _venv_site.exists():
        sys.path.insert(0, str(_venv_site))
        break

# Point to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')

# Get Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
