import re

with open('templates/vols/admin_dashboard_react.html', 'r', encoding='utf-8') as f:
    t = f.read()

t = re.sub(r'\{%\s*trans\s*[\'\"”](.*?)[\'\"”]\s*%\}', r'\1', t)
# Also handle blocktrans? There are none inside React, but maybe.
# Let's fix the React code.

with open('templates/vols/admin_dashboard_react.html', 'w', encoding='utf-8') as f:
    f.write(t)

print("Fixed successfully!")
