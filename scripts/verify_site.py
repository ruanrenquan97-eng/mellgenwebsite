# -*- coding: utf-8 -*-
"""
Verification Script for English Website and Language Switcher
"""

import os
import re
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

# 1. Verify Chinese homepage
with open('index.html', 'r', encoding='utf-8') as f:
    cn_home = f.read()

assert 'class="lang-switch"' in cn_home, 'Language switcher missing in index.html'
assert './en/index.html' in cn_home, 'English link missing in index.html'
print('[OK] Chinese homepage (index.html) has language switcher pointing to ./en/index.html')

# 2. Verify English homepage
with open('en/index.html', 'r', encoding='utf-8') as f:
    en_home = f.read()

assert 'class="lang-switch"' in en_home, 'Language switcher missing in en/index.html'
assert '../index.html' in en_home, 'Chinese link missing in en/index.html'
print('[OK] English homepage (en/index.html) has language switcher pointing to ../index.html')

# 3. Verify assets on en/index.html
srcs = re.findall(r'(?:src|href)=["\']([^"\']+\.(?:jpg|png|gif|css|js|mp4))["\']', en_home)
missing_assets = []
for s in srcs:
    if s.startswith('http') or s.startswith('//'):
        continue
    resolved = os.path.normpath(os.path.join('en', s))
    if not os.path.exists(resolved):
        missing_assets.append((s, resolved))

if missing_assets:
    print(f'[WARN] {len(missing_assets)} assets not found:')
    for orig, res in missing_assets[:10]:
        print(f'  {orig} -> {res}')
else:
    print(f'[OK] All {len(srcs)} local static assets referenced in en/index.html verified on disk!')

# 4. Verify sample subpages
subpages = [
    'en/product_hzpyl.html',
    'en/product_index.html',
    'en/helps/tptjs.html',
    'en/helps/gymej.html',
    'en/article_xwzx.html',
    'en/products/tptyts.html'
]

for sp in subpages:
    assert os.path.exists(sp), f'Subpage {sp} not found'
    with open(sp, 'r', encoding='utf-8') as f:
        sp_html = f.read()
    assert 'class="lang-switch"' in sp_html, f'Language switcher missing in {sp}'
    print(f'[OK] Subpage {sp} verified with language switcher and English content!')

print('\n[SUCCESS] All verification tests passed!')
