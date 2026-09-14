# -*- coding: utf-8 -*-
"""
Site-wide Native English Polish for all 360 English HTML pages:
- Concise, natural 8-item navigation (Home, Cosmetic Actives, Product Catalog, Custom CDMO, Transdermal Tech, Client Cases, Insights, About Us)
- Authoritative, natural brand tagline in header & footer
- Concise, clear search bar prompts & popular searches
- Clean mobile bottom navigation bar
"""

import os
import glob
import re

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.chdir(ROOT_DIR)

def get_clean_nav(prefix="./"):
    return f"""<div class="g_nav menu rter"> 
  <ul>
    <li> <a href="{prefix}index.html" title="Home"> Home </a> </li> 
    <li> <a href="{prefix}product_hzpyl.html" title="Cosmetic Actives"> Cosmetic Actives </a> </li> 
    <li> <a href="{prefix}product_index.html" title="Product Catalog"> Product Catalog </a> </li> 
    <li> <a href="{prefix}helps/yloemd.html" title="Custom CDMO"> Custom CDMO </a> </li> 
    <li> <a href="{prefix}helps/tptjs.html" title="Transdermal Tech"> Transdermal Tech </a> </li> 
    <li> <a href="{prefix}article_hzal.html" title="Client Cases"> Client Cases </a> </li> 
    <li> <a href="{prefix}article_xwzx.html" title="Insights"> Insights </a> </li> 
    <li> <a href="{prefix}helps/gymej.html" title="About Us"> About Us </a> </li> 
  </ul> 
 </div>"""

def polish_file(fp, prefix="./"):
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original = content

    # 1. Update navigation
    nav_pattern = re.compile(r'<div class="g_nav[^"]*">\s*<ul>.*?</ul>\s*</div>', re.DOTALL | re.I)
    content = nav_pattern.sub(get_clean_nav(prefix), content)

    # 2. Update brand tagline in header
    content = re.sub(
        r'<h2 class="lter">\s*<em>.*?</em>\s*<b>.*?</b>\s*</h2>',
        '<h2 class="lter"> <em>Cellular Bio-Actives · Precision Delivery</em><b>Global Pioneer in Transdermal Peptide Technology</b> </h2>',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    # 3. Update search bar
    # Popular searches
    search_html = f'''<p> <b>Popular Searches: </b> 
<a href="{prefix}product_tpxzzd.html" title="Transdermal Peptides">Transdermal Peptides</a> 
<a href="{prefix}products/tpxldb.html" title="Fibronectin">Fibronectin</a> 
<a href="{prefix}products/mellpr8670.html" title="5D Collagen">5D Collagen</a> 
<a href="{prefix}products/pdrnht.html" title="PDRN Actives">PDRN Actives</a> 
<a href="{prefix}helps/yloemd.html" title="Custom CDMO">Custom CDMO</a> 
</p>'''
    content = re.sub(
        r'<p>\s*<b>Popular Searches:\s*</b>.*?</p>',
        search_html,
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Search placeholder
    content = re.sub(
        r'placeholder="Please enter keywords to search\.\.\."',
        'placeholder="Search active ingredients, technology, or solutions..."',
        content,
        flags=re.IGNORECASE
    )

    # 4. Update footer tagline
    content = re.sub(
        r'<h3><b>Reshaping Youth · Locking In Skin Age</b><em>Global Pioneer in Biological Transdermal Technology</em></h3>',
        '<h3><b>Cellular Bio-Actives · Precision Delivery</b><em>Global Pioneer in Transdermal Peptide Technology</em></h3>',
        content
    )

    # 5. Mobile bottom nav (if present)
    content = re.sub(r'Phone Consultation', 'Call Us', content)
    content = re.sub(r'Raw Material Products', 'Products', content)

    # 6. Clean up any remaining Chinese commas or fullstops in titles and H1s
    def clean_punct(m):
        txt = m.group(0)
        txt = txt.replace('，', ', ').replace('。', '. ').replace('！', '! ').replace('；', '; ')
        txt = txt.replace('“', '"').replace('”', '"').replace('【', '[').replace('】', ']')
        txt = txt.replace('（', ' (').replace('）', ') ')
        return txt

    content = re.sub(r'<title>.*?</title>', clean_punct, content, flags=re.DOTALL)
    content = re.sub(r'<h1[^>]*>.*?</h1>', clean_punct, content, flags=re.DOTALL)

    if content != original:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def main():
    root_en = glob.glob("en/*.html")
    sub_en = [f for f in glob.glob("en/*/**/*.html", recursive=True) if "backup_" not in f]

    updated = 0
    for fp in root_en:
        if polish_file(fp, prefix="./"):
            updated += 1

    for fp in sub_en:
        rel = os.path.relpath(fp, "en").replace("\\", "/")
        depth = len(rel.split("/")) - 1
        prefix = "../" * depth
        if polish_file(fp, prefix=prefix):
            updated += 1

    print(f"Site-wide polish completed. Updated {updated} files across {len(root_en) + len(sub_en)} total active files.")

if __name__ == "__main__":
    main()
