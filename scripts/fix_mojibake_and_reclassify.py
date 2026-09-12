# -*- coding: utf-8 -*-
"""
Fixes any latin-1 mojibake from WeChat JSON and accurately reclassifies all WeChat articles.
Then re-generates all HTML pages.
"""

import os
import sys
import json
import re

CMS_DIR = r"e:\私有云\我的AI管理系统\mellgen_website\cms_system"
sys.path.insert(0, CMS_DIR)
import generator

articles_file = os.path.join(CMS_DIR, "cms_data", "articles.json")
with open(articles_file, "r", encoding="utf-8") as f:
    articles = json.load(f)

def try_fix_mojibake(text):
    if not text or not isinstance(text, str):
        return text
    # Test if contains typical UTF-8 as Latin-1 patterns: 'æ', 'ç', 'é', 'è', 'å', 'ã'
    if any(c in text for c in ["æ", "ç", "é", "è", "å", "ã", "â", "ï", "ä", "ž", "©"]):
        try:
            fixed = text.encode("latin1").decode("utf-8")
            return fixed
        except Exception:
            pass
    return text

def classify_article(title, content, digest=""):
    text = f"{title} {digest} {content[:1500]}"
    
    # 1. 企业新闻 / 企业动态 (调研、来访、喜报、获奖、高交会、展会、PCHi、大会、签约等)
    if any(k in text for k in ["调研", "视察", "来访", "喜报", "荣获", "副院长", "高交会", "PCHi", "pchi", "展会", "大会", "出席", "参会", "公司简介", "发展历程", "签约", "认证", "九三学社"]):
        return "企业新闻"

    # 2. 合作案例
    if any(k in text for k in ["案例", "爆品", "客户见证", "合作方"]):
        return "合作案例"

    # 3. 医美行业
    if any(k in text for k in ["敏感肌", "志愿者", "临床", "屏障受损", "医美", "抗敏", "耐受", "抗炎", "招募", "水光"]):
        return "医美行业"

    # 4. 护肤品工厂 / 原料中心
    if any(k in text for k in ["纤连蛋白", "多肽", "透皮", "促渗", "抗老", "抗衰", "抗氧化", "桃胶", "发酵", "配方", "卡脖子", "原料", "海洋胶原", "活性物", "合成生物", "黏蛋白", "水母"]):
        return "护肤品工厂"

    return "新闻资讯"

fixed_count = 0
for a in articles:
    if a.get("id", "").startswith("wx_"):
        old_title = a.get("title", "")
        new_title = try_fix_mojibake(old_title)
        if new_title != old_title:
            a["title"] = new_title
            fixed_count += 1
            
        a["desc"] = try_fix_mojibake(a.get("desc", ""))
        a["content"] = try_fix_mojibake(a.get("content", ""))
        
        # Accurate reclassification
        a["category"] = classify_article(a["title"], a["content"], a.get("desc", ""))

print(f"[*] 修复乱码文章数: {fixed_count} 篇")

# Print classification breakdown for WeChat articles
wx_cats = {}
for a in articles:
    if a.get("id", "").startswith("wx_"):
        c = a.get("category")
        wx_cats[c] = wx_cats.get(c, 0) + 1

print(f"[*] 微信公众号文章最终精准分类分布: {wx_cats}")

with open(articles_file, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print("[*] 正在全量编译生成所有 HTML 文章页及新闻资讯聚合页...")
generator.publish_site()
generator.generate_sitemap()
print("[+] 修复与全量发布圆满完成！")
