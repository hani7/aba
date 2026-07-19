import os
import sys
import site
from pathlib import Path

# Add project root to sys.path
cwd = Path(__file__).resolve().parent
sys.path.insert(0, str(cwd))

# ── cPanel virtualenv: auto-detected from VIRTUAL_ENV env var or hardcoded path ──
# cPanel creates its own venv outside the project folder
_venv_root = os.environ.get('VIRTUAL_ENV', '')
if not _venv_root:
    # Hardcoded fallback: path visible in cPanel Python App settings
    _venv_root = '/home/adanof06/virtualenv/aba.adan-office-services.com/app/3.12'

_venv_site = os.path.join(_venv_root, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
if os.path.isdir(_venv_site):
    site.addsitedir(_venv_site)

# Also ensure the venv bin is first in PATH so correct executables are used
_venv_bin = os.path.join(_venv_root, 'bin')
os.environ['PATH'] = _venv_bin + os.pathsep + os.environ.get('PATH', '')

# Point to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')

# Get Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
