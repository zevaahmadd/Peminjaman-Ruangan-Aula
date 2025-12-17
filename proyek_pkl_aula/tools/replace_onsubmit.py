#!/usr/bin/env python3
# tools/replace_onsubmit.py
# Usage: python tools/replace_onsubmit.py
# Membuat backup file.html.bak sebelum modifikasi

import re
import sys
from pathlib import Path

ROOT = Path('.')

PATTERN = re.compile(
    r'(<form\b[^>]*?)\s+onsubmit\s*=\s*([\'"])\s*return\s+confirm\(\s*([\'"])(.*?)\3\s*\)\s*;?\s*\2([^>]*>)',
    re.IGNORECASE | re.DOTALL
)

html_files = list(ROOT.rglob('*.html'))

if not html_files:
    print("No .html files found.")
    sys.exit(0)

for f in html_files:
    text = f.read_text(encoding='utf-8')
    new_text = text
    matches = list(PATTERN.finditer(text))
    if not matches:
        continue

    for m in reversed(matches):
        before_attrs = m.group(1)
        message = m.group(4).strip()
        after = m.group(5)

        # cek class
        class_match = re.search(r'\bclass\s*=\s*([\'"])(.*?)\1',
                                before_attrs,
                                flags=re.IGNORECASE | re.DOTALL)

        if class_match:
            q = class_match.group(1)
            classes = class_match.group(2).strip()

            if 'needs-confirm' not in classes.split():
                new_classes = classes + ' needs-confirm'
                before_attrs = (
                    before_attrs[:class_match.start()] +
                    f'class={q}{new_classes}{q}' +
                    before_attrs[class_match.end():]
                )
        else:
            before_attrs = before_attrs + ' class="needs-confirm"'

        if re.search(r'\bdata-confirm-message\s*=', before_attrs, flags=re.IGNORECASE):
            replacement = before_attrs + after
        else:
            safe_msg = message.replace('"', '&quot;')
            replacement = before_attrs + f' data-confirm-message="{safe_msg}"' + after

        new_text = new_text[:m.start()] + replacement + new_text[m.end():]

    if new_text != text:
        bak = f.with_suffix(f.suffix + '.bak')
        bak.write_text(text, encoding='utf-8')
        f.write_text(new_text, encoding='utf-8')
        print(f"[UPDATED] {f}  (backup: {bak.name})")

print("\nSelesai! Semua onsubmit=\"return confirm(...)\" berhasil diganti.")
print("Silakan cek hasil dengan 'git diff' atau buka file-file HTML Anda.")
