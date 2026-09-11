# -*- coding: utf-8 -*-
"""
Clean all remaining Chinese phrases in en/ website files.
"""

import os
import glob
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(WORKSPACE, "en")

FINAL_REPLACEMENTS = [
    # Complex strings from home & articles
    ("决赛晋级！Transdermal Cyclic Peptide cTDPWins 「了不起的中国原料」总决赛入场券......",
     "Finals Qualified! Transdermal Cyclic Peptide cTDP Enters 'Great Chinese Raw Materials' Grand Finals..."),
    ("决赛晋级！Transdermal Cyclic Peptide cTDPWins 「了不起的中国原料」总决赛入场券",
     "Finals Qualified! Transdermal Cyclic Peptide cTDP Enters 'Great Chinese Raw Materials' Grand Finals"),
    ("「了不起的中国原料」总决赛入场券", "'Great Chinese Raw Materials' Grand Finals"),
    ("「了不起的中国原料」", "'Great Chinese Raw Materials'"),
    ("总决赛入场券", "Grand Finals Entry"),
    ("决赛晋级！", "Finals Qualified! "),
    ("决赛晋级", "Finals Qualified"),

    ("Dual Certifications! Mellgen BiotechWins ISO 9001 & FDA GMP认......",
     "Dual Certifications! Mellgen Biotech Obtains ISO 9001 & FDA GMP Certifications..."),
    ("Dual Certifications! Mellgen BiotechWins ISO 9001 & FDA GMP认",
     "Dual Certifications! Mellgen Biotech Obtains ISO 9001 & FDA GMP Certifications"),
    ("FDA GMP认", "FDA GMP Certifications"),
    ("ISO 9001 & FDA GMP认", "ISO 9001 & FDA GMP Certifications"),

    ("Mellgen (Shenzhen) Biotechnology Co., Ltd.（以下简称“Mellgen Biotech”）在质量管理与国际合规领域再创里程碑——继成功通过ISO 9001质量管理体系认证后，又顺利获得美国食品药品监督管理局（FDA）颁发的GMP认证",
     "Mellgen (Shenzhen) Biotechnology Co., Ltd. has achieved a new milestone in international compliance: following ISO 9001 certification, it has obtained US FDA GMP certification"),
    ("（以下简称“Mellgen Biotech”）在质量管理与国际合规领域再创里程碑——继成功通过ISO 9001",
     "has achieved a new milestone in global quality compliance: following ISO 9001"),
    ("质量管理体系认证后，又顺利获得美国食品药品监督管理局（FDA）颁发的GMP认证",
     "certification, it has successfully obtained US FDA GMP certification"),
    ("（以下简称“Mellgen Biotech”）", "(hereinafter 'Mellgen Biotech') "),
    ("以下简称", "hereinafter referred to as "),
    ("在质量管理与国际合规领域再创里程碑", "achieved a major milestone in global quality compliance"),
    ("继成功通过", "following successful "),
    ("质量管理体系认证后", "quality management system certification"),
    ("又顺利获得", "it has successfully obtained "),
    ("食品药品监督管理局（FDA）颁发的", "issued by US FDA "),
    ("食品药品监督管理局（FDA）", "US Food and Drug Administration (FDA)"),
    ("食品药品监督管理局", "US Food and Drug Administration (FDA)"),
    ("颁发的", "issued by "),

    ("Mellgen Biotech 5D Transdermal CollagenGranted Chinese Invention Patent，开启活性......",
     "Mellgen Biotech 5D Transdermal Collagen Granted Chinese Invention Patent, Leading High Penetration Era..."),
    ("Mellgen Biotech 5D Transdermal CollagenGranted Chinese Invention Patent，开启活性",
     "Mellgen Biotech 5D Transdermal Collagen Granted Chinese Invention Patent, Leading High Penetration Era"),
    ("开启活性成分高效渗透", "Leading High Penetration Era of Bio-Actives"),
    ("开启活性", "Leading High Penetration Era"),

    ("喜讯Mellgen (Shenzhen) Biotechnology Co., Ltd.的“一种可透皮的多型Recombinant Collagen、Recombinant CollagenCo",
     "Great News! Mellgen (Shenzhen) Biotechnology Co., Ltd.'s patent 'Transdermal Multi-Type Recombinant Collagen Solution"),
    ("喜讯！美尔健生物的“一种可透皮的多型", "Great News! Mellgen Biotech's patent 'Transdermal Multi-Type "),
    ("喜讯！", "Great News! "),
    ("喜讯", "Great News: "),
    ("的“一种可透皮的多型", "'s patent 'Transdermal Multi-Type "),
    ("“一种可透皮的多型", "'Transdermal Multi-Type "),
    ("一种可透皮的多型", "Transdermal Multi-Type "),
    ("液及其制备方法和应用”发明获得国家", "Solution, Preparation, and Application' was awarded Chinese Invention "),
    ("液及其制备方法和应用", "Solution, Preparation, and Application"),
    ("发明获得国家", "Invention was awarded National "),
    ("获得国家", "awarded National "),

    ("During 3 days of PCHi&nbsp;Grandly held and successfully concluded at the Canton Fair Complex in Guangzhou",
     "During the 3 days of PCHi, grandly held at the Canton Fair Complex in Guangzhou"),
    ("在展会上大放异彩，下面让我们一起回顾那些精彩瞬间", "shone brilliantly at the expo. Here is a recap of the highlights"),
    ("在此次展会上大放异彩，下面让我们一起回顾那些精彩瞬间。", "shone brilliantly at the expo. Here is a recap of the highlights."),
    ("大放异彩，下面让我们一起回顾那些精彩瞬间", "shone brilliantly. Let's recap those exciting moments"),
    ("大放异彩", "shone brilliantly"),
    ("下面让我们一起回顾那些精彩瞬间", "Let's recap those exciting moments"),
    ("上大放异彩", "shone brilliantly at the expo"),
    ("在此次", "at this "),
    ("上", "at the expo"),

    ("Overcoming Transdermal Limits! Chinese Team Discovers PDRNNew Anti-Aging Target, Mellgen Biotech环肽",
     "Overcoming Transdermal Limits! Chinese Team Discovers PDRN Anti-Aging Target, Mellgen Cyclic Peptide"),
    ("Mellgen Biotech环肽", "Mellgen Biotech Cyclic Peptide"),
    ("环肽技术", "Cyclic Peptide Tech"),
    ("环肽", "Cyclic Peptide"),

    ("​\"被'修复'Misled for So Many Years? Your Sensitive Skin Might Just Need Precision Repair......",
     "Misled by 'Skin Repair' for So Many Years? Your Sensitive Skin Might Just Need Precision Repair..."),
    ("​\"被'修复'Misled for So Many Years? Your Sensitive Skin Might Just Need Precision Repair",
     "Misled by 'Skin Repair' for So Many Years? Your Sensitive Skin Might Just Need Precision Repair"),
    ("​&quot;被'修复'Misled for So Many Years? Your Sensitive Skin Might Just Need Precision Repair",
     "Misled by 'Skin Repair' for So Many Years? Your Sensitive Skin Might Just Need Precision Repair"),
    ("​\"被'修复'", "Misled by 'Skin Repair'"),
    ("​&quot;被'修复'", "Misled by 'Skin Repair'"),
    ("被'修复'", "Misled by 'Skin Repair'"),
    ("被“修复”", "Misled by 'Skin Repair'"),
    ("护方案", "Regimen"),
    ("修复方案", "Repair Regimen"),
    ("被", "by "),

    ("Have you experienced these skin challenges? ☑Redness and stinging with temperature changes or irritants; ☑Dry peeling despite hydration, fragile barrier; ☑Recurring sensitivity and redness where standard repair fails...",
     "Have you experienced these skin challenges? Redness and stinging with temperature changes; Dry peeling despite hydration, fragile barrier; Recurring sensitivity where standard repair fails..."),
    ("你是否也经历过这些困扰？", "Have you experienced these skin challenges? "),
    ("皮肤立刻“拉响警报”", "skin triggers irritation alerts immediately"),
    ("皮肤立刻拉响警报", "skin triggers irritation alerts immediately"),
    ("皮肤立刻", "skin immediately "),
    ("拉响警报", "triggers irritation alerts"),
    ("干燥脱屑", "dryness and flaking"),

    ("PDRN Explained: How Mellgen Biotech的合成生物学如何引领皮肤再生科......",
     "PDRN Explained: How Mellgen Biotech's Synthetic Biology Leads Skin Regeneration Tech..."),
    ("PDRN Explained: How Mellgen Biotech的合成生物学如何引领皮肤再生科",
     "PDRN Explained: How Mellgen Biotech's Synthetic Biology Leads Skin Regeneration Tech"),
    ("的合成生物学如何引领皮肤再生科", "'s Synthetic Biology Leads Skin Regeneration Tech"),
    ("多聚脱氧核糖核苷酸", "Polydeoxyribonucleotide"),

    ("Behind the Collagen Trust Crisis: Mellgen Biotech如何用「真技术」破解行业信任......",
     "Behind the Collagen Trust Crisis: How Mellgen Biotech Restores Industry Confidence with Verified Bio-Tech..."),
    ("Behind the Collagen Trust Crisis: Mellgen Biotech如何用「真技术」破解行业信任",
     "Behind the Collagen Trust Crisis: How Mellgen Biotech Restores Industry Confidence with Verified Bio-Tech"),
    ("如何用「真技术」破解行业信任", "How Verified Bio-Tech Restores Industry Confidence"),
    ("如何用", "How "),
    ("真技术", "Verified Bio-Tech"),
    ("破解行业信任", "Restores Industry Confidence"),

    ("Collagen争议背后， 谁在坚守“真Ingredients”？", "Behind the Collagen Debate: Who Stands by Authentic Ingredients?"),
    ("Collagen争议背后，", "Behind the Collagen Debate: "),
    ("谁在坚守“真Ingredients”？", "Who Stands by Authentic Ingredients?"),
    ("谁在坚守", "Who Stands by "),
    ("真Ingredients", "Authentic Ingredients"),
    ("争议背后", "Behind the Debate"),

    ("探索原料中 蛋白 的奥秘 您是否曾经在挑选护肤品时，Felt confused by complex chemical names on the ingredient list？especially how much protein bio-actives are truly present and active in the formulation？Today, let us unveil the science behind protein purity and content in cosmetic ingredients!",
     "Exploring the Mystery of Proteins in Raw Materials: Have you ever felt confused by complex chemical names while choosing skincare products? Today, let us unveil the science behind protein purity and content!"),
    ("探索原料中 蛋白 的奥秘 您是否曾经在挑选护肤品时", "Exploring the Mystery of Proteins in Raw Materials: Have you ever wondered while choosing skincare"),
    ("探索原料中 蛋白 的奥秘", "Exploring the Mystery of Proteins in Raw Materials"),
    ("探索原料中", "Exploring "),
    ("蛋白 的奥秘", "the Mystery of Proteins"),
    ("的奥秘", "Mystery"),
    ("蛋白", "Proteins"),
    ("您是否曾经在挑选护肤品时", "Have you ever wondered while choosing skincare products"),
    ("就让我们一起揭开护肤品原料中", "let us unveil the truth behind cosmetic raw materials"),

    ("Biocompatibilitydemand the highest standards", "Biocompatibility demand the highest standards"),
    ("特别", "particularly"),

    ("桃芝精华霜", "Peach Resin Essence Cream"),
    ("破解春季敏感肌困", "Solving Spring Sensitive Skin Concerns"),
    ("抗氧化实验全程", "Antioxidant Experiment Peak Performance"),
    ("真皮渗透", "Dermal Penetration"),
    ("科学验", "Scientifically Validated"),
    ("天祛痘", "Days to Blemish Relief"),
    ("系列", "Series"),
    ("修复抗衰一", "All-in-One Repair & Anti-Aging"),

    # Description and footer punctuation
    ("和School of Medicine", "and School of Medicine"),
    ("和", " and "),
    ("，", ", "),
    ("。\"", ".\""),
    ("。”", ".\""),
    ("。", ". "),
    ("？", "? "),
    ("！", "! "),
    ("：", ": "),
    ("；", "; "),
    ("“", "\""),
    ("”", "\""),
    ("‘", "'"),
    ("’", "'"),
]

# Sort by length descending
FINAL_REPLACEMENTS = sorted(FINAL_REPLACEMENTS, key=lambda x: len(x[0]), reverse=True)

def clean_file(fp):
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    orig = content
    for cn, en in FINAL_REPLACEMENTS:
        if cn in content:
            content = content.replace(cn, en)

    # Clean HTML comments with Chinese
    content = re.sub(r'<!--\s*[\u4e00-\u9fa5\s]+?\s*-->', '', content)
    # Clean placeholder
    content = re.sub(r'placeholder="[^"]*搜索[^"]*"', 'placeholder="Please enter keywords to search..."', content)

    if content != orig:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def main():
    files = glob.glob(os.path.join(EN_DIR, "**/*.html"), recursive=True)
    print(f"Cleaning all remaining Chinese phrases in {len(files)} files...")
    cleaned = 0
    for f in files:
        if clean_file(f):
            cleaned += 1
    print(f"[OK] Cleaned {cleaned} files successfully!")

if __name__ == "__main__":
    main()
