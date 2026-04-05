with open('build_translations.py', 'r', encoding='utf-8') as f:
    c = f.read()
if '"جميع المطارات"' not in c:
    c = c.replace('master_translations = {', 'master_translations = {\n    "جميع المطارات": ("All airports", "Tous les aéroports"),')
    with open('build_translations.py', 'w', encoding='utf-8') as f:
        f.write(c)
print('Done')
