# -*- coding: utf-8 -*-
"""
Mellgen Biotechnology - WeChat Content Scraper & Intelligent Classifier Pipeline
Extracts all articles from WeChat account, applies intelligent topical classification,
downloads images, and updates website's News & Information (新闻资讯) and CMS database.
"""

import os
import re
import sys
import json
import time
import hashlib
import datetime
import requests
from bs4 import BeautifulSoup

WORKSPACE_DIR = r"e:\私有云\我的AI管理系统\mellgen_website"
CMS_DIR = os.path.join(WORKSPACE_DIR, "cms_system")
DATA_DIR = os.path.join(CMS_DIR, "cms_data")
WECHAT_IMG_DIR = os.path.join(WORKSPACE_DIR, "resource", "images", "wechat")
os.makedirs(WECHAT_IMG_DIR, exist_ok=True)

sys.path.insert(0, CMS_DIR)
import wechat_crawler
import generator

def classify_article(title, content, digest=""):
    """
    Intelligently classifies WeChat article based on its title, digest, and body content.
    Returns: '企业新闻', '医美行业', '护肤品工厂', '技术知识', '合作案例', or '新闻资讯'.
    """
    text = f"{title} {digest} {content[:1200]}"
    
    # 1. 企业新闻 / 企业动态 (视察、调研、荣获、大会、签约、喜报、简介等)
    corp_keywords = [
        "调研", "视察", "来访", "喜报", "荣获", "副院长", "大会", "出席", "参会",
        "展会", "公司简介", "发展历程", "荣誉", "签约", "战略合作", "成立", "拜访", "领导", "九三学社"
    ]
    if any(k in text for k in corp_keywords):
        return "企业新闻"

    # 2. 合作案例
    case_keywords = ["案例", "品牌方", "爆品", "客户见证", "采购合作", "联合开发"]
    if any(k in text for k in case_keywords):
        return "合作案例"

    # 3. 医美行业 (敏感肌、志愿者、临床、抗敏、受损屏障、医美级等)
    med_keywords = ["敏感肌", "志愿者", "临床", "屏障", "医美", "抗敏", "耐受", "抗炎", "招募"]
    if any(k in text for k in med_keywords):
        return "医美行业"

    # 4. 护肤品工厂 / 技术知识 (透皮、促渗、纤连蛋白、胶原蛋白、多肽、原料、发酵、桃胶等)
    tech_keywords = [
        "纤连蛋白", "多肽", "透皮", "促渗", "抗老", "抗衰", "抗氧化", "桃胶", "发酵",
        "配方", "卡脖子", "原料", "海洋胶原", "活性物", "合成生物", "发明专利", "生物科技"
    ]
    if any(k in text for k in tech_keywords):
        return "护肤品工厂"

    return "新闻资讯"

def run_pipeline():
    print("[*] 正在连接美尔健生物微信公众平台...", flush=True)
    cfg = wechat_crawler.load_wechat_config()
    appid = cfg["appid"]
    appsecret = cfg["appsecret"]
    
    syncer = wechat_crawler.WeChatOfficialSync(appid, appsecret)
    token = syncer.get_access_token()
    print(f"[+] 微信凭证获取成功! Token: {token[:12]}...", flush=True)

    crawled_articles = []
    seen_titles = set()

    # Helper function to process news item
    def process_item(news, pub_date, origin_source="material"):
        title = news.get("title", "").strip()
        if not title or title in seen_titles:
            return None
        seen_titles.add(title)

        author = news.get("author", "美尔健生物").strip() or "美尔健生物"
        digest = news.get("digest", "").strip() or f"美尔健（深圳）生物科技有限公司发布：{title}"
        thumb_url = news.get("thumb_url") or news.get("cover_url") or ""
        raw_content = news.get("content", "")
        source_url = news.get("url") or news.get("content_url") or ""

        # Download cover image
        cover_image = "resource/images/ban_txt.png"
        if thumb_url:
            try:
                cover_image = wechat_crawler.download_wechat_image(thumb_url)
            except Exception:
                cover_image = thumb_url

        # Clean HTML content and download embedded images
        clean_content = wechat_crawler.process_wechat_html_content(raw_content, download_images=True)
        if len(clean_content) < 300 and source_url:
            try:
                scraped = wechat_crawler.scrape_wechat_article_by_url(source_url, download_images=True)
                if scraped and len(scraped.get("content", "")) > 300:
                    clean_content = scraped["content"]
                    if scraped.get("date"):
                        pub_date = scraped["date"]
            except Exception:
                pass

        # Intelligent Classification
        category = classify_article(title, clean_content, digest)

        title_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:8]
        article_id = f"wx_{title_hash}"

        return {
            "id": article_id,
            "title": title,
            "author": author,
            "category": category,
            "image": cover_image,
            "desc": digest,
            "link": f"articles/{article_id}.html",
            "content": clean_content,
            "date": pub_date,
            "source_url": source_url,
            "recommend": False,
            "top": False,
            "show": True,
            "sort": 50
        }

    # 1. Pull Permanent Materials
    print("[*] [1/3] 正在拉取永久图文素材库 (Material Library)...", flush=True)
    offset = 0
    while True:
        try:
            r = requests.post(
                f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}",
                json={"type": "news", "offset": offset, "count": 20},
                timeout=20
            ).json()
        except Exception as e:
            print(f"[-] 素材库请求异常: {e}", flush=True)
            break

        items = r.get("item", [])
        total_count = r.get("total_count", 0)
        item_count = r.get("item_count", len(items))
        if not items:
            break

        for it in items:
            ut = it.get("update_time", int(time.time()))
            p_date = datetime.datetime.fromtimestamp(ut).strftime("%Y-%m-%d")
            news_list = it.get("content", {}).get("news_item", [])
            for n in news_list:
                art = process_item(n, p_date, "material")
                if art:
                    crawled_articles.append(art)
                    print(f"  + 素材入库: [{art['category']}] 《{art['title']}》 ({art['date']})", flush=True)

        offset += item_count
        if offset >= total_count:
            break

    # 2. Pull Drafts
    print("[*] [2/3] 正在拉取图文草稿库 (Draft Library)...", flush=True)
    offset = 0
    while True:
        try:
            r = requests.post(
                f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}",
                json={"offset": offset, "count": 20, "no_content": 0},
                timeout=20
            ).json()
        except Exception as e:
            print(f"[-] 草稿库请求异常: {e}", flush=True)
            break

        items = r.get("item", [])
        total_count = r.get("total_count", 0)
        item_count = r.get("item_count", len(items))
        if not items:
            break

        for it in items:
            ut = it.get("update_time", int(time.time()))
            p_date = datetime.datetime.fromtimestamp(ut).strftime("%Y-%m-%d")
            news_list = it.get("content", {}).get("news_item", [])
            for n in news_list:
                art = process_item(n, p_date, "draft")
                if art:
                    crawled_articles.append(art)
                    print(f"  + 草稿入库: [{art['category']}] 《{art['title']}》 ({art['date']})", flush=True)

        offset += item_count
        if offset >= total_count:
            break

    # 3. Pull Custom Menu News
    print("[*] [3/3] 正在扫描公众号自定义菜单图文 (Menu Items)...", flush=True)
    try:
        m_r = requests.get(
            f"https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token={token}",
            timeout=15
        ).json()
        buttons = m_r.get("selfmenu_info", {}).get("button", [])
        def scan_buttons(b_list):
            for b in b_list:
                if "sub_button" in b and "list" in b["sub_button"]:
                    scan_buttons(b["sub_button"]["list"])
                news_info = b.get("news_info", {}).get("list", [])
                for n in news_info:
                    p_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    art = process_item(n, p_date, "menu")
                    if art:
                        crawled_articles.append(art)
                        print(f"  + 菜单图文: [{art['category']}] 《{art['title']}》", flush=True)
                url = b.get("url", "")
                if url and "mp.weixin.qq.com" in url:
                    try:
                        scraped = wechat_crawler.scrape_wechat_article_by_url(url, download_images=True)
                        if scraped and scraped["title"] not in seen_titles:
                            seen_titles.add(scraped["title"])
                            scraped["category"] = classify_article(scraped["title"], scraped["content"], scraped.get("desc", ""))
                            crawled_articles.append(scraped)
                            print(f"  + 菜单外链: [{scraped['category']}] 《{scraped['title']}》", flush=True)
                    except Exception:
                        pass
        scan_buttons(buttons)
    except Exception as e:
        print(f"[-] 菜单扫描异常: {e}", flush=True)

    print(f"\n[+] 微信公众号图文抓取解析完毕！共获得 {len(crawled_articles)} 篇图文文章。", flush=True)
    
    # Class breakdown
    stats = {}
    for a in crawled_articles:
        stats[a["category"]] = stats.get(a["category"], 0) + 1
    print(f"[*] 智能分类统计结果: {stats}", flush=True)

    # 4. Integrate into articles.json
    articles_file = os.path.join(DATA_DIR, "articles.json")
    existing_articles = []
    if os.path.exists(articles_file):
        with open(articles_file, "r", encoding="utf-8") as f:
            existing_articles = json.load(f)

    existing_titles = {a.get("title", "").strip(): i for i, a in enumerate(existing_articles)}
    
    added = 0
    updated = 0
    for art in crawled_articles:
        t = art["title"].strip()
        if t in existing_titles:
            # Update category and content if existed
            idx = existing_titles[t]
            existing_articles[idx]["category"] = art["category"]
            if len(art["content"]) > len(existing_articles[idx].get("content", "")):
                existing_articles[idx]["content"] = art["content"]
            if art.get("image") and not existing_articles[idx].get("image"):
                existing_articles[idx]["image"] = art["image"]
            updated += 1
        else:
            existing_articles.insert(0, art)
            existing_titles[t] = 0
            added += 1

    with open(articles_file, "w", encoding="utf-8") as f:
        json.dump(existing_articles, f, ensure_ascii=False, indent=2)

    print(f"[+] 数据成功保存至 articles.json! 新增入库: {added} 篇, 更新归类: {updated} 篇, 数据库现存文章总量: {len(existing_articles)} 篇。", flush=True)

    # 5. Compile Static Pages (Generate detail pages & update article_xwzx.html)
    print("[*] 正在重新编译全站静态页面 (生成详情页、更新新闻资讯 article_xwzx.html)...", flush=True)
    try:
        generator.publish_site()
        generator.generate_sitemap()
        print("[+] 官网静态页面全量生成发布成功！已发布至新闻资讯与各大分类频道！", flush=True)
    except Exception as e:
        print(f"[-] 静态页面编译警告: {e}", flush=True)

if __name__ == "__main__":
    run_pipeline()
