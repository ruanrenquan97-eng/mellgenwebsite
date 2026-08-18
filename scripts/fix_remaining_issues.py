# -*- coding: utf-8 -*-
"""
Fix asset paths in en subdirectories and translate remaining Chinese text
"""

import os
import glob
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

# 1. Fix asset paths in en subdirectories
sub_files = glob.glob("en/*/**/*.html", recursive=True)
print(f"Fixing asset paths in {len(sub_files)} subdirectory English files...")

for file_path in sub_files:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # In en/helps/, en/products/, en/articles/:
    # Replace single "../resource/" with "../../resource/"
    # Replace single "../images/" with "../../images/"
    # Replace single "../css/" with "../../css/"
    # Replace single "../js/" with "../../js/"
    
    # Avoid triple ../../../ if already ../../
    content = re.sub(r'(?<!\.\.)\.\./resource/', '../../resource/', content)
    content = re.sub(r'(?<!\.\.)\.\./images/', '../../images/', content)
    content = re.sub(r'(?<!\.\.)\.\./css/', '../../css/', content)
    content = re.sub(r'(?<!\.\.)\.\./js/', '../../js/', content)

    # In root en/*.html
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("[OK] Subdirectory asset paths fixed!")

# 2. Fix root en/*.html asset paths
root_files = glob.glob("en/*.html")
for file_path in root_files:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Make sure single ./resource/ or resource/ becomes ../resource/
    content = re.sub(r'src=["\']\./resource/', 'src="../resource/', content)
    content = re.sub(r'src=["\']resource/', 'src="../resource/', content)
    content = re.sub(r'src=["\']\./images/', 'src="../images/', content)
    content = re.sub(r'src=["\']images/', 'src="../images/', content)
    content = re.sub(r'href=["\']\./css/', 'href="../css/', content)
    content = re.sub(r'href=["\']css/', 'href="../css/', content)
    content = re.sub(r'src=["\']\./js/', 'src="../js/', content)
    content = re.sub(r'src=["\']js/', 'src="../js/', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("[OK] Root EN asset paths verified!")

# 3. Translate all remaining Chinese phrases in en/index.html & subpages
EXTRA_TRANSLATIONS = [
    ("认准Mellgen (Shenzhen) Biotechnology Co., Ltd.。", "Trust Mellgen (Shenzhen) Biotechnology Co., Ltd. "),
    ("依托中国科学技术大学生命科学学院和华南理工大学医学院，拥有自主研发的第三代生物透皮技术，致力解决生物大分子，如蛋白多肽，多糖类的无创透皮吸收。",
     "Relying on USTC School of Life Sciences and SCUT School of Medicine, Mellgen possesses proprietary 3rd-generation biological transdermal technology, dedicated to non-invasive transdermal absorption of biomacromolecules such as proteins, peptides, and polysaccharides."),
    ("双认证加持！Mellgen Biotech斩获ISO 9001与FDA GMP认证，", "Dual Certifications! Mellgen Obtains ISO 9001 & FDA GMP, "),
    ("Mellgen Biotech5D透皮胶原蛋白获中国Invention Patents授权，开启活性成分", "Mellgen 5D Transdermal Collagen Granted Invention Patent, Leading Active Ingredients "),
    ("突破透皮困局！中国团队发现PDRN抗老新靶点，Mellgen Biotech环肽技术", "Overcoming Transdermal Limits! PDRN Target Discovered, Cyclic Peptide Tech "),
    ("PDRN是什么？揭秘Mellgen Biotech的合成生物学如何引领皮肤再生科技新", "What is PDRN? How Synthetic Biology Leads Skin Regeneration Tech "),
    ("胶原蛋白信任危机背后，Mellgen Biotech如何用「真技术」破解行业信任危机", "Behind Collagen Trust Crisis: How Mellgen Restores Trust with True Tech "),
    ("透皮型化妆品功效原料定制开发", "Custom Development of Transdermal Cosmetic Efficacy Materials"),
    ("医用械字号原料开发与主文档备案", "Medical Device Grade Material Development & DMF Filing"),
    ("消字号抗菌材料定制开发", "Disinfection Grade Antibacterial Material Customization"),
    ("配方定制服务", "Custom Formulation Services"),
    ("中国发明专利授权", "Chinese Invention Patent Grant"),
    ("中国发明专利", "Chinese Invention Patent"),
    ("中国团队发现", "Chinese Research Team Discovered"),
    ("双认证加持", "Dual Certification Advantage"),
    ("斩获", "Awarded"),
    ("开启活性成分高效渗透新时代", "Ushering in a New Era of High-Efficiency Active Ingredient Penetration"),
    ("开启活性成分", "Unlocking Active Ingredients"),
    ("破解吸收难题", "Solving Absorption Challenges"),
    ("如何引领皮肤再生科技新纪元", "How to Lead a New Era of Skin Regeneration Technology"),
    ("如何引领皮肤再生科技新", "Leading Skin Regeneration Tech"),
    ("如何用「真技术」破解行业信任危机", "How to Resolve Industry Trust Crisis with True Bio-Tech"),
    ("如何用", "How to Use"),
    ("破解行业信任危机", "Solving Industry Trust Crisis"),
    ("环肽技术", "Cyclic Peptide Technology"),
    ("生物透皮技术", "Biological Transdermal Technology"),
    ("生物透皮", "Bio-Transdermal"),
    ("透皮技术", "Transdermal Technology"),
    ("透皮胶原蛋白", "Transdermal Collagen"),
    ("透皮环肽", "Transdermal Cyclic Peptide"),
    ("透皮多肽", "Transdermal Peptide"),
    ("透皮复合肽", "Transdermal Complex Peptide"),
    ("透皮", "Transdermal"),
    ("胶原蛋白", "Collagen"),
    ("合成生物学", "Synthetic Biology"),
    ("皮肤再生科技", "Skin Regeneration Science"),
    ("抗老新靶点", "New Anti-Aging Target"),
    ("抗老", "Anti-Aging"),
    ("抗衰", "Anti-Aging"),
    ("修护", "Repair"),
    ("无创透皮吸收", "Non-invasive Transdermal Absorption"),
    ("蛋白多肽", "Protein Peptides"),
    ("多糖类", "Polysaccharides"),
    ("生物大分子", "Biomacromolecules"),
    ("大分子", "Macromolecules"),
    ("发明专利", "Invention Patents"),
    ("企业新闻", "Corporate News"),
    ("技术知识", "Technical Knowledge"),
    ("常见问答", "FAQs"),
    ("生产基地", "Manufacturing Base"),
    ("企业相册", "Corporate Album"),
    ("荣誉证书", "Honors & Certificates"),
    ("公司资质", "Qualifications"),
    ("视频中心", "Video Center"),
    ("创始人介绍", "Founder Introduction"),
    ("关于美尔健", "About Mellgen"),
    ("美尔健生物", "Mellgen Biotech"),
    ("美尔健", "Mellgen"),
]

EXTRA_SORTED = sorted(EXTRA_TRANSLATIONS, key=lambda x: len(x[0]), reverse=True)

all_en_files = glob.glob("en/**/*.html", recursive=True)
for fp in all_en_files:
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    orig = html
    for cn, en in EXTRA_SORTED:
        html = html.replace(cn, en)

    if html != orig:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(html)

print(f"[OK] Completed extra translation passes across {len(all_en_files)} files!")
