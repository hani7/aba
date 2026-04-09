import polib
import sys
sys.stdout.reconfigure(encoding='utf-8')

po = polib.pofile('locale/en/LC_MESSAGES/django.po', encoding='utf-8')
print(f"Total entries: {len(po)}\n")

# Show first 30 entries
for i, entry in enumerate(po[:30]):
    print(f"[{i+1}] msgid: '{entry.msgid[:50]}' -> msgstr: '{entry.msgstr[:50]}'")

print("\n--- Searching by substring ---")
# Try substring match
for entry in po:
    if 'جمع' in entry.msgid or 'خصوصية' in entry.msgid:
        print(f"FOUND: {entry.msgid[:60]} -> {entry.msgstr[:60]}")
        break
