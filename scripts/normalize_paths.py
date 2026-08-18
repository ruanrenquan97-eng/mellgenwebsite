# -*- coding: utf-8 -*-
"""
Asset Path Normalizer & Final Chinese Text Cleaner
"""

import os
import glob
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

# 1. Normalize root en/*.html
root_en = glob.glob("en/*.html")
for fp in root_en:
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()

    # Asset paths in en/*.html must start with "../"
    c = re.sub(r'(?:(?:\.\./)+|\./|(?<!/)\b)(images|resource|css|js)/', r'../\1/', c)
    # Fix any double href/src
    c = re.sub(r'(src|href)=["\']\.\./\.\./(images|resource|css|js)/', r'\1="../\2/', c)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(c)

print(f"[OK] Normalized {len(root_en)} root EN files.")

# 2. Normalize subdirectory en/*/**/*.html
sub_en = glob.glob("en/*/**/*.html", recursive=True)
for fp in sub_en:
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()

    # Asset paths in en/subfolder/*.html must start with "../../"
    c = re.sub(r'(?:(?:\.\./)+|\./|(?<!/)\b)(images|resource|css|js)/', r'../../\1/', c)
    # Fix any triple/quadruple
    c = re.sub(r'(src|href)=["\'](?:\.\./){3,}(images|resource|css|js)/', r'\1="../../\2/', c)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(c)

print(f"[OK] Normalized {len(sub_en)} subdirectory EN files.")

# 3. Clean any remaining Chinese fragments in en/index.html
with open("en/index.html", "r", encoding="utf-8", errors="ignore") as f:
    home = f.read()

REPLACEMENTS = [
    ("融合技术", "Fusion Technology"),
    ("案例列表", "Case List"),
    ("视频", "Videos"),
    ("底部", "Footer"),
    ("头部 开始", "Header Start"),
    ("头部 结束", "Header End"),
    ("抖音视频直播", "Video Showcase"),
    ("好原料成就品质美妆", "Premium Raw Materials Empower Quality Beauty"),
    ("从源头做好产品", "Crafting Quality Products from the Source"),
    ("颠覆性透皮科技", "Disruptive Transdermal Tech"),
    ("发明专利矩阵", "Invention Patent Matrix"),
    ("打造“超车式竞争力”", "Building Leapfrog Competitiveness"),
    ("全流程原料研发体系", "End-to-End Raw Material R&D System"),
    ("迅速响应需求", "Rapidly Responding to Demands"),
    ("完成交付与量产", "Delivering Mass Production"),
    ("全球学术界引起广泛关注", "Attracting Widespread Global Academic Acclaim"),
    ("累计高达", "Cumulatively Exceeding "),
    ("深耕者", "Pioneers"),
    ("重塑青春", "Reshaping Youth"),
    ("锁住肌龄", "Locking In Skin Age"),
    ("透皮肽", "Transdermal Peptide"),
    ("透皮", "Transdermal"),
]

for cn, en in REPLACEMENTS:
    home = home.replace(cn, en)

with open("en/index.html", "w", encoding="utf-8") as f:
    f.write(home)

print("[OK] Homepage cleaned!")
