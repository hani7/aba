import os
import sys

from pathlib import Path

# Add the project base directory to the sys.path
cwd = Path(__file__).resolve().parent
sys.path.insert(0, str(cwd))

# Set the settings module (replace 'abo.settings' if needed)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')

# Get the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
