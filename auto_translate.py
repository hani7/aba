import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = ""
    lines = content.split('\n')
    extracted_strings = set()
    
    # regex to find Arabic words. We want to avoid matching inside tags like <...>, so we can roughly split by < and >
    for i, line in enumerate(lines):
        if '{% trans' in line or '{% blocktrans' in line:
            new_content += line + '\n'
            continue
        
        # We need to find Arabic texts ignoring html tags
        original_line = line
        
        # A simple hack: findall chunks of Arabic text and wrap them. 
        # Excludes 1-character words.
        # It handles cases like ` placeholder="الاسم" ` or ` >تفاصيل الرحلة< ` or `الربح الصافي`
        
        matches = re.finditer(r'([\u0600-\u06FF\s،!؟:()/-]+[\u0600-\u06FF])', line)
        offset = 0
        transformed_line = ""
        last_end = 0
        
        for m in matches:
            text = m.group(1).strip()
            if len(text.replace(' ', '')) <= 1:
                continue
                
            start, end = m.span(1)
            
            # check if text is already inside a {% %} tag (heuristic)
            left_part = original_line[:start]
            if '{%' in left_part and '%}' not in left_part[left_part.rfind('{%'):]:
                continue
                
            # check if inside a script tag (e.g., alert("..."))
            # For scripts, we shouldn't use django template tags unless it's a django template.
            # actually django tags work in scripts if they are in .html templates
            
            # find original string boundary with its spaces preserved
            original_match = line[start:end]
            
            # check if there are quotes immediately surrounding
            in_quotes = False
            q_char = '"'
            if start > 0 and line[start-1] in ['"', "'"]:
                in_quotes = True
                q_char = line[start-1]
                
            # build the trans tag. If in quotes, we use single quotes inside trans if double quote outside, and vice versa.
            inner_quote = "'" if q_char == '"' else '"'
            trans_tag = f"{{% trans {inner_quote}{text}{inner_quote} %}}"
            
            # if we are replacing text inside an HTML node (no quotes), we can just replace text with {% trans "text" %}
            if not in_quotes:
                trans_tag = f"{{% trans \"{text}\" %}}"
                
            transformed_line += original_line[last_end:start] + original_match.replace(text, trans_tag)
            last_end = end
            extracted_strings.add(text)
            
        transformed_line += original_line[last_end:]
        new_content += transformed_line + '\n'
        
    # strip trailing newline
    if new_content.endswith('\n'):
        new_content = new_content[:-1]
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return extracted_strings

all_extracted = set()

for root, _, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            extracted = process_file(filepath)
            all_extracted.update(extracted)

with open('new_translations.txt', 'w', encoding='utf-8') as f:
    for text in sorted(all_extracted):
        f.write(f'{text}\n')
