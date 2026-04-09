import os
import polib

def compile_po_to_mo(locale_dir):
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                mo_path = po_path.replace('.po', '.mo')
                print(f"Compiling {po_path} -> {mo_path}")
                try:
                    po = polib.pofile(po_path)
                    po.save_as_mofile(mo_path)
                    print("  Success!")
                except Exception as e:
                    print(f"  Error: {e}")

if __name__ == "__main__":
    locale_path = os.path.join(os.getcwd(), 'locale')
    if os.path.exists(locale_path):
        compile_po_to_mo(locale_path)
    else:
        print(f"Locale directory not found at {locale_path}")
