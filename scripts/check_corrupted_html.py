import os
import re

html_files_with_multiple_endtags = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', '.gemini', 'node_modules', '__pycache__'] and not d.startswith('backup')]
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
            matches = list(re.finditer(r'</html>', content, re.IGNORECASE))
            if len(matches) > 1:
                html_files_with_multiple_endtags.append((p, len(matches)))
            elif len(matches) == 1:
                tail = content[matches[0].end():].strip()
                if len(tail) > 10:
                    html_files_with_multiple_endtags.append((p, f"trailing data: {len(tail)} bytes"))

print(f"Files with corrupted HTML / multiple </html>: {len(html_files_with_multiple_endtags)}")
for f, info in html_files_with_multiple_endtags:
    print(f"  {f}: {info}")
