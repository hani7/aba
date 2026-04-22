import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read templates
files = [
    'templates/vols/results.html',
    'templates/vols/includes/search_form.html',
    'templates/vols/includes/search_scripts.html',
    'templates/base.html',
    'templates/vols/home.html',
    'templates/vols/passenger_details.html',
]

all_trans = set()
for fpath in files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        found = re.findall(r"""\{%\s*trans\s+["'](.+?)["']\s*%\}""", content)
        all_trans.update(found)
    except FileNotFoundError:
        pass

# Read PO files
with open('locale/en/LC_MESSAGES/django.po', 'r', encoding='utf-8') as f:
    po_en = f.read()

with open('locale/fr/LC_MESSAGES/django.po', 'r', encoding='utf-8') as f:
    po_fr = f.read()

missing_en = []
missing_fr = []
for s in sorted(all_trans):
    check = f'msgid "{s}"'
    if check not in po_en:
        missing_en.append(s)
    if check not in po_fr:
        missing_fr.append(s)

if missing_en:
    print(f"MISSING from EN PO ({len(missing_en)} strings):")
    for m in missing_en:
        print(f"  - {m}")
else:
    print("EN PO: All trans strings found!")

print()
if missing_fr:
    print(f"MISSING from FR PO ({len(missing_fr)} strings):")
    for m in missing_fr:
        print(f"  - {m}")
else:
    print("FR PO: All trans strings found!")
