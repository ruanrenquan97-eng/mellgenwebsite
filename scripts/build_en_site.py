# -*- coding: utf-8 -*-
"""
Comprehensive Mellgen Website English Version Generator & Language Switcher Injector
"""

import os
import re
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(WORKSPACE, "en")

# Translation Dictionary
TRANSLATIONS = [
    # Meta / Brand
    ("美尔健（深圳）生物科技有限公司", "Mellgen (Shenzhen) Biotechnology Co., Ltd."),
    ("美尔健生物", "Mellgen Biotech"),
    ("美尔健", "Mellgen"),
    ("重塑青春·锁住肌龄", "Reshaping Youth · Locking In Skin Age"),
    ("全球生物透皮技术深耕者", "Global Pioneer in Biological Transdermal Technology"),
    ("生物科技 · 世界骄傲", "Biotechnology · Global Pride"),
    ("美尔健开创生物修复美容新时代", "Mellgen Pioneers a New Era of Bio-Repair Beauty"),
    ("颠覆性的第三代透皮肽融合技术", "Disruptive 3rd-Generation Transdermal Peptide Fusion Technology"),
    ("医用原料-化妆品原料-食品营养原料", "Medical Raw Materials - Cosmetic Raw Materials - Food Nutrition Ingredients"),
    ("医用原料,化妆品原料,食品营养原料", "Medical Raw Materials, Cosmetic Raw Materials, Food Nutrition Ingredients"),
    ("医用原料,化妆品原料,食品营养原料认准美尔健（深圳）生物科技有限公司。美尔健生物依托中国科学技术大学生命科学学院和华南理工大学医学院，拥有自主研发的第三代生物透皮技术，致力解决生物大分子，如蛋白多肽，多糖类的无创透皮吸收。",
     "Medical, cosmetic, and food nutrition ingredients from Mellgen (Shenzhen) Biotechnology Co., Ltd. Relying on USTC School of Life Sciences and SCUT School of Medicine, Mellgen possesses proprietary 3rd-generation biological transdermal technology, dedicated to non-invasive transdermal absorption of biomacromolecules such as proteins, peptides, and polysaccharides."),

    # Navigation & Categories
    ("首页", "Home"),
    ("化妆品原料", "Cosmetic Raw Materials"),
    ("透皮型重组蛋白/多肽", "Transdermal Recombinant Protein/Peptides"),
    ("透皮型重组蛋白", "Transdermal Recombinant Protein"),
    ("重组仿生蛋白", "Recombinant Biomimetic Protein"),
    ("植物源活性物", "Plant-Derived Actives"),
    ("海洋源活性物", "Marine-Derived Actives"),
    ("婴儿菌发酵源活性物", "Infant Probiotic Fermentation Actives"),
    ("原料产品中心", "Raw Material Center"),
    ("医用原料", "Medical Raw Materials"),
    ("食品营养原料", "Food Nutrition Ingredients"),
    ("原料OEM定制", "Raw Material OEM / Customization"),
    ("原料定制OEM", "Raw Material OEM / Customization"),
    ("透皮肽技术", "Transdermal Peptide Tech"),
    ("合作案例", "Case Studies"),
    ("医美行业", "Medical Aesthetics"),
    ("医药行业", "Pharmaceuticals"),
    ("化妆品", "Cosmetics"),
    ("护肤品工厂", "Skincare Factories"),
    ("功能类食品", "Functional Foods"),
    ("洗护用品", "Personal Care"),
    ("女性护理产品", "Feminine Care"),
    ("新闻资讯", "News & Insights"),
    ("企业新闻", "Corporate News"),
    ("技术知识", "Technical Knowledge"),
    ("常见问答", "FAQs"),
    ("关于美尔健", "About Mellgen"),
    ("关于我们", "About Us"),
    ("创始人介绍", "Founder Introduction"),
    ("企业相册", "Corporate Album"),
    ("生产基地", "Manufacturing Base"),
    ("视频中心", "Video Center"),
    ("荣誉证书", "Honors & Certificates"),
    ("公司资质", "Qualifications"),
    ("发明专利", "Invention Patents"),
    ("快捷链接", "Quick Links"),
    ("解决方案", "Solutions"),
    ("联系我们", "Contact Us"),
    ("产品中心", "Product Center"),
    ("行业案例", "Industry Cases"),
    ("更多行业", "More Industries"),
    ("网站地图", "Sitemap"),

    # Banners
    ("美尔健生物从源头做好产品", "Mellgen Biotech: Crafting Superior Products from the Source"),
    ("突破生物透皮技术在皮肤修复与抗衰应用", "Breakthrough in Biological Transdermal Tech for Skin Repair & Anti-Aging"),
    ("国内外1000+家品牌方携手2000+款化妆品品牌选用我们的原料", "1,000+ Global Brand Partners & 2,000+ Cosmetic Brands Choose Our Ingredients"),

    # Core strengths & labs
    ("22年研发经验", "22 Years R&D Experience"),
    ("期刊SCI论文", "SCI Journal Publications"),
    ("六大研发实验室", "6 R&D Laboratories"),
    ("科创基金支持", "Sci-Tech Fund Support"),
    ("国家药监局注册备案", "NMPA Filing & Registration"),
    ("稀缺四大资源库", "4 Rare Resource Libraries"),
    ("自主知识产权", "Proprietary IP"),
    ("国家及美国发明专利", "CN & US Invention Patents"),
    ("软件注册权登记", "Software Copyrights"),
    ("生物透皮技术孵化中心", "Bio-Transdermal Incubation Center"),
    ("微生物细胞工厂", "Microbial Cell Factory"),
    ("冷冻干燥制剂线", "Freeze-Drying Formulation Line"),
    ("规模化制造中心", "Large-Scale Manufacturing Center"),
    ("科研成果 · 荣誉与责任", "Scientific Achievements · Honors & Responsibilities"),
    ("好原料成就品质美妆", "Premium Raw Materials Empower Quality Beauty"),
    ("了解化妆品原料·从美尔健开始", "Understand Cosmetic Ingredients · Start with Mellgen"),
    ("视频中心 · 原料工厂", "Video Center · Raw Material Factory"),
    ("原料与解决方案", "Raw Materials & Solutions"),
    ("为各大化妆品加工厂，医用，食品品牌等提供应用解决方案", "Providing application solutions for cosmetic manufacturers, medical and food brands worldwide"),
    ("集合分子设计、工艺开发和功效验证到下游原料生产以及终端产品一站式", "One-stop integration from molecular design, process development, and efficacy validation to downstream raw material and end-product manufacturing"),
    ("产品成功打入美国、欧洲、 东南亚等重点区域，备受赞誉", "Products successfully exported to the US, Europe, Southeast Asia, and other key regions, earning high acclaim"),
    ("成功打入美国、欧洲、 东南亚等重点区域，备受赞誉", "Successfully entering the US, Europe, Southeast Asia, and other key regions, widely acclaimed"),
    ("每日价值资讯，精彩资讯实时推荐", "Daily valuable insights and real-time industry updates"),

    # Paragraphs
    ("美尔健生物 是一家依托赢领的生物透皮技术与绿色合成生物制造，专注新型生物功效活性材料开发、制造与整体方案输出的国家高新技术企业。 公司专注“皮肤内源分子”、 “海洋仿生分子”和“特色植物资源”的研究，具备从上游分子设计、工艺开发和功效验证到下游原料生产以及终端产品生产贯通的上下游产业链。",
     "Mellgen Biotech is a national high-tech enterprise focusing on the development, manufacturing, and turnkey solutions of novel bio-efficacy active materials, powered by leading biological transdermal technology and green synthetic biology. The company focuses on the research of 'skin endogenous molecules', 'marine biomimetic molecules', and 'characteristic botanical resources', possessing an integrated upstream and downstream industrial chain from molecular design, process development, and efficacy verification to raw material and finished product manufacturing."),

    ("以人工智能分子设计，合成生物学基础，基因工程、发酵工程为技术手段，开发新一代透皮增强型生物活性分子， 实现蛋白质多肽，植物多糖以及微生物发酵产物等特色功效性生物资源的绿色开发与产业化， 提升功效性活性分子在皮肤修护与健康护理方面的高效率利用。",
     "Utilizing AI molecular design, synthetic biology foundations, genetic engineering, and fermentation technology to develop next-generation transdermal-enhanced bio-active molecules, realizing the green development and industrialization of featured functional bio-resources such as protein peptides, plant polysaccharides, and microbial fermentation products, greatly enhancing the utilization efficiency of active molecules in skin repair and health care."),

    ("公司专注“皮肤内源分子”\"海洋仿生分子”和“特色植物资源”的研究。 以人工智能分子设计，合成生物学基础，基因工程、发酵工程为技术手段，开发新一代透皮增强型生物活性分子， 实现蛋白质多肽，植物多糖以及微生物发酵产物等特色功效性生物资源的绿色开发与产业化。",
     "The company focuses on 'skin endogenous molecules', 'marine biomimetic molecules', and 'featured plant resources', using AI molecular design, synthetic biology, genetic and fermentation engineering to develop next-generation transdermal-enhanced bioactive molecules."),

    ("历经22年漫长科研征途，在生物透皮技术的探索中积累了深厚的科研与应用经验，专注于成为该领域备受信赖的研发创新企业",
     "Through 22 years of dedicated scientific research, we have accumulated profound R&D and application experience in biological transdermal technology, focusing on becoming a highly trusted innovative enterprise in this field."),

    ("在《自然》《科学》 等国际学术期刊上发表了30篇高质量论文,这些论文的影响因子累计高达200 ,在全球学术界引起广泛关注",
     "Published over 30 high-quality papers in top international academic journals including Nature and Science, with cumulative impact factors exceeding 200, attracting widespread global academic acclaim."),

    ("研发实验室体系，涵盖AI人工智能分子设计、分子克隆生物学、细胞生物学、合成生物学、生物透皮给药和皮肤功效测试6大实验室",
     "A comprehensive R&D laboratory system comprising 6 major labs: AI Molecular Design, Molecular Cloning Biology, Cell Biology, Synthetic Biology, Bio-Transdermal Delivery, and Skin Efficacy Testing."),

    ("多项研发项目获得国家青年科学基金，国家博士后科研基金，中国科学技术大学青年科学基金,深圳科创基金支持",
     "Multiple R&D projects supported by the National Youth Science Fund, National Postdoctoral Research Fund, USTC Youth Science Fund, and Shenzhen Science & Tech Innovation Fund."),

    ("高品质生物原料在国家药监局规范完成安全信息与主文档登记，依托先进的AI驱动全流程原料研发体系,我们能迅速响应需求,完成交付与量产",
     "High-quality bio-materials have completed standard safety information and DMF filing with the NMPA. Backed by an advanced AI-driven end-to-end R&D system, we rapidly respond to client demands and deliver mass production."),

    ("拥有全球稀缺的四大资源库,涵盖透皮多肽库,皮肤活性多肽和蛋白库，微生物基因元件库以及微生物菌株库",
     "Equipped with 4 globally scarce proprietary bio-resource repositories: Transdermal Peptide Library, Skin Active Peptide & Protein Library, Microbial Genetic Element Library, and Microbial Strain Library."),

    ("配备医用万级生产洁净车间，价值上千万元的研发设备，同时引入注射剂医用纯水系统，严苛环境与精尖设施，确保产品无菌、纯净，配备近10吨级发酵罐，每年产出各类原料超百吨。 拥有工业化冻干产线，冻干粉剂年产量超10000 万支。全自动化配料灌装产线更是高效率运转， 年产各类水乳膏霜超100万支。",
     "Equipped with Class 10,000 medical cleanrooms and tens of millions worth of R&D instruments, introducing injection-grade purified water systems to ensure aseptic purity. Features ~10-ton fermenters producing over 100 tons of raw materials annually, industrialized freeze-drying lines with annual capacity exceeding 100M vials, and fully automated filling lines producing over 1M units of lotions and creams annually."),

    ("拥有生物透皮技术孵化平台，开展分子生物学、细胞生物学、发酵与纯化工程、制剂开发及人体功效验证等研发工作。1000平制药级GMP细胞工厂，装载7台发酵罐， 总装量达5吨；2000平制剂生产平台，含冻干粉剂生产线，乳化生产线。公司具备从上游分子设计、工艺开发和功效验证到下游原料生产以及终端产品生产贯通的上下游产业链。",
     "Featuring a biological transdermal incubation platform for molecular biology, cell biology, fermentation & purification, formulation development, and clinical efficacy testing. A 1,000m² pharma-grade GMP cell factory with 7 fermenters totaling 5 tons; a 2,000m² formulation platform with freeze-dried powder and emulsification lines."),

    ("拥有工业化冻干产线，冻干粉剂年产量超10000万 支。全自动化配料灌装产线更是高效运转， 年产各类水乳膏霜超100万支，配备医用万级生产洁净车间，同时引入注射剂医用纯水系统，严苛环境与齐全的设施，确保产品无菌，纯净。",
     "Industrialized freeze-drying lines with annual capacity over 100M vials; fully automated high-efficiency formulation lines producing over 1M units of creams/lotions annually with Class 10,000 cleanrooms and pure water systems."),

    ("全球生物透皮技术的原创团队，汇聚了10多位研发科学家，成员分别来自美国斯坦福大学、中国科学技术大学、香港大学以及华南理工大学涵盖教授、博士与博士后。我们对分子结构，分子序列, 制备工艺, 科学配方,菌株等技术实施全方位严格保护，形成无法超越的技术壁垒！",
     "The original team of global biological transdermal technology brings together over 10 leading scientists from Stanford University, University of Science and Technology of China (USTC), University of Hong Kong (HKU), and South China University of Technology (SCUT), including professors, PhDs, and postdocs. We strictly protect molecular structures, sequences, manufacturing processes, formulations, and strains, building solid competitive barriers."),

    # Video Cards
    ("未来美妆战场，创新定制原料成为品牌核心竞争力！", "Future Beauty Battlefield: Custom Innovative Raw Materials as Core Competitiveness!"),
    ("皮肤护理做不好？这里有高科技方案", "Suboptimal Skincare Results? High-Tech Bio Solutions Here"),
    ("你还在用没效果的护肤品？看这里", "Still Using Ineffective Skincare? Discover Transdermal Science"),
    ("美尔健生物给您拜年啦", "Mellgen Biotech Season's Greetings"),
    ("2025护肤品市场千亿预热！！！", "2025 Skincare Market: 100-Billion Surge!"),
    ("“中国芯”原料定制，成美妆爆款新密码！", "'China-Core' Material Customization: Secret to Beauty Best-sellers!"),

    # News & Case Articles
    ("爆品密码再升级:成分x剂型x场景=透皮5D胶原系列，一招破解胶原流失焦虑!", "Blockbuster Code: Ingredient × Form × Scenario = Transdermal 5D Collagen Series!"),
    ("颠覆性透皮科技!美尔健发明专利矩阵，打造“超车式竞争力”", "Disruptive Transdermal Tech! Mellgen Patent Matrix Builds Leapfrog Competitiveness"),
    ("敏感肌护肤新趋势：天然+科技，开启修护抗衰新纪元", "Sensitive Skin New Trend: Natural + Tech, Ushering in Repair & Anti-Aging Era"),
    ("捷报！美尔健生物霸榜「了不起的中国原料」，实力藏不住了", "Triumph! Mellgen Tops 'Great Chinese Raw Materials' List!"),
    ("2026年皮肤科SCI期刊影响因子重磅发布：格局重塑下的投稿策略与选题风向", "2026 Dermatology SCI Impact Factors Released: Editorial Trends & Direction"),
    ("胶原蛋白信任危机？美尔健揭秘「真技术」，拒绝概念添加！", "Collagen Trust Crisis? Mellgen Reveals Genuine Technology, Rejecting Mere Concept Addition!"),
    ("30+抗老新思路：不是补胶原，是给肌肤重铺“弹簧床”", "30+ Anti-Aging: Rebuilding the Skin's 'Spring Mattress' Support"),
    ("别再给敏感肌乱“进补”了！细胞级修护才是真·换脸秘籍", "Cellular-Level Repair: The Genuine Strategy for Sensitive Skin Rejuvenation"),
    ("🔑 一把“钥匙”，5分钟打开皮肤通道——大分子透皮不再是难题", "🔑 The Key to Opening Skin Channels in 5 Mins — Transdermal Biomacromolecules Solved"),
    ("三文鱼DNA多维修护！探索深层水润与肌肤屏障焕活新机制", "Salmon DNA Multi-Dimensional Repair: Deep Hydration & Barrier Revitalization"),
    ("决赛晋级！透皮环肽cTDP斩获「了不起的中国原料」总决赛入场券！", "Finals Qualified! Transdermal Cyclic Peptide cTDP Enters 'Great Chinese Raw Materials' Finals!"),
    ("双认证加持！美尔健生物斩获ISO 9001与FDA GMP认证，开启原料国际化新征程", "Dual Certifications! Mellgen Obtains ISO 9001 & FDA GMP, Launching Global Strategy"),
    ("美尔健生物5D透皮胶原蛋白获中国发明专利授权，开启活性成分高效渗透新时代！", "Mellgen 5D Transdermal Collagen Awarded Invention Patent, Leading High Penetration Era!"),
    ("美尔健生物2025PCHi完美收官/带你回顾精彩盛况", "Mellgen Biotech 2025 PCHi Recap: Highlights & Innovation Showcases"),
    ("突破透皮困局！中国团队发现PDRN抗老新靶点，美尔健生物环肽技术破解吸收难题", "Overcoming Transdermal Limits! PDRN Target Discovered, Cyclic Peptide Solves Absorption Barrier"),
    ("2025敏感肌护肤新趋势：天然+科技，开启修护抗衰新纪元", "2025 Sensitive Skin Trends: Natural + Science, Opening New Repair & Anti-Aging Era"),
    ("PDRN是什么？揭秘美尔健生物的合成生物学如何引领皮肤再生科技新纪元", "What is PDRN? How Synthetic Biology Leads Skin Regeneration Tech"),
    ("温和舒缓干痒不适！揭秘「益生舒缓因子」如何赋能敏肌修护", "Gentle Soothing for Dry Itchiness: Probiotic Soothing Factor in Sensitive Skin Repair"),
    ("胶原蛋白信任危机背后，美尔健生物如何用「真技术」破解行业信任危机？", "Behind Collagen Trust Crisis: How Mellgen Restores Trust with True Bio-Tech"),
    ("肌肤的 “吸收密码”，你找到了吗？", "Have You Unlocked Your Skin's 'Absorption Code'?"),
    ("科普视频｜3分钟看懂原料中蛋白的含量", "Science Video | 3-Minute Guide to Protein Purity & Content"),
    ("美尔健生物：为医用领域提供创新生物活性材料解决方案", "Mellgen Biotech: Delivering Innovative Bioactive Material Solutions for Medical Field"),

    # Products
    ("胎盘肽羊胎素", "Placental Peptide Sheep Placenta"),
    ("PDRN环肽棒", "PDRN Cyclic Peptide Stick"),
    ("MELLPRO 5Dcollagen 5D 胶原", "MELLPRO 5Dcollagen 5D Collagen"),
    ("透皮纤连蛋白", "Transdermal Fibronectin"),
    ("长白山三宝", "Changbai Mountain Three Treasures"),
    ("缺端胶原", "Atelocollagen"),
    ("0型胶原蛋白", "Type 0 Collagen"),
    ("灵芝多糖", "Ganoderma Polysaccharide"),
    ("灵芝黄酮", "Ganoderma Flavonoids"),
    ("人参多肽", "Ginseng Peptide"),
    ("复合营养素", "Complex Nutrients"),
    ("婴儿源益生菌", "Infant-Derived Probiotics"),
    ("重组蛋白", "Recombinant Protein"),
    ("动物源活性物", "Animal-Derived Actives"),
    ("活性抗菌材料", "Active Antibacterial Materials"),
    ("桃胶多糖", "Peach Gum Polysaccharide"),
    ("水母胶原", "Jellyfish Collagen"),
    ("肽维多Vitaluxe", "Peptivida Vitaluxe"),
    ("透皮环肽cTDP", "Transdermal Cyclic Peptide cTDP"),
    ("聚能环肽EAC", "Energy Cyclic Peptide EAC"),
    ("5D胶原蛋白", "5D Collagen"),
    ("重组胶原蛋白溶液", "Recombinant Collagen Solution"),
    ("重组胶原蛋白", "Recombinant Collagen"),
    ("酵母外泌肽", "Yeast Exosome Peptide"),

    # Services
    ("透皮型化妆品功效原料定制开发", "Custom Development of Transdermal Cosmetic Efficacy Materials"),
    ("医用械字号原料开发与主文档备案", "Medical Device Grade Material Development & DMF Filing"),
    ("消字号抗菌材料定制开发", "Disinfection Grade Antibacterial Material Customization"),
    ("配方定制服务", "Custom Formulation Services"),

    # Common UI
    ("电话咨询", "Phone Consultation"),
    ("微信咨询", "WeChat Consultation"),
    ("QQ咨询", "QQ Consultation"),
    ("微信客服", "WeChat Customer Service"),
    ("微信公众号", "WeChat Official Account"),
    ("小红书二维码", "RED QR Code"),
    ("抖音二维码", "TikTok QR Code"),
    ("扫码抖音账号", "Scan for TikTok"),
    ("咨询我们", "Contact Us"),
    ("详情", "Details"),
    ("详情&gt;", "Details &gt;"),
    ("详情 &gt;&gt;", "Details &gt;&gt;"),
    ("上一页", "Previous"),
    ("下一页", "Next"),
    ("播放按钮", "Play Video"),
    ("热搜关键词：", "Popular Searches: "),
    ("您当前的位置：", "Current Location: "),
    ("产品频道", "Products"),
    ("推荐产品", "Recommended Products"),
    ("推荐资讯", "Recommended News"),
    ("产品介绍", "Product Introduction"),
    ("产品优势", "Product Advantages"),
    ("功效与特点", "Efficacy & Features"),
    ("应用场景：", "Applications: "),
    ("推荐应用：", "Recommended Applications: "),
    ("性状：", "Appearance: "),
    ("性状", "Appearance"),
    ("溶解性：", "Solubility: "),
    ("溶解性", "Solubility"),
    ("服务热线：", "Hotline: "),
    ("服务热线", "Hotline"),
    ("包装：", "Packaging: "),
    ("包装", "Packaging"),
    ("无色透明液体", "Colorless Transparent Liquid"),
    ("水溶", "Water Soluble"),
    ("高纯度", "High Purity"),
    ("生物相容性", "Biocompatibility"),
    ("生物活性", "Bioactivity"),
    ("调节细胞活性", "Regulate Cellular Activity"),
    ("去皱抗衰", "Anti-Wrinkle & Anti-Aging"),
    ("促进代谢", "Promote Metabolism"),
    ("收缩毛孔", "Pore Minimizing"),
    ("促进吸收力", "Enhance Absorption"),
    ("友情链接：", "Friendly Links: "),
    ("友情链接", "Friendly Links"),
    ("文思子牙", "Wensi Ziya"),
    ("版权所有 © 2025-2039   美尔健生物   保留一切权利", "Copyright © 2025-2039 Mellgen Biotech. All Rights Reserved."),
    ("版权所有 © 2025-2039\xa0\xa0\xa0美尔健生物\xa0\xa0\xa0保留一切权利\xa0\xa0\xa0", "Copyright © 2025-2039 Mellgen Biotech. All Rights Reserved.\xa0\xa0\xa0"),
    ("备案号：", "ICP License: "),
    ("邮箱：", "Email: "),
    ("地址：广东省深圳市大鹏新区葵涌街道生命科学产业园", "Address: Life Science Industrial Park, Kuichong Sub-district, Dapeng New District, Shenzhen, Guangdong, China"),
    ("地址：", "Address: "),
    ("广东省深圳市大鹏新区葵涌街道生命科学产业园", "Life Science Industrial Park, Kuichong Sub-district, Dapeng New District, Shenzhen, Guangdong, China"),
]

def get_lang_switch_html(is_en=False, depth=0):
    if is_en:
        # English page linking back to Chinese
        if depth == 0:
            cn_url = "../index.html"
            en_url = "./index.html"
        else:
            cn_url = "../../index.html"
            en_url = "../index.html"
        return f'''<div class="lang-switch">
  <span class="lang-icon">🌐</span>
  <a href="{cn_url}" title="中文">CN</a>
  <span class="lang-sep">|</span>
  <a href="{en_url}" class="active" title="English">EN</a>
</div>'''
    else:
        # Chinese page linking to English
        if depth == 0:
            cn_url = "./index.html"
            en_url = "./en/index.html"
        else:
            cn_url = "../index.html"
            en_url = "../en/index.html"
        return f'''<div class="lang-switch">
  <span class="lang-icon">🌐</span>
  <a href="{cn_url}" class="active" title="中文">CN</a>
  <span class="lang-sep">|</span>
  <a href="{en_url}" title="English">EN</a>
</div>'''

def inject_lang_switcher(html, is_en=False, depth=0):
    # Remove existing switcher if present
    html = re.sub(r'<div class="lang-switch">.*?</div>\s*', '', html, flags=re.DOTALL)
    
    switcher_html = get_lang_switch_html(is_en=is_en, depth=depth)
    
    # Inject right inside .m_top before .tel or at top of .m_top
    if '<div class="tel rter">' in html:
        html = html.replace('<div class="tel rter">', switcher_html + '\n  <div class="tel rter">', 1)
    elif '<div class="m_top">' in html:
        html = html.replace('<div class="m_top">', '<div class="m_top">\n  ' + switcher_html, 1)
    elif '<div class="g_top' in html:
        html = re.sub(r'(<div class="g_top[^>]*>)', r'\1\n' + switcher_html, html, count=1)
        
    return html

def translate_html_content(content):
    # Apply all dictionary replacements
    for cn, en in TRANSLATIONS:
        content = content.replace(cn, en)
        
    # Update html lang attribute
    content = re.sub(r'<html[^>]*lang=["\']zh[^"\']*["\']', '<html lang="en"', content, flags=re.I)
    
    return content

def fix_asset_paths_for_en(content, depth=0):
    """
    In en/ root (depth=0):
      ./images/ -> ../images/
      ./css/ -> ../css/
      ./js/ -> ../js/
      ./resource/ -> ../resource/
    In en/subfolder/ (depth=1):
      ../images/ -> ../../images/
      ../css/ -> ../../css/
      ../js/ -> ../../js/
      ../resource/ -> ../../resource/
    """
    if depth == 0:
        # en/*.html
        content = re.sub(r'src=["\']\./images/', 'src="../images/', content)
        content = re.sub(r'src=["\']images/', 'src="../images/', content)
        content = re.sub(r'href=["\']\./css/', 'href="../css/', content)
        content = re.sub(r'href=["\']css/', 'href="../css/', content)
        content = re.sub(r'src=["\']\./js/', 'src="../js/', content)
        content = re.sub(r'src=["\']js/', 'src="../js/', content)
        content = re.sub(r'src=["\']\./resource/', 'src="../resource/', content)
        content = re.sub(r'src=["\']resource/', 'src="../resource/', content)
        content = re.sub(r'url\(\./images/', 'url(../images/', content)
        content = re.sub(r'url\(\./resource/', 'url(../resource/', content)
        content = re.sub(r'href=["\']\./67b', 'href="../css/67b', content)
        content = re.sub(r'href=["\']67b', 'href="../css/67b', content)
    else:
        # en/subfolder/*.html
        content = re.sub(r'src=["\']\.\./images/', 'src="../../images/', content)
        content = re.sub(r'href=["\']\.\./css/', 'href="../../css/', content)
        content = re.sub(r'src=["\']\.\./js/', 'src="../../js/', content)
        content = re.sub(r'src=["\']\.\./resource/', 'src="../../resource/', content)
        content = re.sub(r'url\(\.\./images/', 'url(../../images/', content)
        content = re.sub(r'url\(\.\./resource/', 'url(../../resource/', content)
        content = re.sub(r'url\(\.\./\.\./resource/', 'url(../../resource/', content)
        content = re.sub(r'href=["\']\.\./67b', 'href="../../css/67b', content)

    return content

def process_file(src_rel_path):
    src_abs = os.path.join(WORKSPACE, src_rel_path)
    if not os.path.exists(src_abs) or not src_abs.endswith('.html'):
        return

    with open(src_abs, 'r', encoding='utf-8', errors='ignore') as f:
        src_html = f.read()

    # 1. Update Chinese file with language switcher
    depth_cn = len(src_rel_path.replace('\\', '/').split('/')) - 1
    updated_cn_html = inject_lang_switcher(src_html, is_en=False, depth=depth_cn)
    with open(src_abs, 'w', encoding='utf-8') as f:
        f.write(updated_cn_html)

    # 2. Build English file
    dest_abs = os.path.join(EN_DIR, src_rel_path)
    os.makedirs(os.path.dirname(dest_abs), exist_ok=True)

    en_html = translate_html_content(src_html)
    depth_en = depth_cn
    en_html = fix_asset_paths_for_en(en_html, depth=depth_en)
    en_html = inject_lang_switcher(en_html, is_en=True, depth=depth_en)

    with open(dest_abs, 'w', encoding='utf-8') as f:
        f.write(en_html)

def main():
    print("Starting generation of Mellgen English website and language switchers...")
    os.makedirs(EN_DIR, exist_ok=True)

    # Get all html files in workspace (excluding en, cms_system, .git, etc.)
    all_htmls = []
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in ['.git', 'en', 'cms_system', '.gemini', 'node_modules', '__pycache__']]
        for f in files:
            if f.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, f), WORKSPACE)
                all_htmls.append(rel_path)

    print(f"Found {len(all_htmls)} HTML pages to process.")
    for h in all_htmls:
        process_file(h)

    print(f"Successfully processed {len(all_htmls)} Chinese pages and generated {len(all_htmls)} English pages in en/")

if __name__ == '__main__':
    main()
