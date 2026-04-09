"""
fix_double_encoded_po.py
Fixes the double-encoding: Latin-1 misread as UTF-8 -> correct Arabic text.
"""
import sys, os, re

sys.stdout.reconfigure(encoding='utf-8')

PO_PATH = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
MO_PATH = PO_PATH.replace('.po', '.mo')

# Read raw bytes
with open(PO_PATH, 'rb') as f:
    raw_bytes = f.read()

print(f"File size: {len(raw_bytes)} bytes")

# Decode with latin-1 (which recovers the true UTF-8 bytes)
try:
    text_latin1 = raw_bytes.decode('latin-1')
    # Re-encode to latin-1 bytes, then decode as utf-8 to get correct Arabic
    fixed_bytes = text_latin1.encode('latin-1')
    fixed_text = fixed_bytes.decode('utf-8')
    print("Double-encoding fix successful!")
    
    # Quick sanity check
    if 'جميع' in fixed_text or 'سياسة' in fixed_text:
        print("Arabic text found correctly in fixed content.")
    else:
        print("WARNING: Arabic text not found after fix - check manually.")
    
    # Write the fixed file
    with open(PO_PATH, 'w', encoding='utf-8') as f:
        f.write(fixed_text)
    print(f"Saved fixed PO to {PO_PATH}")
    
    # Recompile
    import polib
    po = polib.pofile(PO_PATH, encoding='utf-8')
    print(f"Loaded {len(po)} entries")
    
    # Verify key translations
    keys = ['سياسة الخصوصية', 'الأسئلة الشائعة', 'شروط الخدمة', 'نشاطاتنا', 'اكتشف', 'الدعم', 'قانوني']
    for key in keys:
        e = po.find(key)
        if e and e.msgstr:
            print(f"  OK: {key} -> {e.msgstr[:40]}")
        else:
            print(f"  MISSING: {key}")
    
    po.save_as_mofile(MO_PATH)
    print(f"\nRecompiled {MO_PATH} successfully!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
