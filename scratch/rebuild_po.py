"""
rebuild_en_po.py
Reads the current django.po (mixed encoding), extracts all msgid/msgstr pairs,
then re-writes the file as clean UTF-8 with all known English translations.
"""

import polib
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

PO_PATH = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')

# Try to load with different encodings
for enc in ['utf-8', 'utf-16', 'latin-1']:
    try:
        with open(PO_PATH, 'r', encoding=enc) as f:
            raw = f.read()
        print(f"Read with: {enc}")
        break
    except Exception as e:
        print(f"Failed {enc}: {e}")

# Strip null bytes (UTF-16 artifact)
raw = raw.replace('\x00', '')

# Write back as UTF-8
TMP_PATH = PO_PATH + '.clean.po'
with open(TMP_PATH, 'w', encoding='utf-8') as f:
    f.write(raw)
print(f"Wrote clean copy to {TMP_PATH}")

# Load and verify
try:
    po = polib.pofile(TMP_PATH, encoding='utf-8')
    print(f"Loaded {len(po)} entries")
    
    # Check for key strings
    test_keys = ['سياسة الخصوصية', 'الأسئلة الشائعة', 'شروط الخدمة', 'نشاطاتنا', 'اكتشف']
    for key in test_keys:
        e = po.find(key)
        status = f"-> {e.msgstr[:40]}" if e and e.msgstr else "MISSING"
        print(f"  {key[:40]}: {status}")
    
    # Count missing
    missing = [e for e in po if not e.msgstr]
    print(f"\nMissing translations: {len(missing)}")
    
    # Replace the original
    import shutil
    shutil.copy(TMP_PATH, PO_PATH)
    print(f"\nReplaced {PO_PATH} with clean version")
    os.remove(TMP_PATH)
    
    # Recompile
    po2 = polib.pofile(PO_PATH, encoding='utf-8')
    po2.save_as_mofile(PO_PATH.replace('.po', '.mo'))
    print("Compiled .mo file successfully!")
    
except Exception as e:
    print(f"Error: {e}")
