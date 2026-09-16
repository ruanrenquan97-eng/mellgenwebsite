# -*- coding: utf-8 -*-
"""
Deep Translation Engine for Mellgen Biotechnology English Website
Translates all remaining Chinese text in en/ files with precise biotech/pharma terms,
curated dictionaries, and comprehensive pattern localizers.
"""

import os
import glob
import re
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(WORKSPACE, "en")
DICT_PATH = os.path.join(WORKSPACE, "cms_system", "cms_data", "en_dictionary.json")
PRODUCTS_EN_PATH = os.path.join(WORKSPACE, "cms_system", "cms_data", "products_en.json")

def load_all_translations():
    combined = {}

    # 1. Load en_dictionary.json
    if os.path.exists(DICT_PATH):
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
            combined.update(d)

    # 2. Load products_en translations
    if os.path.exists(PRODUCTS_EN_PATH):
        with open(PRODUCTS_EN_PATH, "r", encoding="utf-8") as f:
            prods = json.load(f)
        for p in prods:
            if "title" in p and p["title"]:
                # If we have original Chinese title mapping
                pass

    # 3. Base Curated Biotech / Corporate Pairs
    CURATED = [
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
        ("贻贝黏蛋白可以在皮肤表面形成保护层",
         "Mussel adhesive protein forms a protective barrier on the skin surface"),
        ("海洋低温溶菌酶是一种从海洋噬菌体中发现的溶菌酶",
         "Marine psychrophilic lysozyme is an enzyme discovered from marine bacteriophages"),

        # Common sentences in articles
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
        ("在护肤路上，我们都在追寻着让肌肤变得更好的方法。那些昂贵的精华、面霜，真的都被肌肤“吃”进去了吗？其实，",
         "On our skincare journey, we constantly seek ways to improve our skin. Are expensive serums and creams truly absorbed?"),
        ("在现代皮肤医学和功效护肤品领域，多聚脱氧核糖核苷酸（PDRN）正迅速成为炙手可热的修护成分。作为一种源自鱼类或植物的DNA片段活性物质，它以其出色的肌肤焕活、舒缓修护和皮肤屏障维护能力，赢得全",
         "In modern dermatology and functional skincare, PDRN (Polydeoxyribonucleotide) is emerging as a premier reparative active. Originating from marine DNA fragments, it delivers profound cellular revitalization, soothing repair, and barrier defense."),
        ("在现代皮肤医学和功效护肤品领域，", "In modern dermatology and efficacy skincare, "),
        ("正迅速成为炙手可热的修护成分。作为一种源自鱼类或植物的", "is rapidly becoming a sought-after restorative active. As a substance derived from marine or botanical sources, "),
        ("片段活性物质，它以其出色的肌肤焕活、舒缓修护和皮肤屏障维护能力，赢得全", "active fragments, it earns widespread acclaim for cellular revitalization, soothing repair, and barrier defense."),
        ("近日，美妆博主“大嘴博士”质疑某品牌重组胶原产品“测不到胶原蛋白”，引发行业地震。消费者对功效成分的信任度跌至冰点，",
         "Recent industry discussions concerning recombinant collagen purity have prompted brands to prioritize verified authentic technology."),
        ("近日，美妆博主“大嘴博士”质疑某品牌重组胶原产品“测不到胶原", "Recent industry discussions concerning recombinant collagen purity, "),
        ("蛋白”，引发行业地震。消费者对功效成分的信任度跌至冰点，", "prompting brands to prioritize verified authentic bio-technology."),
        ("成分造假风波背后：在怕什么？", "Behind Ingredient Authenticity: The Quest for Genuine Science"),
        ("今天，美尔健生物带着它的创新“黑科技”", "Today, Mellgen Biotech presents its innovative bio-technology"),
        ("今天，", "Today, "),
        ("带着它的创新“黑科", "presenting its innovative transdermal bio-technology"),
        ("探索原料中蛋白的奥秘", "Exploring the Mystery of Proteins in Raw Materials"),
        ("您是否曾经在挑选护肤品时，尤其是那些听起来就充满营养的“蛋白质”成分，它们在产品中的含量究竟是多少？", "Have you ever wondered about the actual content and purity of protein ingredients when choosing skincare products?"),
        ("尤其是那些听起来就充满营养的“蛋白质”成分，它们在产品中的含量究竟是多少？", "especially how much protein bio-actives are truly present and active in the formulation?"),
        ("今天，就让我们一起揭开护肤品原料中蛋白含量的神秘面纱！", "Today, let us unveil the science behind protein purity and content in cosmetic ingredients!"),
        ("在医用领域，对材料的安全性、有效性和生物相容性有着颇高的要求。", "In the medical field, material safety, efficacy, and biocompatibility demand the highest standards."),
        ("有着颇高的要求。", "demand the highest standards."),
        ("为医用领域提供了创新性的生物活性材料解决方案", "delivers innovative bioactive material solutions for medical applications"),
        ("的重组胶原（特别是", "recombinant collagen (particularly "),

        # Additional UI
        ("您的姓名", "Your Name"),
        ("联系电话", "Contact Phone"),
        ("电子邮箱", "Email Address"),
        ("留言内容", "Message Content"),
        ("验证码", "Verification Code"),
        ("提交", "Submit"),
        ("重置", "Reset"),
        ("发送", "Send"),
        ("清除", "Clear"),
        ("CNZZ统计", ""),
        ("百度统计", ""),
        ("网站统计", ""),
    ]

    for cn, en in CURATED:
        if cn not in combined:
            combined[cn] = en

    # Order strictly by key length descending
    sorted_items = sorted(combined.items(), key=lambda x: len(x[0]), reverse=True)
    return sorted_items

def translate_file(file_path, translations):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    original = content

    # 1. Apply translation dictionary
    for cn, en in translations:
        if cn in content:
            content = content.replace(cn, en)

    # 2. Cleanup HTML attributes
    content = re.sub(r'<html[^>]*lang=["\']zh[^"\']*["\']', '<html lang="en"', content, flags=re.I)
    content = re.sub(r'placeholder="请输入您要搜索的关键词"', 'placeholder="Please enter keywords to search..."', content)
    content = re.sub(r'placeholder="[^"]*搜索[^"]*"', 'placeholder="Please enter keywords to search..."', content)
    content = re.sub(r'>\s*CNZZ统计\s*<', '><', content)
    content = re.sub(r'>\s*统计\s*<', '><', content)

    # 3. Clean remaining dates like 2025年03月15日 -> 2025-03-15
    content = re.sub(r'(\d{4})年(\d{1,2})月(\d{1,2})日', r'\1-\2-\3', content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("Loading all translation datasets...")
    translations = load_all_translations()
    print(f"Total {len(translations)} translation rules loaded.")

    files = glob.glob(os.path.join(EN_DIR, "**/*.html"), recursive=True)
    files = [f for f in files if "backup" not in f]
    print(f"Applying deep translations across {len(files)} English files...")
    updated_count = 0
    for f in files:
        if translate_file(f, translations):
            updated_count += 1
    print(f"Deep translation complete: {updated_count} files updated.")

if __name__ == '__main__':
    main()
