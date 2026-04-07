import os
import sys
from pathlib import Path

# Add project root to sys.path
cwd = Path(__file__).resolve().parent
sys.path.insert(0, str(cwd))

# Point to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')

# Get Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
