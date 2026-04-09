import sys, os
import polib

sys.stdout.reconfigure(encoding='utf-8')

PO = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
MO = PO.replace('.po', '.mo')

po = polib.pofile(PO, encoding='utf-8')

# Ensure we have a standalone entry for "نشاطاتنا"
msgid = 'نشاطاتنا'
msgstr = 'Activities'

# Look for an entry with EXACTLY this msgid
entry = None
for e in po:
    if e.msgid == msgid:
        entry = e
        break

if entry:
    entry.msgstr = msgstr
    print(f"Updated existing entry for '{msgid}'")
else:
    new_entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
    po.append(new_entry)
    print(f"Added new standalone entry for '{msgid}'")

po.save(PO)
po.save_as_mofile(MO)
print(f"Total entries now: {len(po)}")
