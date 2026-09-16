import re

with open('article_xwzx.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'lzdt' in l:
        print(f"Around line {i+1}:")
        print(''.join(lines[max(0, i-15):min(len(lines), i+15)]))
