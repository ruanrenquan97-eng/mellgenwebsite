import json

with open('cms_system/cms_data/products.json', 'r', encoding='utf-8') as f:
    cn_products = json.load(f)

with open('cms_system/cms_data/products_en.json', 'r', encoding='utf-8') as f:
    en_products = json.load(f)

en_by_id = {p.get('id'): p for p in en_products}

print(f"Total CN products: {len(cn_products)}")
print(f"Total EN products: {len(en_products)}")

for p in cn_products:
    pid = p.get('id')
    en_p = en_by_id.get(pid, {})
    cn_status = p.get('status')
    cn_show = p.get('show')
    en_status = en_p.get('status')
    en_show = en_p.get('show')
    title = p.get('title')
    cat = p.get('category')
    diff = ""
    if cn_status != en_status or cn_show != en_show:
        diff = " [DIFFERENCE!]"
    print(f"{pid:15} | CN: status={cn_status}, show={cn_show} | EN: status={en_status}, show={en_show} | cat={cat} | {title}{diff}")
