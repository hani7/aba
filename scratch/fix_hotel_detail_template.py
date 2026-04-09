import os

file_path = r'c:\Users\PC\Desktop\New folder\test\templates\vols\hotel_detail.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The unique part before and after the problematic line
before = '<p style="color:#555; line-height:1.8; font-size:1.05rem;">'
after = '</p>'

# Problematic code snippet
old_code = '{{ hotel.description|default:"{% trans \'يقع هذا الفندق المميز في موقع استراتيجي ويوفر كافة سبل الراحة والخدمات المتميزة لضمان إقامة لا تُنسى\' %}. {% trans \\"استمتع بأرقى المرافق والخدمة التي تلبي أعلى المعايير العالمية\\" %}.\\" }}'

new_code = """
        {% if hotel.description %}
          {{ hotel.description }}
        {% else %}
          {% trans "يقع هذا الفندق المميز في موقع استراتيجي ويوفر كافة سبل الراحة والخدمات المتميزة لضمان إقامة لا تُنسى" %}. 
          {% trans "استمتع بأرقى المرافق والخدمة التي تلبي أعلى المعايير العالمية" %}.
        {% endif %}"""

# We look for the <p> tag and replace its content
# Since there might be many <p> tags, we look specifically for the one following 'عن الفندق'
marker = '{% trans "عن الفندق" %}</h3>'
if marker in content:
    parts = content.split(marker)
    target_part = parts[1]
    
    # Within target_part, find the first <p>...</p>
    p_start = target_part.find(before) + len(before)
    p_end = target_part.find(after, p_start)
    
    if p_start > -1 and p_end > -1:
        new_target_part = target_part[:p_start] + new_code + target_part[p_end:]
        new_content = parts[0] + marker + new_target_part
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully replaced the problematic code.")
    else:
        print("Could not find paragraph markers.")
else:
    print("Could not find marker 'عن الفندق'.")
