# -*- coding: utf-8 -*-
import re
import sys

with open("en/index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Filter out intentional switcher
text = text.replace('title="中文">CN', '').replace('>中文<', '')
matches = re.findall(r'[\u4e00-\u9fa5]+', text)
print(f"Total remaining fragments in en/index.html: {len(set(matches))}")
for m in sorted(set(matches), key=len, reverse=True):
    print(repr(m))
