# -*- coding: utf-8 -*-
with open("en/index.html", "r", encoding="utf-8") as f:
    text = f.read()

REPLACEMENTS = [
    ('认准Mellgen (Shenzhen) Biotechnology Co., Ltd.。Mellgen Biotech依托中国科学技术大学生命科学学院和华南理工大学医学院，拥有自主研发的第三代生物透皮技术，致力解决生物大分子，如蛋白多肽，多糖类的无创透皮吸收。',
     'Trust Mellgen (Shenzhen) Biotechnology Co., Ltd. for Medical, Cosmetic, and Food Nutrition Ingredients. Powered by USTC School of Life Sciences and SCUT School of Medicine, Mellgen features 3rd-Gen transdermal technology for non-invasive absorption of biomacromolecules.'),
    ('<!-- 抖音视频直播 -->', '<!-- Video Broadcast -->'),
    ('<!-- 科研成果 -->', '<!-- Scientific Achievements -->'),
    ('<!-- 案例列表 -->', '<!-- Case List -->'),
    ('<!-- 新闻资讯 -->', '<!-- News & Insights -->'),
    ('<!-- 融合技术 -->', '<!-- Fusion Technology -->'),
    ('<!-- 解决方案 -->', '<!-- Solutions -->'),
    ('<!-- 规模化制造中心 -->', '<!-- Manufacturing Center -->'),
    ('<!-- 视频 -->', '<!-- Videos -->'),
    ('<!-- 友情链接 -->', '<!-- Friendly Links -->'),
    ('<!-- 底部 -->', '<!-- Footer -->'),
    ('<!-- 头部 开始 -->', '<!-- Header Start -->'),
    ('<!-- 头部 结束 -->', '<!-- Header End -->'),
    ('alt="电话"', 'alt="Phone"'),
    ('alt="播放按钮"', 'alt="Play"'),
    ('alt="上一页"', 'alt="Previous"'),
    ('alt="下一页"', 'alt="Next"'),
    ('Leading Active Ingredients 高效渗透', 'Leading Active Ingredients High-Efficiency Penetration'),
    ('Leading Active Ingredients ...', 'Leading Active Ingredients High Penetration...'),
    ('CNZZ统计', 'Statistics'),
    ('保留一切权利', 'All Rights Reserved'),
]

for cn, en in REPLACEMENTS:
    text = text.replace(cn, en)

with open("en/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("en/index.html fully polished and cleaned!")
