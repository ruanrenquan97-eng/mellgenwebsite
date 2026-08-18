# -*- coding: utf-8 -*-
"""
Deep Comprehensive Audit for Mellgen Website (CN & EN)
"""

import os
import glob
import re
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

print("="*60, flush=True)
print("       MELLGEN DUAL-LANGUAGE WEBSITE DEEP AUDIT REPORT", flush=True)
print("="*60, flush=True)

all_cn = [p for p in glob.glob("**/*.html", recursive=True) if not p.startswith("en") and not p.startswith("cms_system") and not p.startswith(".")]
all_en = glob.glob("en/**/*.html", recursive=True)

print(f"[1] Page Inventory: {len(all_cn)} Chinese pages | {len(all_en)} English pages", flush=True)

# 1. Check Language Switchers
cn_missing_switch = [p for p in all_cn if 'class="lang-switch"' not in open(p, "r", encoding="utf-8", errors="ignore").read()]
en_missing_switch = [p for p in all_en if 'class="lang-switch"' not in open(p, "r", encoding="utf-8", errors="ignore").read()]

print(f"    - Chinese pages with Language Switcher: {len(all_cn) - len(cn_missing_switch)}/{len(all_cn)}", flush=True)
print(f"    - English pages with Language Switcher: {len(all_en) - len(en_missing_switch)}/{len(all_en)}", flush=True)

# 2. Check remaining Chinese in English Homepage
with open("en/index.html", "r", encoding="utf-8") as f:
    en_home = f.read()

clean_en_home = en_home.replace('title="中文">CN', '').replace('>中文<', '')
cn_chars = set(re.findall(r'[\u4e00-\u9fa5]+', clean_en_home))
print(f"\n[2] English Homepage Remaining Chinese: {len(cn_chars)} distinct fragments", flush=True)
if cn_chars:
    print("    Sample items:", flush=True)
    for item in sorted(cn_chars, key=len, reverse=True)[:10]:
        print(f"      - {item}", flush=True)

# 3. Check All Local Asset Links in en/index.html & core pages
print("\n[3] Checking Static Asset Integrity across core English Pages...", flush=True)
core_pages = ['en/index.html', 'en/product_hzpyl.html', 'en/product_index.html', 'en/helps/tptjs.html', 'en/helps/gymej.html', 'en/article_xwzx.html']
missing_assets = []

for p in core_pages:
    dir_name = os.path.dirname(p)
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    asset_matches = re.findall(r'(?:src|href)=["\']([^"\']+\.(?:jpg|jpeg|png|gif|css|js|mp4))["\']', content, re.I)
    for asset in asset_matches:
        if asset.startswith("http") or asset.startswith("//") or "consult-tel-icon" in asset:
            continue
        resolved = os.path.normpath(os.path.join(dir_name, asset))
        if not os.path.exists(resolved):
            missing_assets.append((p, asset, resolved))

if missing_assets:
    print(f"    [WARN] Found {len(missing_assets)} missing asset references:", flush=True)
    for file, asset, res in missing_assets[:5]:
        print(f"      In {file}: {asset} -> {res}", flush=True)
else:
    print("    [OK] All static assets in core English pages exist and resolve cleanly!", flush=True)

# 4. Check Internal Hyperlinks in en/index.html
print("\n[4] Checking Navigation & Content Links in en/index.html...", flush=True)
link_matches = re.findall(r'href=["\']([^"\']+\.html)["\']', en_home, re.I)
missing_links = []
for link in link_matches:
    if link.startswith("http") or link.startswith("//"):
        continue
    resolved = os.path.normpath(os.path.join("en", link))
    if not os.path.exists(resolved):
        missing_links.append((link, resolved))

if missing_links:
    print(f"    [WARN] Missing destination pages: {len(missing_links)}", flush=True)
    for l, r in missing_links[:5]:
        print(f"      {l} -> {r}", flush=True)
else:
    print(f"    [OK] All {len(link_matches)} internal page links point to valid existing English pages!", flush=True)

print("\n" + "="*60, flush=True)
print("                      AUDIT COMPLETE", flush=True)
print("="*60, flush=True)
