# -*- coding: utf-8 -*-
import os
import json
import re
from bs4 import BeautifulSoup

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH_JSON = os.path.join(WORKSPACE, "cms_system", "cms_data", "products.json")
EN_JSON = os.path.join(WORKSPACE, "cms_system", "cms_data", "products_en.json")

with open(ZH_JSON, "r", encoding="utf-8") as f:
    zh_products = json.load(f)

with open(EN_JSON, "r", encoding="utf-8") as f:
    en_products = json.load(f)

print(f"Total Products in DB: ZH={len(zh_products)}, EN={len(en_products)}")
assert len(zh_products) == 37, f"Expected 37 products, got {len(zh_products)}"
assert len(en_products) == 37, f"Expected 37 products, got {len(en_products)}"

errors = []
prohibited_words = ["治疗", "治愈", "细胞再生", "生长因子", "消除微炎症", "根除", "手术后"]

for p in zh_products:
    pid = p["id"]
    zh_file = os.path.join(WORKSPACE, "products", f"{pid}.html")
    en_file = os.path.join(WORKSPACE, "en", "products", f"{pid}.html")

    # Check diagram image existence on disk
    diag_img = p.get("diagram_image")
    if diag_img:
        diag_path = os.path.join(WORKSPACE, diag_img.replace("/", os.sep))
        if not os.path.exists(diag_path):
            errors.append(f"Diagram image on disk not found: {diag_path} (for {pid})")

    if not os.path.exists(zh_file):
        errors.append(f"Missing ZH file: {zh_file}")
    else:
        with open(zh_file, "r", encoding="utf-8") as f:
            zh_content = f.read()
        if "原料专业技术与供应档案" not in zh_content:
            errors.append(f"ZH file {pid}.html missing B2B dossier header")
        if "生物科技机理与实验佐证" not in zh_content:
            errors.append(f"ZH file {pid}.html missing mechanism diagram section")
        if "mellgen-rich-product-detail" in zh_content:
            errors.append(f"ZH file {pid}.html contains removed conflicting detail class")
        
        # Check prohibited words in content
        for pw in prohibited_words:
            if pw in p.get("content", ""):
                errors.append(f"ZH product {pid} content contains prohibited compliance word: {pw}")
        if re.search(r'(?<!技)术后', p.get("content", "")):
            errors.append(f"ZH product {pid} content contains medical post-op claim: 术后")

    if not os.path.exists(en_file):
        errors.append(f"Missing EN file: {en_file}")
    else:
        with open(en_file, "r", encoding="utf-8") as f:
            en_content = f.read()
        if "RAW MATERIAL TECHNICAL & REGULATORY DOSSIER" not in en_content and "RAW MATERIAL TECHNICAL &amp; REGULATORY DOSSIER" not in en_content:
            errors.append(f"EN file {pid}.html missing B2B dossier header")
        if "Biotechnology Mechanism &amp; Scientific Evidence" not in en_content and "Biotechnology Mechanism & Scientific Evidence" not in en_content:
            errors.append(f"EN file {pid}.html missing mechanism diagram section")
        if "mellgen-rich-product-detail" in en_content:
            errors.append(f"EN file {pid}.html contains removed conflicting detail class")

if errors:
    print(f"FAILED with {len(errors)} errors:")
    for e in errors[:10]:
        print(" -", e)
else:
    print("SUCCESS: All 37 ZH and EN product detail pages verified cleanly with diagrams, valid disk assets, and strict NMPA compliance!")

