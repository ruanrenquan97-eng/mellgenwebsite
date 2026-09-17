import os
import re
import sys

sys.path.insert(0, 'scripts')
import generate_en_product_pages

products, offline_products, settings, nav_links = generate_en_product_pages.load_data()
tphtct = [p for p in products if p['id'] == 'tphtct'][0]

src_cn_path = os.path.join(generate_en_product_pages.WORKSPACE, "products", "tphtct.html")
with open(src_cn_path, "r", encoding="utf-8") as f:
    html = f.read()

print("Step 0 (start from CN):", "jnhtea" in html)

# Step 1: remove B2B
html = re.sub(r'<!-- ==================== B2B PROFESSIONAL DOSSIER & DISCLAIMER ==================== -->[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->', '', html)
html = re.sub(r'<div class="mellgen-b2b-section"[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->', '', html)
print("Step 1 (after clean b2b):", "jnhtea" in html)

# Step 2: SEO Title
# Step 3: Breadcrumbs
# Step 4: Title & Specs
# Step 5: B2B dossier
b2b_html_en = generate_en_product_pages.render_b2b_dossier_en(tphtct)
intro_p = tphtct.get("content", f"<p>{tphtct.get('desc')}</p>")
full_content_en = f"{intro_p}\n{b2b_html_en}"
content_pattern = r'(<div class="p102-pro-content-desc endit-content">)([\s\S]*?)((?:\s*</div>){3,5}\s*<div class="k12-cx-xgcp-4pl-fx1-1-01)'
match = re.search(content_pattern, html)
if match:
    html = html[:match.start(2)] + f"\n     {full_content_en}\n    " + html[match.end(2):]
print("Step 5 (after content):", "jnhtea" in html)

# Step 6: rel_replacements
rel_replacements = [
    ('MELLPRO-RHCTransdermal Recombinant Human Ⅰ型、Ⅲ型', 'MELLPRO-RHC Transdermal Recombinant Human Type I & Type III '),
    ('MELLPRO-RHCTransdermal Recombinant Human Ⅰ型、Ⅲ', 'MELLPRO-RHC Transdermal Recombinant Human Type I & Type III '),
    ('Ⅰ型、Ⅲ型', 'Type I & Type III'),
    ('Ⅰ型、Ⅲ', 'Type I & Type III'),
    ('十肽-4', 'Decapeptide-4'),
    ('水溶性胶原', 'Soluble Collagen'),
    ('水、', 'Aqua, '),
    ('胶原、', 'Collagen, '),
    ('胶原', 'Collagen'),
    ('无色澄澈透明液体', 'Colorless Transparent Liquid'),
    ('水溶', 'Water Soluble'),
]
for k, v in rel_replacements:
    html = html.replace(k, v)
print("Step 6 (after rel_replacements):", "jnhtea" in html)

# Step 7: rec_pattern
print("standard_rec_block_en has jnhtea?", "jnhtea" in generate_en_product_pages.standard_rec_block_en if hasattr(generate_en_product_pages, 'standard_rec_block_en') else "not global")

rec_pattern = r'((?:</div>\s*){3})\s*(?:<div class=["\']k12-cx-xgcp-4pl-fx1-1-01[\s\S]*?)(?=\s*<div class=["\']g_ft f_fw["\'])'
# Check what generate_en_product_pages does!
m_rec = re.search(rec_pattern, html)
print("rec_pattern matched in html?", bool(m_rec))
if m_rec:
    print("matched block length:", len(m_rec.group(0)))
