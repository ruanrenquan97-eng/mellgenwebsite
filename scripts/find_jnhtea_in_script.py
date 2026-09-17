import os
import re
import sys

with open('scripts/generate_en_product_pages.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'jnhtea' in l:
        print(f"Line {i+1}: {l.strip()}")
