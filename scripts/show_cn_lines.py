# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("en/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

cn_lines_count = 0
for i, line in enumerate(lines):
    clean_line = line.replace('title="中文">CN', '').replace('>中文<', '')
    if any('\u4e00' <= ch <= '\u9fa5' for ch in clean_line):
        cn_lines_count += 1
        print(f"Line {i+1}: {line.strip()[:120]}")

print(f"Total lines with remaining Chinese: {cn_lines_count}")
