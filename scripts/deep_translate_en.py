# -*- coding: utf-8 -*-
"""
Deep Translation Engine for Mellgen Biotechnology English Website
Translates all remaining Chinese text in en/ files with precise biotech/pharma terms.
"""

import os
import glob
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(WORKSPACE, "en")

TRANSLATION_PAIRS = [
    # Founder & Team
    ("创始人阮仁全博士当选英国皇家生物学会院士", "Founder Dr. Ruan Renquan Elected Fellow of the Royal Society of Biology (FRSB)"),
    ("阮仁全博士", "Dr. Ruan Renquan"),
    ("阮仁全", "Dr. Ruan Renquan"),
    ("温龙平教授", "Prof. Wen Longping"),
    ("温龙平", "Prof. Wen Longping"),
    ("英国皇家生物学会院士", "Fellow of the Royal Society of Biology (FRSB)"),
    ("中国科学技术大学生命科学学院", "School of Life Sciences, University of Science and Technology of China (USTC)"),
    ("中国科学技术大学", "University of Science and Technology of China (USTC)"),
    ("华南理工大学医学院", "School of Medicine, South China University of Technology (SCUT)"),
    ("华南理工大学", "South China University of Technology (SCUT)"),
    ("斯坦福大学", "Stanford University"),
    ("香港大学", "The University of Hong Kong (HKU)"),
    ("大鹏新区优化营商环境咨询监督委员会委员", "Member of Dapeng New District Business Environment Advisory & Supervisory Committee"),
    ("深圳国际生物谷", "Shenzhen International Bio-Valley"),
    ("粤港澳大湾区产业创新核心区域", "Core Industrial Innovation Zone of Guangdong-Hong Kong-Macao Greater Bay Area"),

    # Technologies & Platforms
    ("生物透皮给药技术是基于中国科学技术大学温龙平教授团队创立的一种透皮肽分子技术",
     "Biological transdermal delivery technology is a transdermal peptide molecular technology founded by Prof. Wen Longping's team at USTC"),
    ("由中国科学技术大学教授和博士后团队成立的一家从事透皮技术孵化",
     "Founded by professors and postdoctoral fellows from USTC, focusing on transdermal tech incubation"),
    ("生物透皮技术作为平台技术可广泛用于生物医药以及医疗美容等领域",
     "As a platform technology, biological transdermal tech is widely applicable in biomedicine and medical aesthetics"),
    ("透皮技术作为平台技术可广泛用于生物医药以及医疗美容等领域",
     "As a platform technology, transdermal tech is widely applicable in biomedicine and medical aesthetics"),
    ("以多肽作为分子伴侣解决生物大分子透皮吸收的世界性难题",
     "Using peptides as molecular chaperones to solve the worldwide challenge of biomacromolecule transdermal absorption"),
    ("聚焦人工智能赋能合成生物新药研发与经皮递送技术创新",
     "Focusing on AI-empowered synthetic biology new drug R&D and innovative transdermal delivery technologies"),
    ("深耕大分子药物透皮给药机理及应用研究领域",
     "Deeply engaged in the mechanism and applied research of macromolecular drug transdermal delivery"),
    ("全球头一次提出透皮肽输运过程能量的参与",
     "First in the world to propose the energy participation in transdermal peptide transport"),
    ("自主研发载体肽与活性成分智能融合体系",
     "Proprietary smart fusion system of carrier peptides and active ingredients"),
    ("公司拥有透皮肽序列库以及质粒载体库",
     "The company possesses proprietary transdermal peptide sequence and plasmid vector libraries"),
    ("提升功效性活性分子在皮肤修护与健康护理方面的有效利用",
     "Enhancing the effective utilization of functional active molecules in skin repair and health care"),
    ("凭借其在生物透皮技术和绿色合成生物制造方面的深厚积累",
     "Leveraging profound accumulation in biological transdermal technology and green synthetic biology"),
    ("凭借其在生物透皮技术和绿色合成生物制造领域的深",
     "Leveraging its deep expertise in biological transdermal technology and green synthetic biology"),
    ("凭借其独特的透皮技术和绿色合成生物制造能力",
     "With unique transdermal technology and green synthetic biology manufacturing capabilities"),
    ("作为生物透皮技术与绿色合成生物制造的深耕者",
     "As a dedicated pioneer in biological transdermal technology and green synthetic biology"),
    ("是一家依托生物透皮技术与绿色合成生物制造",
     "A high-tech enterprise relying on biological transdermal tech and green synthetic biology"),
    ("酶解破壁技术与赢领的分离提取技术得到高含量高活性的天然植物多糖",
     "Enzymatic wall-breaking and advanced separation extraction technologies yield high-purity, high-activity natural botanical polysaccharides"),
    ("可提高透皮肽输运大分子药物的效率并大大降低成本",
     "Greatly improves the transdermal transport efficiency of macromolecular drugs while significantly reducing costs"),

    # Patents & Technical Titles
    ("一种酵母发酵小分子重组纤连蛋白肽及其制备方法和应用",
     "A Yeast-Fermented Small-Molecule Recombinant Fibronectin Peptide, Preparation Method, and Applications"),
    ("基于伴侣肽的透皮增强型重组人源三型胶原蛋白及其应用",
     "Chaperone Peptide-Based Transdermal-Enhanced Recombinant Human Type III Collagen and Its Applications"),
    ("一种促进蛋白质类药物表皮生长因子透皮给药的方法",
     "A Method for Promoting Transdermal Delivery of Protein Drugs (Epidermal Growth Factor)"),
    ("一种协同增效的亮肤修护冻干粉及其制备方法和应用",
     "A Synergistic Brightening & Repair Freeze-Dried Powder, Preparation Method, and Applications"),
    ("一种重组透皮环肽的生物合成方法及透皮吸收应用",
     "A Biosynthesis Method for Recombinant Transdermal Cyclic Peptides and Transdermal Applications"),
    ("一种治疗阴道炎的药物组合物及其制备方法和应用",
     "A Pharmaceutical Composition for Vaginitis Treatment, Preparation Method, and Applications"),
    ("一种仿生重组蜗牛粘液蛋白及其制备方法和应用",
     "A Biomimetic Recombinant Snail Mucin Protein, Preparation Method, and Applications"),
    ("皮肤创伤修复外用溶液制剂及其制备方法和应用",
     "Topical Solution Formulation for Skin Wound Repair, Preparation Method, and Applications"),
    ("一种高效制备植物提取物的加热搅拌均质设备",
     "A High-Efficiency Heating, Stirring, and Homogenizing Device for Botanical Extracts"),
    ("型重组人胶原蛋白水凝胶的制备方法及其应用",
     "Preparation Method and Applications of Recombinant Human Collagen Hydrogel"),
    ("贻贝黏蛋白可以在皮肤表面形成保护层",
     "Mussel adhesive protein forms a protective barrier on the skin surface"),
    ("海洋低温溶菌酶是一种从海洋噬菌体中发现的溶菌酶",
     "Marine psychrophilic lysozyme is an enzyme discovered from marine bacteriophages"),

    # Marketing & General Content
    ("在广州市中国进出口商品交易会展馆盛大举行并圆满落下帷幕",
     "Grandly held and successfully concluded at the Canton Fair Complex in Guangzhou"),
    ("探索原料中蛋白的奥秘您是否曾经在挑选护肤品时",
     "Exploring the Mystery of Proteins in Raw Materials: Have You Ever Wondered While Choosing Skincare"),
    ("对成分表上那些复杂的化学名称感到困惑",
     "Felt confused by complex chemical names on the ingredient list"),
    ("你的敏感肌可能只是缺这套精准修护方案",
     "Your sensitive skin might just need this precision repair regimen"),
    ("人们从未停止过对胶原蛋白的探索与追求",
     "The relentless exploration and pursuit of collagen science has never ceased"),
    ("泛红不适及干纹细纹肌肤的日常修护与改善",
     "Daily repair and improvement of redness, discomfort, dry lines, and fine wrinkles"),
    ("促进胶原蛋白类物质深层吸收至真皮层",
     "Promoting deep absorption of collagen substances into the dermis"),
    ("通过专精的合成生物学和基因工程技术",
     "Through specialized synthetic biology and genetic engineering technologies"),
    ("依托其自主研发的第三代生物透皮技术",
     "Powered by its proprietary 3rd-generation biological transdermal technology"),
    ("每一个环节都凝聚着科技的力量与匠心的坚守",
     "Every stage embodies the power of science and meticulous craftsmanship"),
    ("填写后我司将第一时间与您通过电话取得联系",
     "After submission, our team will contact you promptly via phone"),
    ("消费者对产品的安全性和有效性要求日益提高",
     "Consumers' demands for product safety and efficacy are constantly increasing"),
    ("消费者对产品的个性化需求呈现出前所未有的增长态势",
     "Consumer demand for personalized products is showing unprecedented growth"),
    ("如何提升产品的吸收效率和护肤效果成为了众多",
     "How to improve product absorption efficiency and skincare efficacy has become a priority for many"),
    ("随着全球对环境保护和可持续发展的日益重视",
     "With increasing global focus on environmental protection and sustainability"),
    ("肌肤的吸收问题一直是个困扰着我们的大难题",
     "Skin absorption has long been a challenging bottleneck in skincare science"),
    ("制造与整体方案输出的国家高新技术企业",
     "National high-tech enterprise for manufacturing and turnkey solution delivery"),
    ("美容和生物材料领域有着广泛的应用潜力",
     "Broad application potential in cosmetics and biomaterials"),
    ("是酵母细胞生长过程中通过胞吐作用形成囊泡分泌到细胞外的",
     "Vesicles secreted extracellularly by yeast cells via exocytosis during growth"),
    ("加速各类关键蛋白的合成以达到维持肌肤健康状态",
     "Accelerating key protein synthesis to maintain healthy skin status"),
    ("其所携带的营养物质能够更快更多地被肌肤吸收",
     "Carried active nutrients can be absorbed by the skin faster and in greater amounts"),
    ("帮助用户在可视化操作下生成百度地图",
     "Helping users generate interactive location maps"),
    ("牛商帮是针对企业客户的营销工具使用及营销教育的服务平台",
     "Customer service and support platform for enterprise partners"),

    # Additional UI / Category terms
    ("企业相册", "Corporate Album"),
    ("公司资质", "Qualifications"),
    ("荣誉证书", "Honors & Certificates"),
    ("发明专利", "Invention Patents"),
    ("生产基地", "Manufacturing Base"),
    ("视频中心", "Video Center"),
    ("技术知识", "Technical Knowledge"),
    ("常见问答", "FAQs"),
    ("企业新闻", "Corporate News"),
    ("合作案例", "Case Studies"),
    ("医美行业", "Medical Aesthetics"),
    ("医药行业", "Pharmaceuticals"),
    ("护肤品工厂", "Skincare Factories"),
    ("功能类食品", "Functional Foods"),
    ("洗护用品", "Personal Care"),
    ("女性护理产品", "Feminine Care"),
    ("化妆品", "Cosmetics"),
    ("化妆品原料", "Cosmetic Raw Materials"),
    ("医用原料", "Medical Raw Materials"),
    ("食品营养原料", "Food Nutrition Ingredients"),
    ("原料产品中心", "Raw Material Center"),
    ("透皮肽技术", "Transdermal Peptide Tech"),
    ("原料OEM定制", "Raw Material OEM / Customization"),
    ("关于美尔健", "About Mellgen"),
    ("新闻资讯", "News & Insights"),
    ("快捷链接", "Quick Links"),
    ("产品中心", "Product Center"),
    ("行业案例", "Industry Cases"),
    ("网站地图", "Sitemap"),
    ("首页", "Home"),
    ("电话咨询", "Phone Consultation"),
    ("微信咨询", "WeChat Consultation"),
    ("QQ咨询", "QQ Consultation"),
    ("在线咨询", "Online Consultation"),
    ("微信客服", "WeChat Service"),
    ("微信公众号", "Official WeChat"),
    ("小红书二维码", "RED QR Code"),
    ("抖音二维码", "TikTok QR Code"),
    ("扫码抖音账号", "Scan for TikTok"),
    ("咨询我们", "Contact Us"),
    ("详情", "Details"),
    ("返回顶部", "Back to Top"),
    ("提交", "Submit"),
    ("重置", "Reset"),
    ("您的姓名", "Your Name"),
    ("联系电话", "Contact Phone"),
    ("电子邮箱", "Email Address"),
    ("留言内容", "Message Content"),
    ("验证码", "Verification Code"),
]

# Sort by length descending
TRANSLATION_PAIRS_SORTED = sorted(TRANSLATION_PAIRS, key=lambda x: len(x[0]), reverse=True)

def translate_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    original = content
    for cn, en in TRANSLATION_PAIRS_SORTED:
        content = content.replace(cn, en)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = glob.glob(os.path.join(EN_DIR, "**/*.html"), recursive=True)
    print(f"Applying deep translations across {len(files)} English files...")
    updated_count = 0
    for f in files:
        if translate_file(f):
            updated_count += 1
    print(f"Deep translation complete: {updated_count} files updated.")

if __name__ == '__main__':
    main()
