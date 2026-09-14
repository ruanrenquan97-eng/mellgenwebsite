# -*- coding: utf-8 -*-
"""
Clean English Navigation Bar Generator
Ensures the 8 primary navigation sections display cleanly across all English pages without sub-item clutter.
"""

import os
import glob
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def get_clean_en_nav(prefix="./"):
    return f"""<div class="g_nav menu rter"> 
  <ul>
    <li> <a href="{prefix}index.html" title="Home"> Home </a> </li> 
    <li> <a href="{prefix}product_hzpyl.html" title="Cosmetic Raw Materials"> Cosmetics </a> </li> 
    <li> <a href="{prefix}product_index.html" title="Product Center"> Product Center </a> </li> 
    <li> <a href="{prefix}helps/yloemd.html" title="Raw Material OEM / Customization"> OEM Customization </a> </li> 
    <li> <a href="{prefix}helps/tptjs.html" title="Transdermal Peptide Tech"> Transdermal Tech </a> </li> 
    <li> <a href="{prefix}article_hzal.html" title="Case Studies"> Case Studies </a> </li> 
    <li> <a href="{prefix}article_xwzx.html" title="News & Insights"> News & Insights </a> </li> 
    <li> <a href="{prefix}helps/gymej.html" title="About Mellgen"> About Mellgen </a> </li> 
  </ul> 
 </div>"""

nav_pattern = re.compile(r'<div class="g_nav[^"]*">\s*<ul>.*?</ul>\s*</div>', re.DOTALL | re.I)

# 1. Update root en/*.html
root_en_files = glob.glob("en/*.html")
root_updated = 0
for fp in root_en_files:
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    new_nav = get_clean_en_nav("./")
    new_html, count = nav_pattern.subn(new_nav, html)
    if count > 0:
        root_updated += 1
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new_html)

print(f"[OK] Cleaned navigation in {root_updated} / {len(root_en_files)} root English files.")

# 2. Update subdirectory en/*/**/*.html (excluding backup)
sub_en_files = [f for f in glob.glob("en/*/**/*.html", recursive=True) if "backup_" not in f]
sub_updated = 0
for fp in sub_en_files:
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Determine depth relative to en/
    rel = os.path.relpath(fp, "en").replace("\\", "/")
    depth = len(rel.split("/")) - 1
    prefix = "../" * depth

    new_nav = get_clean_en_nav(prefix)
    new_html, count = nav_pattern.subn(new_nav, html)
    if count > 0:
        sub_updated += 1
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new_html)

print(f"[OK] Cleaned navigation in {sub_updated} / {len(sub_en_files)} subdirectory English files.")
