import os

base_dir = r"c:\Users\PC\Desktop\test\templates\vols"
home_path = os.path.join(base_dir, "home.html")
results_path = os.path.join(base_dir, "results.html")
includes_dir = os.path.join(base_dir, "includes")

os.makedirs(includes_dir, exist_ok=True)

with open(home_path, "r", encoding="utf-8") as f:
    home_lines = f.readlines()

form_start = -1
form_end = -1
script_start = -1
script_end = -1

for i, line in enumerate(home_lines):
    if '<form action="{% url \'vols:search_results\' %}"' in line:
        form_start = i
    if '</form>' in line and form_start != -1 and form_end == -1:
        form_end = i
    if '// Setup dates' in line:
        script_start = i
    if 'document.getElementById("searchForm").addEventListener("submit"' in line:
        script_end = i + 5 # include the remaining lines up to </script>

if form_start == -1 or form_end == -1 or script_start == -1 or script_end == -1:
    print(f"Error finding indices: form {form_start}-{form_end}, script {script_start}-{script_end}")
    import sys
    sys.exit(1)

# Extract form
form_content = "".join(home_lines[form_start:form_end+1])
with open(os.path.join(includes_dir, "search_form.html"), "w", encoding="utf-8") as f:
    f.write(form_content)

# Extract scripts
script_content = "".join(home_lines[script_start:script_end+1])
with open(os.path.join(includes_dir, "search_scripts.html"), "w", encoding="utf-8") as f:
    f.write("<script>\n" + script_content)

# Re-write home.html
new_home = home_lines[:form_start] + ["    {% include 'vols/includes/search_form.html' %}\n"] + home_lines[form_end+1:script_start-1] + ["{% include 'vols/includes/search_scripts.html' %}\n"] + home_lines[script_end+2:]

with open(home_path, "w", encoding="utf-8") as f:
    f.writelines(new_home)

# Now inject into results.html
with open(results_path, "r", encoding="utf-8") as f:
    results_html = f.read()

# Replace the edit button
old_button = '<a href="{% url \'vols:home\' %}" class="btn btn-ghost btn-sm">← تعديل</a>'
new_button = '<button type="button" id="toggleSearchBtn" class="btn btn-ghost btn-sm">← تعديل</button>'
results_html = results_html.replace(old_button, new_button)

# Inject hidden form right after results-header
header_end = '</div>\n\n    <div style="display: flex;'
form_inject = """</div>\n\n    <div id="inlineSearchForm" style="display: none; margin-bottom: 24px;">\n        {% include 'vols/includes/search_form.html' %}\n    </div>\n\n    <div style="display: flex;"""
if header_end in results_html:
    results_html = results_html.replace(header_end, form_inject)
else:
    print("Could not find header_end in results.html")

# Inject scripts and toggle listener
script_inject = """{% block extra_scripts %}\n{% include 'vols/includes/search_scripts.html' %}\n<script>\n  document.getElementById('toggleSearchBtn').addEventListener('click', () => {\n      const f = document.getElementById('inlineSearchForm');\n      f.style.display = f.style.display === 'none' ? 'block' : 'none';\n  });"""
results_html = results_html.replace('{% block extra_scripts %}\n<script>', script_inject)

with open(results_path, "w", encoding="utf-8") as f:
    f.write(results_html)

print("Refactor complete.")
