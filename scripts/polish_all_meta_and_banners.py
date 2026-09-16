# -*- coding: utf-8 -*-
"""
Polish meta descriptions, titles, and banners across en/ pages.
"""

import os
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

META_REPLACEMENTS = [
    # product_hzpyl.html meta description
    ("作为Biological Transdermal Technology的深耕者, 不断探索Biological Transdermal Technology的无限可能, 为Cosmetic Raw Materials的创新提供了源源不断的动力.",
     "As a dedicated pioneer in biological transdermal technology, Mellgen continuously explores infinite possibilities to power innovative cosmetic raw materials."),
    ("作为Biological Transdermal Technology的深耕者，不断探索Biological Transdermal Technology的无限可能，为Cosmetic Raw Materials的创新提供了源源不断的动力。",
     "As a dedicated pioneer in biological transdermal technology, Mellgen continuously explores infinite possibilities to power innovative cosmetic raw materials."),

    # product_index.html
    ("专注\"皮肤抗衰老分子\"、\"海洋蓝色分子\" and \"特色植物资源\"的研究, 生产Proteins质多肽药物、生物发酵制品, 功能性Cosmetics与保健食品原辅料, 医用可降解材料等多领域产品.",
     "Focusing on skin anti-aging molecules, marine blue molecules, and featured botanical resources, producing protein peptide drugs, bio-fermentation products, functional cosmetic and nutritional ingredients, and medical biodegradable materials."),
    ("专注“皮肤衰老与修护”、“海洋仿生” and “特色植物资源”研究", "focuses on skin aging and repair, marine biomimetics, and featured botanical bio-resources"),
    ("专注“皮肤内源分子”、“海洋仿生分子”和“特色植物资源”的研究", "focuses on skin endogenous molecules, marine biomimetic molecules, and featured botanical resources"),
    ("可广泛用于生物医药、医疗美容、化妆品及保健食品原料、医用可降解材料等领域", "widely applicable in biomedicine, medical aesthetics, cosmetics, nutritional ingredients, and biodegradable materials"),
    ("广泛用于生物医药、医疗美容、化妆品及保健食品原料", "widely applicable in biomedicine, aesthetics, cosmetics, and nutritional ingredients"),
    ("医用可降解材料等众多行业领域", "medical biodegradable materials and diverse industries"),

    # article_xwzx.html meta description
    (", 拥有Biological Transdermal Technology孵化平台, 可开展分子生物学、细胞生物学、发酵与纯化工程、制剂开发及人体功效验证等研发工作.",
     "Covering 4,600m², Mellgen features an advanced transdermal incubation platform for molecular biology, cell biology, fermentation & purification, formulation development, and human efficacy validation."),
    ("公司占地4600平米，拥有Biological Transdermal Technology孵化平台，可开展分子生物学、细胞生物学、发酵与纯化工程、制剂开发及人体功效验证等研发工作。",
     "Covering 4,600m², Mellgen features an advanced transdermal incubation platform for molecular biology, cell biology, fermentation & purification, formulation development, and human efficacy validation."),

    # mellgen_home.html residuals
    ("Behind Ingredient Authenticity: The Quest for Genuine Science 背后：在怕什么？......",
     "Behind Ingredient Authenticity: The Quest for Genuine Science — Rejecting Mere Concept Addition..."),
    ("背后：在怕什么？", " — The Quest for Genuine Science"),
    ("背后：在怕什么", " — The Quest for Genuine Science"),
    ("Mellgen Biotech为医用领域提供了创新性的生物活性材料解决方案，其重组胶原（特别是",
     "Mellgen Biotech delivers innovative bioactive material solutions for medical applications, including recombinant collagen (particularly "),
    ("其重组胶原（特别是", "its recombinant collagen (particularly "),
    ("其重组胶原（特别", "its recombinant collagen (particularly "),
    ("其重组胶原", "its recombinant collagen"),
    ("为医用领域提供了创新性的生物活性材料解决方案", "delivers innovative bioactive material solutions for medical applications"),
    ("为医用领域提供了创新性的", "delivers innovative solutions for medical applications, "),
]

# Sort by length descending
META_REPLACEMENTS = sorted(META_REPLACEMENTS, key=lambda x: len(x[0]), reverse=True)

def polish_target(rel_path):
    fp = os.path.join(WORKSPACE, rel_path)
    if not os.path.exists(fp):
        return
    with open(fp, "r", encoding="utf-8") as f:
        c = f.read()

    orig = c
    for cn, en in META_REPLACEMENTS:
        if cn in c:
            c = c.replace(cn, en)

    if c != orig:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"[OK] Polished {rel_path}")

def main():
    polish_target("en/product_hzpyl.html")
    polish_target("en/product_index.html")
    polish_target("en/article_xwzx.html")
    polish_target("en/mellgen_home.html")
    polish_target("en/index.html")

if __name__ == "__main__":
    main()
