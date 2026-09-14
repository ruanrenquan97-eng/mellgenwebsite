import glob
import re

count = 0
for fp in glob.glob('en/**/*.html', recursive=True):
    if 'backup_' in fp:
        continue
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        c = f.read()
    orig = c
    c = re.sub(r'(resetcommon\.css|reset\.css|index\.css|mobile\.css)\?v=[^\"]+', r'\1?v=20260914v7', c)
    if c != orig:
        count += 1
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)

print(f"Updated cache query strings to v=20260914v7 in {count} files.")
