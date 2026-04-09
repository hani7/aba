import os

def normalize_po_encoding(file_path):
    print(f"Normalizing {file_path}")
    try:
        # Try reading as UTF-16 (le or be) if UTF-8 fails
        encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1']
        content = None
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                print(f"  Successfully read with {enc}")
                break
            except:
                continue
        
        if content:
            # Remove null bytes if any (often happen with mix-matched UTF-16 encoding)
            content = content.replace('\x00', '')
            
            # Save as pure UTF-8 (no BOM)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("  Successfully normalized to UTF-8")
        else:
            print("  Failed to read file with any tested encoding")
            
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    po_path = os.path.join(os.getcwd(), 'locale', 'en', 'LC_MESSAGES', 'django.po')
    if os.path.exists(po_path):
        normalize_po_encoding(po_path)
    else:
        print(f"File not found: {po_path}")
