import os

for root, _, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if '{% trans' in content or '{% blocktrans' in content:
                # Check for load i18n
                if '{% load i18n' not in content and '{% load static i18n' not in content and '{% load i18n static' not in content and '{% load static' not in content:
                    # just prepend load i18n immediately if it doesn't extend
                    if '{% extends' in content:
                        # find where extends ends and insert afterwards
                        parts = content.split('%}')
                        for i, p in enumerate(parts):
                            if '{% extends' in p:
                                parts[i] = p + '%}\n{% load i18n %}'
                                break
                        new_content = '%}'.join(parts)
                    else:
                        new_content = '{% load i18n %}\n' + content
                        
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print('Fixed', filepath)
                elif '{% load static' in content and '{% load static i18n' not in content and '{% load i18n' not in content:
                     new_content = content.replace('{% load static %}', '{% load static i18n %}')
                     with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                     print('Fixed', filepath)
