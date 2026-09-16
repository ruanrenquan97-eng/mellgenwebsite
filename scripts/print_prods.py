import re

with open('product_hzpyl.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'products/' in line:
        print(f"Line {i+1}: {line.strip()[:120]}")
