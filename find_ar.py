import os
import re

out = open('output.txt', 'w', encoding='utf-8')
for root, _, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for i, line in enumerate(content.split('\n')):
                    if re.search(r'[\u0600-\u06FF]', line) and '{% trans' not in line:
                        out.write(f'{path}:{i+1}: {line.strip()}\n')
out.close()
