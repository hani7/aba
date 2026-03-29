import requests
import re
from pathlib import Path

content = Path('vols/views.py').read_text(encoding='utf-8')
urls = re.findall(r'https://images.unsplash.com/photo-[a-zA-Z0-9-]+[^\"\']+', content)
for u in urls:
    try:
        r = requests.head(u, timeout=5)
        if r.status_code != 200:
            print(f'BROKEN: {r.status_code} {u}')
    except Exception as e:
        pass
