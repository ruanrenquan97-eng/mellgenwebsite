# -*- coding: utf-8 -*-
"""
Reclassify all WeChat articles strictly according to the official Category List:
["新闻资讯", "企业新闻", "技术知识", "合作案例", "常见问答"]

Also fixes cover images so NO article uses the transparent ban_txt.png,
and hides meaningless placeholder drafts ('分享图片', '化妆品').
"""

import os
import sys
import json
import re
from bs4 import BeautifulSoup

WORKSPACE_DIR = r"e:\私有云\我的AI管理系统\mellgen_website"
CMS_DIR = os.path.join(WORKSPACE_DIR, "cms_system")
DATA_DIR = os.path.join(CMS_DIR, "cms_data")
ARTICLES_FILE = os.path.join(DATA_DIR, "articles.json")

sys.path.insert(0, CMS_DIR)
import generator
import wechat_crawler

OFFICIAL_CATEGORIES = ["新闻资讯", "企业新闻", "技术知识", "合作案例", "常见问答"]

with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
    articles = json.load(f)

# High-quality fallback banners
HIGH_RES_FALLBACKS = {
    "企业新闻": "resource/images/bab44d41caf84e418181ff0690ccb806_16.jpg",
    "技术知识": "resource/images/bab44d41caf84e418181ff0690ccb806_26.jpg",
    "合作案例": "resource/images/b983e8faff7f431887af680abcdc1fa5_2.jpg",
    "新闻资讯": "resource/images/9f838476b8d84546a371528b262cbe05_2.jpg",
    "常见问答": "resource/images/d7a6a892140b4c8b8bad06dc6f4a56eb_24.jpg"
}

def determine_official_category(title, content, desc):
    text = f"{title} {desc} {content[:1500]}"
    
    # 1. 企业新闻 (公司大事件、领导视察、来访、喜报、获奖、院士当选、参展PCHi/高交会、ISO认证、公司简介、研发中心成立等)
    corp_keys = [
        "调研", "视察", "来访", "喜报", "荣获", "副院长", "高交会", "PCHi", "pchi",
        "展会", "大会", "出席", "参会", "公司简介", "发展历程", "签约", "认证", "九三学社",
        "当选", "院士", "FRSB", "新增一项", "发明专利", "中期试验", "应用研究中心", "获奖", "再创辉煌", "高峰论坛", "研发生产中心"
    ]
    if any(k in text for k in corp_keys):
        return "企业新闻"

    # 2. 合作案例
    if any(k in text for k in ["合作案例", "品牌案例", "爆品打造", "客户见证", "采购合作"]):
        return "合作案例"
        
    # 3. 常见问答
    if any(k in text for k in ["常见问题", "问答", "FAQ", "答疑"]):
        return "常见问答"

    # 4. 技术知识 (透皮促渗、重组胶原蛋白、纤连蛋白、多肽、水母黏蛋白、活性物、桃胶、抗老、抗氧化、配方等)
    tech_keys = [
        "纤连蛋白", "多肽", "透皮", "促渗", "抗老", "抗衰", "抗氧化", "桃胶", "发酵",
        "配方", "卡脖子", "原料", "海洋胶原", "活性物", "合成生物", "黏蛋白", "水母",
        "胶原蛋白", "环肽", "柏蕈", "敏感肌", "临床", "屏障", "抗敏", "耐受"
    ]
    if any(k in text for k in tech_keys):
        return "技术知识"

    # 5. 默认归入 新闻资讯
    return "新闻资讯"

updated_count = 0
for a in articles:
    aid = a.get("id", "")
    title = a.get("title", "").strip()
    content = a.get("content", "")
    desc = a.get("desc", "").strip()

    # Hide low quality drafts
    if title in ["分享图片", "化妆品"] or len(title) <= 3:
        a["show"] = False
        print(f"  [Draft Hidden] {aid}: {title}")
        continue

    # Only reclassify WeChat imported articles or ones not in official list
    if aid.startswith("wx_") or a.get("category") not in OFFICIAL_CATEGORIES:
        new_cat = determine_official_category(title, content, desc)
        a["category"] = new_cat
        updated_count += 1

    # Fix cover image: Replace ban_txt.png with actual high quality cover
    img = a.get("image", "").strip()
    if not img or "ban_txt" in img or not os.path.exists(os.path.join(WORKSPACE_DIR, img)):
        # Try finding real image in content
        soup = BeautifulSoup(content, "html.parser")
        first_img = None
        for im_tag in soup.find_all("img"):
            src = im_tag.get("src", "").strip()
            if src and not src.startswith("http") and os.path.exists(os.path.join(WORKSPACE_DIR, src)):
                if os.path.getsize(os.path.join(WORKSPACE_DIR, src)) > 500:
                    first_img = src
                    break
        if first_img:
            a["image"] = first_img
        else:
            cat = a.get("category", "新闻资讯")
            a["image"] = HIGH_RES_FALLBACKS.get(cat, HIGH_RES_FALLBACKS["新闻资讯"])

    # Ensure clean desc without any broken text
    if not desc or len(desc) < 15 or "美尔健（深圳）生物科技有限公司发布：" in desc:
        soup = BeautifulSoup(content, "html.parser")
        text_clean = re.sub(r'\s+', ' ', soup.get_text()).strip()
        text_clean = text_clean.replace("声明与支持：美尔健（深圳）生物科技有限公司致力于生物透皮技术与功效原料研发，如需获取原料详细规格书（TDS）、安全评估资料或定制配方打样，欢迎致电全国服务热线：0755-82926499 / 186-9197-8530。", "").strip()
        if text_clean:
            a["desc"] = text_clean[:120].strip() + "..."
        else:
            a["desc"] = f"美尔健（深圳）生物科技有限公司官方发布：{title}"

# Save to articles.json
with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

# Print final official categories distribution for WeChat articles
wx_dist = {}
for a in articles:
    if a.get("id", "").startswith("wx_") and a.get("show", True):
        c = a.get("category")
        wx_dist[c] = wx_dist.get(c, 0) + 1

print("\n" + "="*60)
print(f"[+] 微信公众号文章在官方分类列表中的最终归类统计 (共 {sum(wx_dist.values())} 篇有效展现):")
for cat_name in OFFICIAL_CATEGORIES:
    print(f"    - 【{cat_name}】: {wx_dist.get(cat_name, 0)} 篇")
print("="*60)

print("\n[*] 正在重新全量编译整站 HTML 页面 (更新分类列表、详情页、新闻资讯中心)...")
generator.publish_site()
generator.generate_sitemap()
print("[+] 整站重新发布圆满完成！")
