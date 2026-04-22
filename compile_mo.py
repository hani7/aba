"""
Compiles .po files to .mo binary format (GNU MO spec).
Correctly includes the header entry (msgid "") so Python/Django
reads the file as UTF-8 instead of falling back to ASCII.
"""
import struct
import re


def compile_po_to_mo(po_path, mo_path):
    messages = {}

    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalise line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Match msgid / msgstr blocks (multi-line strings supported)
    pattern = re.compile(
        r'msgid\s+((?:"[^"]*"\s*\n?)+)\s*msgstr\s+((?:"[^"]*"\s*\n?)+)',
        re.MULTILINE,
    )

    def unescape(raw):
        """Join multi-line PO string and unescape escape sequences."""
        parts = re.findall(r'"((?:[^"\\]|\\.)*)"', raw)
        joined = ''.join(parts)
        joined = joined.replace('\\n', '\n')
        joined = joined.replace('\\t', '\t')
        joined = joined.replace('\\"', '"')
        joined = joined.replace('\\\\', '\\')
        return joined

    for m in pattern.finditer(content):
        msgid  = unescape(m.group(1))
        msgstr = unescape(m.group(2))
        # Include ALL entries — even the empty-string header (msgid "")
        if msgstr:          # only skip entries with no translation
            messages[msgid] = msgstr

    # Ensure the header entry exists so Python reads MO as UTF-8
    if '' not in messages:
        messages[''] = (
            'Content-Type: text/plain; charset=utf-8\n'
            'Content-Transfer-Encoding: 8bit\n'
        )

    # Build MO binary -------------------------------------------------------
    # Keys must be sorted; empty string sorts first (ord value 0 < any char)
    keys   = sorted(messages.keys())
    values = [messages[k] for k in keys]

    koffsets, voffsets = [], []
    kdata, vdata = b'', b''

    for k in keys:
        kb = k.encode('utf-8')
        koffsets.append((len(kb), len(kdata)))
        kdata += kb + b'\x00'

    for v in values:
        vb = v.encode('utf-8')
        voffsets.append((len(vb), len(vdata)))
        vdata += vb + b'\x00'

    n = len(keys)
    # Offsets inside the file
    orig_table_offset  = 28              # right after the 7-int header
    trans_table_offset = orig_table_offset  + n * 8
    key_data_start     = trans_table_offset + n * 8
    val_data_start     = key_data_start + len(kdata)

    # magic | revision | n | orig_offset | trans_offset | hash_size | hash_offset
    header = struct.pack('<IIIIIII',
                         0x950412de, 0, n,
                         orig_table_offset, trans_table_offset,
                         0, 0)

    orig_table  = b''.join(
        struct.pack('<II', length, key_data_start + offset)
        for length, offset in koffsets
    )
    trans_table = b''.join(
        struct.pack('<II', length, val_data_start + offset)
        for length, offset in voffsets
    )

    with open(mo_path, 'wb') as f:
        f.write(header + orig_table + trans_table + kdata + vdata)

    print(f'Compiled  {po_path}')
    print(f'       -> {mo_path}  ({n} entries, UTF-8 header included)')


if __name__ == '__main__':
    compile_po_to_mo(
        'locale/en/LC_MESSAGES/django.po',
        'locale/en/LC_MESSAGES/django.mo',
    )
    compile_po_to_mo(
        'locale/fr/LC_MESSAGES/django.po',
        'locale/fr/LC_MESSAGES/django.mo',
    )
    print('Done!')
