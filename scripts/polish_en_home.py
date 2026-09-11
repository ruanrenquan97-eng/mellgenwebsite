# -*- coding: utf-8 -*-
"""
Polish and clean en/index.html and en/mellgen_home.html,
translating all news excerpts, banners, comments, and card snippets into fluent English.
"""

import os
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(WORKSPACE, "en")

REPLACEMENTS = [
    # Headlines with partial translations
    ("Mellgen BiotechWins ISO 9001与FDA GMPCertifications", "Mellgen Biotech Obtains ISO 9001 & FDA GMP Certifications"),
    ("ISO 9001与FDA GMP", "ISO 9001 & FDA GMP"),
    ("Mellgen Biotech5D透皮Collagen获中国Invention Patents授权，Leading Active Ingredients 高效渗...", "Mellgen Biotech 5D Transdermal Collagen Granted Chinese Invention Patent, Leading High Penetration Era..."),
    ("Mellgen Biotech5D透皮Collagen", "Mellgen Biotech 5D Transdermal Collagen"),
    ("获中国Invention Patents授权", "Granted Chinese Invention Patent"),
    ("Leading Active Ingredients 高效渗...", "Leading Active Ingredients High Penetration Era..."),
    ("Leading Active Ingredients 高效渗", "Leading Active Ingredients High Penetration Era"),
    ("Collagen信任危机背后，Mellgen BiotechHow Verified Bio-Tech Restores Industry Confidence...", "Collagen Trust Crisis: How Mellgen Biotech Restores Confidence with Verified Bio-Tech..."),
    ("Collagen信任危机背后，", "Behind the Collagen Trust Crisis: "),
    ("Collagen信任危机背后", "Behind the Collagen Trust Crisis"),
    ("ISO 9001与", "ISO 9001 & "),
    ("与FDA GMP", " & FDA GMP"),
    ("获中国", "Granted Chinese "),
    ("授权，", "Patent, "),
    ("授权", "Patent"),
    ("高效渗", "High Penetration"),
    ("信任危机", "Trust Crisis"),

    # Full sentences & news items on home
    ("双认证加持！美尔健生物斩获ISO 9001与FDA GMP认证，开启原料国际化新征程",
     "Dual Certifications! Mellgen Biotech Obtains ISO 9001 & FDA GMP, Launching Global Strategy"),
    ("双认证加持！Mellgen Biotech斩获ISO 9001与FDA GMP认证，开启原料国际化新征程",
     "Dual Certifications! Mellgen Biotech Obtains ISO 9001 & FDA GMP, Launching Global Strategy"),
    ("在质量管理与国际合规领域再创里程碑——继成功通过ISO 9001质量管理体系认证后，又顺利获得美国食品药品监督管理局（FDA）颁发的GMP认证",
     "Achieving a new milestone in quality management and international compliance: Following ISO 9001 certification, Mellgen has successfully obtained US FDA GMP certification"),
    ("美尔健生物5D透皮胶原蛋白获中国发明专利授权，开启活性成分高效渗透新时代！",
     "Mellgen 5D Transdermal Collagen Granted Chinese Invention Patent, Leading High Penetration Era!"),
    ("Mellgen Biotech5D透皮胶原蛋白获中国发明专利授权，开启活性成分高效渗透新时代！",
     "Mellgen 5D Transdermal Collagen Granted Chinese Invention Patent, Leading High Penetration Era!"),
    ("突破透皮困局！中国团队发现PDRN抗老新靶点，美尔健生物环肽技术破解吸收难题",
     "Overcoming Transdermal Limits! Chinese Team Discovers PDRN Target, Mellgen Cyclic Peptide Solves Absorption Barrier"),
    ("突破透皮困局！中国团队发现PDRN抗老新靶点，Mellgen Biotech环肽技术破解吸收难题",
     "Overcoming Transdermal Limits! Chinese Team Discovers PDRN Target, Mellgen Cyclic Peptide Solves Absorption Barrier"),
    ("PDRN是什么？揭秘美尔健生物的合成生物学如何引领皮肤再生科技新纪元",
     "What is PDRN? How Synthetic Biology Leads a New Era in Skin Regeneration Science"),
    ("PDRN是什么？揭秘Mellgen Biotech的合成生物学如何引领皮肤再生科技新纪元",
     "What is PDRN? How Synthetic Biology Leads a New Era in Skin Regeneration Science"),
    ("胶原蛋白信任危机背后，美尔健生物如何用「真技术」破解行业信任危机？",
     "Behind Collagen Trust Crisis: How Mellgen Biotech Restores Confidence with Genuine Bio-Tech"),
    ("胶原蛋白信任危机背后，Mellgen Biotech如何用「真技术」破解行业信任危机？",
     "Behind Collagen Trust Crisis: How Mellgen Biotech Restores Confidence with Genuine Bio-Tech"),
    ("美尔健生物2025PCHi完美收官/带你回顾精彩盛况",
     "Mellgen Biotech 2025 PCHi Recap: Innovation Showcases & Future Highlights"),
    ("Mellgen Biotech2025PCHi完美收官/带你回顾精彩盛况",
     "Mellgen Biotech 2025 PCHi Recap: Innovation Showcases & Future Highlights"),
    ("为期3天的2025PCHi在此次展会上大放异彩，下面让我们一起回顾那些精彩瞬间。",
     "During the 3-day 2025 PCHi Expo, Mellgen shone brilliantly with breakthrough transdermal innovations. Let's look back at the highlights."),
    ("为期3天的2025 PCHi在此次展会上大放异彩，下面让我们一起回顾那些精彩瞬间。",
     "During the 3-day 2025 PCHi Expo, Mellgen shone brilliantly with breakthrough transdermal innovations. Let's look back at the highlights."),
    ("喜讯！美尔健生物的“一种可透皮的多型重组胶原蛋白溶液及其制备方法和应用”发明获得国家知识产权局颁发的发明专利证书",
     "Great News! Mellgen Biotech's invention 'Transdermal Multi-Type Recombinant Collagen Solution, Preparation, and Application' was awarded Chinese Invention Patent Certificate"),
    ("喜讯！Mellgen Biotech的“一种可透皮的多型重组胶原蛋白溶液及其制备方法和应用”发明获得国家知识产权局颁发的发明专利证书",
     "Great News! Mellgen Biotech's invention 'Transdermal Multi-Type Recombinant Collagen Solution, Preparation, and Application' was awarded Chinese Invention Patent Certificate"),
    ("喜讯！Mellgen Biotech的“一种可透皮的多型", "Great News! Mellgen Biotech's patent 'Transdermal Multi-Type "),
    ("液及其制备方法和应用”发明获得国家", "Collagen Solution and Its Preparation' was awarded Invention Patent "),
    ("证书", "Certificate"),
    ("为期", "During "),
    ("天的", " days of "),
    ("在此次展会上大放异彩，下面让我们一起回顾那些精彩瞬间。", "shone brilliantly at the expo. Here is a recap of the highlights."),
    ("在此次", "at this "),
    ("大放异彩，下面让我们一起回顾那些精彩瞬间。", "shone brilliantly. Let's recap those exciting moments."),
    ("大放异彩，下面让我们一起回顾那些精彩瞬间", "shone brilliantly. Let's recap those exciting moments."),
    ("下面让我们一起回顾那些精彩瞬间", "Let's recap those exciting moments."),
    ("你是否也经历过这些困扰？☑泛红刺痒：稍遇温差或刺激成分，皮肤立刻“拉响警报”；☑干燥脱屑：补水产品越用越干，屏障脆弱如“纸糊”；☑反复敏感：痘痘、泛红不适频发，修护难见起色……",
     "Have you experienced these concerns? Sensitive redness, dry peeling, fragile barrier, or recurring irritation? Precision cellular repair is the scientific answer."),
    ("你是否也经历过这些困扰？", "Have you experienced these skin challenges? "),
    ("泛红刺痒：稍遇温差或刺激", "Redness and stinging with temperature changes or irritants; "),
    ("补水产品越用越干，屏障脆弱如“纸糊”；", "Dry peeling despite hydration, fragile barrier; "),
    ("反复敏感：痘痘、泛红不适频发，修护难见起色", "Recurring sensitivity and redness where standard repair fails..."),
    ("年，中国敏感肌市场规模将突破", "By 2026, the sensitive skin skincare market is projected to exceed "),
    ("亿，消费者需求正从基础修护向“精准抗衰", "billions, with demands shifting from basic soothing toward precision anti-aging "),
    ("多元功效”升级。数据显示，", "and multi-dimensional efficacy. Data shows "),
    ("人群面临敏感困扰，而“敏肌抗老”赛道", "consumers face sensitivity, and the sensitive anti-aging segment "),
    ("同比暴涨", "surged year-on-year, "),
    ("成为品牌必争之地。敏感肌护理", "becoming a crucial focus for leading brands. Sensitive skin care "),
    ("在现代皮肤医学和功效护肤品领域，多聚脱氧核糖核苷酸（PDRN）正迅速成为炙手可热的修复成分。作为一种源自鱼类或植物的DNA片段活性物质，它以其出色的肌肤焕活、舒缓修护和皮肤屏障维护能力，赢得全",
     "In modern dermatology and efficacy skincare, PDRN is rapidly becoming a sought-after restorative active, renowned for cellular revitalization, soothing repair, and skin barrier fortification."),
    ("近日，美妆博主“大嘴博士”质疑某品牌重组胶原产品“测不到胶原蛋白”，引发行业地震。消费者对功效成分的信任度跌至冰点，",
     "Recent industry discussions regarding recombinant collagen verification have prompted leading brands to insist on authentic bio-technology."),
    ("胶原蛋白争议背后，谁在坚守“真成分”？", "Behind the Collagen Debate: Who Stands by Authentic Ingredients?"),
    ("胶原蛋白争议背后，", "Behind the Collagen Debate: "),
    ("谁在坚守“真成分”？", "Who Stands by Authentic Ingredients?"),
    ("在护肤路上，我们都在追寻着让肌肤变得更好的方法。那些昂贵的精华、面霜，真的都被肌肤“吃”进去了吗？其实，",
     "On the journey of skincare, are premium essences and creams truly absorbed by the skin? Transdermal delivery makes the real difference."),
    ("今天，美尔健生物带着它的创新“黑科技”", "Today, Mellgen Biotech presents its innovative transdermal bio-technology"),
    ("探索原料中蛋白的奥秘您是否曾经在挑选护肤品时，尤其是那些听起来就充满营养的“蛋白质”成分，它们在产品中的含量究竟是多少？",
     "Exploring the Mystery of Proteins in Raw Materials: Have you ever wondered about the actual content and purity of protein actives?"),
    ("在医用领域，对材料的安全性、有效性和生物相容性有着颇高的要求。美尔健生物为医用领域提供了创新性的生物活性材料解决方案，其重组胶原（特别是",
     "In medical fields, material safety, efficacy, and biocompatibility demand high standards. Mellgen Biotech provides innovative bioactive materials."),
    ("在医用领域，对材料的安全性、有效性和", "In the medical field, material safety, efficacy, and "),
    ("有着颇高的要求。", "have exceptionally high requirements. "),
    ("为医用领域提供了创新性的", "provides innovative solutions for medical fields, "),
    ("材料", "materials "),
    ("的重组胶原（特别", "recombinant collagen (particularly "),

    # Brand intro & about on home
    ("认准Mellgen (Shenzhen) Biotechnology Co., Ltd.。Mellgen Biotech依托中国科学技术大学生命科学学院和华南理工大学医学院，拥有自主研发的第三代生物透皮技术，致力解决生物大分子，如蛋白多肽，多糖类的无创透皮吸收。",
     "Trust Mellgen (Shenzhen) Biotechnology Co., Ltd. for Medical, Cosmetic, and Food Nutrition Ingredients. Powered by USTC and SCUT, Mellgen features 3rd-Gen transdermal technology for non-invasive absorption of biomacromolecules."),
    ("认准Mellgen (Shenzhen) Biotechnology Co., Ltd.。", "Trust Mellgen (Shenzhen) Biotechnology Co., Ltd. "),
    ("Mellgen Biotech依托中国科学技术大学生命科学学院和华南理工大学医学院，拥有自主研发的第三代生物透皮技术，致力解决生物大分子，如蛋白多肽，多糖类的无创透皮吸收。",
     "Mellgen Biotech is powered by USTC and SCUT, commanding proprietary 3rd-Gen transdermal delivery technology dedicated to non-invasive absorption of biomacromolecules."),
    ("拥有自主研发的第三代生物透皮技术，致力解决生物大分子，如蛋白多肽，多糖类的无创透皮吸收。",
     "Equipped with proprietary 3rd-gen biological transdermal tech, dedicated to non-invasive absorption of biomacromolecules."),
    ("依托中国科学技术大学生命科学学院和华南理工大学医学院", "Powered by USTC School of Life Sciences and SCUT School of Medicine"),

    # HTML Comments
    ("<!-- 头部 开始 -->", "<!-- Header Start -->"),
    ("<!-- 头部 结束 -->", "<!-- Header End -->"),
    ("<!-- 底部 -->", "<!-- Footer -->"),
    ("<!-- 抖音视频直播 -->", "<!-- Video Broadcast -->"),
    ("<!-- 科研成果 -->", "<!-- Scientific Achievements -->"),
    ("<!-- 案例列表 -->", "<!-- Case List -->"),
    ("<!-- 新闻资讯 -->", "<!-- News & Insights -->"),
    ("<!-- 融合技术 -->", "<!-- Fusion Technology -->"),
    ("<!-- 解决方案 -->", "<!-- Solutions -->"),
    ("<!-- 规模化制造中心 -->", "<!-- Manufacturing Center -->"),
    ("<!-- 视频 -->", "<!-- Videos -->"),
    ("<!-- 友情链接 -->", "<!-- Friendly Links -->"),

    # Common tags and titles
    ("双认证加持！", "Dual Certifications! "),
    ("斩获", "Obtains "),
    ("认证，", "Certifications, "),
    ("透皮胶原蛋白获中国", "Transdermal Collagen Granted Chinese "),
    ("授权，开启活性成分高效渗", "Patent, Leading High Penetration Era"),
    ("突破透皮困局！中国团队发现", "Overcoming Transdermal Limits! Chinese Team Discovers "),
    ("抗老新靶点，", "New Anti-Aging Target, "),
    ("环肽技术", "Cyclic Peptide Tech"),
    ("是什么？揭秘", " Explained: How "),
    ("的合成生物学如何引领皮肤再生科技新", " Synthetic Biology Leads Skin Regeneration Tech"),
    ("胶原蛋白信任危机背后，", "Behind Collagen Trust Crisis, "),
    ("如何用「真技术」破解行业信任危机", "How Verified Bio-Tech Restores Industry Confidence"),
    ("版权所有", "Copyright"),
    ("统计", ""),
    ("CNZZ统计", ""),
    ("百度统计", ""),
]

# Sort by length descending
REPLACEMENTS = sorted(REPLACEMENTS, key=lambda x: len(x[0]), reverse=True)

def polish_file(fp):
    if not os.path.exists(fp):
        return
    with open(fp, "r", encoding="utf-8") as f:
        html = f.read()

    orig = html
    for cn, en in REPLACEMENTS:
        html = html.replace(cn, en)

    # Clean any residual Chinese phrases
    html = re.sub(r'<!--\s*[\u4e00-\u9fa5\s]+\s*-->', '', html)
    html = re.sub(r'placeholder="[^"]*搜索[^"]*"', 'placeholder="Please enter keywords to search..."', html)

    if html != orig:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[OK] Polished {fp}")

def main():
    polish_file(os.path.join(EN_DIR, "index.html"))
    polish_file(os.path.join(EN_DIR, "mellgen_home.html"))

if __name__ == "__main__":
    main()
