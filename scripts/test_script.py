import os
import re
import json

with open('product_hzpyl.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'(<div class="hyt-product-list-6">)(.*?)(<div class="clear"></div>\s*</div>)', html, re.DOTALL)
print('Match in product_hzpyl.html?', bool(m))

# Check how many products are matched in generator.py
with open('cms_system/cms_data/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

active_products = [p for p in products if p.get("show", True) is not False and p.get("status") != "offline"]
print(f'Active products in products.json: {len(active_products)}')
for p in active_products:
    print(f"Active: {p.get('id')} - {p.get('title')} ({p.get('category')})")

import sys
sys.path.insert(0, 'cms_system')
import generator
subcats = generator.get_product_subcategories("化妆品原料")
print('Subcats for 化妆品原料:', subcats)

cat_prods = [p for p in active_products if p.get('category') in subcats]
print(f'Cat products for 化妆品原料: {len(cat_prods)}')
for p in cat_prods:
    print(f"  {p.get('id')} - {p.get('title')}")
