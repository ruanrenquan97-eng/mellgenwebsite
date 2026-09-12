# -*- coding: utf-8 -*-
"""
Mellgen Biotechnology - WeChat Official Account Crawler & Auto-Sync Engine
Supports:
1. WeChat Official MP API (freepublish/batchget) for full, lossless history sync
2. Smart Article Web Scraper for single/batch WeChat article URLs
3. Anti-leech image downloading and path replacement to resource/images/wechat/
4. Auto-deduplication, CMS articles.json integration, and static site rebuilding
"""

import os
import re
import sys
import time
import json
import uuid
import hashlib
import datetime
import threading
import urllib.parse
import requests
from bs4 import BeautifulSoup

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")
CONFIG_FILE = os.path.join(DATA_DIR, "wechat_config.json")
WECHAT_IMG_DIR = os.path.join(WORKSPACE_DIR, "resource", "images", "wechat")
os.makedirs(WECHAT_IMG_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "appid": "",
    "appsecret": "",
    "account_name": "美尔健生物",
    "auto_sync_daily": True,
    "default_category": "新闻资讯",
    "download_images": True,
    "last_sync_time": None,
    "last_sync_status": "就绪",
    "total_synced": 0
}

# In-memory sync state for real-time progress monitoring
_sync_state = {
    "is_running": False,
    "task_id": None,
    "trigger": None,
    "status": "idle",
    "message": "待机就绪",
    "progress": 0,
    "total": 0,
    "current": 0,
    "added": 0,
    "skipped": 0,
    "failed": 0,
    "logs": []
}
_state_lock = threading.Lock()

def get_sync_state():
    with _state_lock:
        return dict(_sync_state)

def update_sync_state(**kwargs):
    with _state_lock:
        for k, v in kwargs.items():
            _sync_state[k] = v
        if "log" in kwargs and kwargs["log"]:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_line = f"[{timestamp}] {kwargs['log']}"
            _sync_state["logs"].append(log_line)
            if len(_sync_state["logs"]) > 100:
                _sync_state["logs"] = _sync_state["logs"][-100:]
            print(f"[WeChat Sync] {log_line}")

def load_wechat_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = dict(DEFAULT_CONFIG)
                merged.update(data)
                return merged
        except Exception as e:
            print(f"[-] Failed to load wechat_config.json: {e}")
    return dict(DEFAULT_CONFIG)

def save_wechat_config(config_data):
    try:
        cur = load_wechat_config()
        cur.update(config_data)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[-] Failed to save wechat_config.json: {e}")
        return False

# ==============================================================================
# Anti-Leech Image Downloader
# ==============================================================================
def download_wechat_image(img_url, timeout=12):
    """
    Downloads WeChat images (mmbiz.qpic.cn) with appropriate headers to bypass 403.
    Saves to resource/images/wechat/{hash}.{ext}
    Returns the relative path 'resource/images/wechat/...' or original if failed.
    """
    if not img_url or not isinstance(img_url, str):
        return ""
    img_url = img_url.strip()
    if not img_url.startswith("http"):
        return img_url
    
    # Check if already local
    if img_url.startswith("resource/") or img_url.startswith("images/"):
        return img_url

    url_hash = hashlib.md5(img_url.encode("utf-8")).hexdigest()
    
    # Try guessing extension
    ext = "jpg"
    lower_url = img_url.lower()
    if "wx_fmt=png" in lower_url or lower_url.endswith(".png"):
        ext = "png"
    elif "wx_fmt=webp" in lower_url or lower_url.endswith(".webp"):
        ext = "webp"
    elif "wx_fmt=gif" in lower_url or lower_url.endswith(".gif"):
        ext = "gif"
        
    filename = f"{url_hash}.{ext}"
    local_path = os.path.join(WECHAT_IMG_DIR, filename)
    rel_path = f"resource/images/wechat/{filename}"

    if os.path.exists(local_path) and os.path.getsize(local_path) > 100:
        return rel_path

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://mp.weixin.qq.com/",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }

    try:
        resp = requests.get(img_url, headers=headers, timeout=timeout)
        if resp.status_code == 200 and len(resp.content) > 100:
            # Correct extension based on content-type if available
            ctype = resp.headers.get("Content-Type", "").lower()
            if "png" in ctype and ext != "png":
                ext = "png"
                filename = f"{url_hash}.{ext}"
                local_path = os.path.join(WECHAT_IMG_DIR, filename)
                rel_path = f"resource/images/wechat/{filename}"
            elif "gif" in ctype and ext != "gif":
                ext = "gif"
                filename = f"{url_hash}.{ext}"
                local_path = os.path.join(WECHAT_IMG_DIR, filename)
                rel_path = f"resource/images/wechat/{filename}"

            with open(local_path, "wb") as f:
                f.write(resp.content)
            return rel_path
    except Exception as e:
        print(f"[-] Failed to download image {img_url[:60]}: {e}")
    
    return img_url

def process_wechat_html_content(raw_html, download_images=True):
    """
    Sanitizes WeChat article HTML:
    1. Replaces data-src with local image src
    2. Removes WeChat tracking scripts, applet tags, qr-code cards, and reward blocks
    3. Wraps in standard Mellgen website article wrapper
    """
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove script, style, iframe, audio/video ads
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    # Remove WeChat specific widget blocks
    for selector in [
        "#js_toobar3", "#js_view_source", ".reward_area", ".qr_code_pc",
        ".profile_container", ".share_media", ".like_area", ".weui-dialog"
    ]:
        for el in soup.select(selector):
            el.decompose()

    # Process all img tags
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if not src:
            img.decompose()
            continue

        if download_images:
            local_src = download_wechat_image(src)
            img["src"] = local_src
        else:
            img["src"] = src

        # Remove problematic wechat img attributes
        for attr in ["data-src", "data-ratio", "data-w", "data-type", "data-s", "data-fail"]:
            if attr in img.attrs:
                del img.attrs[attr]

        # Ensure responsive styling
        existing_style = img.get("style", "")
        img["style"] = f"max-width:100%;height:auto;display:block;margin:16px auto;border-radius:6px;{existing_style}"

    # Clean styling on containers
    body_content = ""
    js_content = soup.find(id="js_content")
    if js_content:
        body_content = "".join([str(c) for c in js_content.children])
    else:
        body_content = str(soup)

    # Format into website template wrapper
    formatted_html = f"""<div class="article-body-wrapper" style="line-height:1.9;color:#333;font-size:15px;text-align:justify;">
    {body_content}
    <div class="article-footer-note" style="margin-top:32px;padding:14px 18px;background:#fafafa;border:1px dashed #dcdcdc;border-radius:6px;font-size:13px;color:#777;">
        <p style="margin:0;line-height:1.6;"><strong>声明与支持：</strong>美尔健（深圳）生物科技有限公司致力于生物透皮技术与功效原料研发，如需获取原料详细规格书（TDS）、安全评估资料或定制配方打样，欢迎致电全国服务热线：0755-82926499 / 186-9197-8530。</p>
    </div>
</div>"""

    return formatted_html

# ==============================================================================
# Mode A: WeChat Article URL Scraper
# ==============================================================================
def scrape_wechat_article_by_url(url, download_images=True):
    """
    Scrapes a single WeChat article given its URL.
    Returns a dict with title, author, date, desc, image, content, link, or None on failure.
    """
    if not url or not url.startswith("http"):
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            print(f"[-] HTTP Error {resp.status_code} fetching {url}")
            return None

        html_text = resp.text
        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Title
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        if not title:
            h1 = soup.find(id="activity-name")
            if h1:
                title = h1.get_text(strip=True)
        if not title and soup.title:
            title = soup.title.get_text(strip=True)
            
        if not title:
            return None

        # 2. Author
        author = "美尔健生物"
        og_author = soup.find("meta", property="og:article:author")
        if og_author and og_author.get("content"):
            author = og_author["content"].strip()
        else:
            author_node = soup.find(id="js_author_name") or soup.find(class_="profile_nickname")
            if author_node:
                author = author_node.get_text(strip=True)

        # 3. Publish Date
        pub_date = datetime.datetime.now().strftime("%Y-%m-%d")
        # Match ct timestamp (var ct = "1719912000")
        ct_match = re.search(r'var\s+ct\s*=\s*["\']?(\d{10})["\']?', html_text)
        if ct_match:
            try:
                ts = int(ct_match.group(1))
                pub_date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            except Exception:
                pass
        else:
            # Match publish_time (var publish_time = "2025-06-20")
            pt_match = re.search(r'var\s+publish_time\s*=\s*["\'](\d{4}-\d{2}-\d{2})["\']', html_text)
            if pt_match:
                pub_date = pt_match.group(1)

        # 4. Cover Image
        cover_image = "resource/images/ban_txt.png"
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            raw_cover_url = og_image["content"].strip()
            if download_images and raw_cover_url:
                cover_image = download_wechat_image(raw_cover_url)
            elif raw_cover_url:
                cover_image = raw_cover_url

        # 5. Description / Digest
        desc = ""
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            desc = og_desc["content"].strip()
        if not desc:
            desc = f"美尔健（深圳）生物科技有限公司微信公众号发布文章：{title}"

        # 6. Sanitize Content
        content = process_wechat_html_content(html_text, download_images=download_images)

        # Generate unique ID
        title_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:8]
        article_id = f"wx_{title_hash}"

        return {
            "id": article_id,
            "title": title,
            "author": author,
            "category": "新闻资讯",
            "image": cover_image,
            "desc": desc,
            "link": f"articles/{article_id}.html",
            "content": content,
            "date": pub_date,
            "source_url": url,
            "recommend": False,
            "top": False,
            "show": True,
            "sort": 50
        }
    except Exception as e:
        print(f"[-] Scrape article error for {url}: {e}")
        return None

# ==============================================================================
# Mode B: WeChat Official API Sync (freepublish/batchget)
# ==============================================================================
class WeChatOfficialSync:
    def __init__(self, appid, appsecret):
        self.appid = appid.strip()
        self.appsecret = appsecret.strip()
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self):
        now = time.time()
        if self.access_token and now < self.token_expires_at - 180:
            return self.access_token

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "access_token" in data:
                self.access_token = data["access_token"]
                self.token_expires_at = now + data.get("expires_in", 7200)
                return self.access_token
            else:
                errcode = data.get("errcode")
                errmsg = data.get("errmsg", "")
                if errcode == 40164:
                    ip_match = re.search(r'invalid ip\s+([\d\.]+)', errmsg)
                    detected_ip = ip_match.group(1) if ip_match else "当前外网IP"
                    raise Exception(f"微信公众平台限制：未配置IP白名单！微信检测到的出口IP为【{detected_ip}】。请登录微信公众平台(mp.weixin.qq.com) -> 设置与开发 -> 基本配置 -> IP白名单，将【{detected_ip}】添加进去后即可立即同步！")
                raise Exception(f"微信 Token 获取失败 [{errcode}]: {errmsg}")
        except Exception as e:
            raise Exception(f"{e}")

    def fetch_all_published_articles(self, download_images=True, default_category="新闻资讯"):
        """
        Retrieves all articles by querying:
        1. Material API (material/batchget_material) - Permanent news materials
        2. Draft API (draft/batchget) - Draft news items
        3. FreePublish API (freepublish/batchget) - If authorized
        4. Self-Menu API (get_current_selfmenu_info) - Articles attached in menu
        Deduplicates by title and content hash.
        """
        token = self.get_access_token()
        all_articles = []
        seen_titles = set()

        update_sync_state(log="微信凭证认证通过，启动全渠道图文抓取引擎...")

        # ---------------------------------------------------------
        # Helper: parse news item into standard dict
        # ---------------------------------------------------------
        def parse_news_dict(news, pub_date, source_url=""):
            title = news.get("title", "").strip()
            if not title:
                return None
            if title in seen_titles:
                return None
            seen_titles.add(title)

            author = news.get("author", "美尔健生物").strip() or "美尔健生物"
            digest = news.get("digest", "").strip() or f"美尔健（深圳）生物科技有限公司：{title}"
            thumb_url = news.get("thumb_url") or news.get("cover_url") or ""
            raw_content = news.get("content", "")
            article_source_url = news.get("url") or news.get("content_url") or source_url

            cover_image = "resource/images/ban_txt.png"
            if thumb_url:
                if download_images:
                    cover_image = download_wechat_image(thumb_url)
                else:
                    cover_image = thumb_url

            clean_content = process_wechat_html_content(raw_content, download_images=download_images)
            title_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:8]
            article_id = f"wx_{title_hash}"

            return {
                "id": article_id,
                "title": title,
                "author": author,
                "category": default_category,
                "image": cover_image,
                "desc": digest,
                "link": f"articles/{article_id}.html",
                "content": clean_content,
                "date": pub_date,
                "source_url": article_source_url,
                "recommend": False,
                "top": False,
                "show": True,
                "sort": 50
            }

        # ---------------------------------------------------------
        # Channel 1: Material Library (永久图文素材库)
        # ---------------------------------------------------------
        update_sync_state(log="[1/4] 正在扫描微信公众号永久素材图文库 (material)...")
        mat_offset = 0
        mat_count = 20
        while True:
            try:
                resp = requests.post(
                    f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}",
                    json={"type": "news", "offset": mat_offset, "count": mat_count},
                    timeout=20
                )
                data = resp.json()
            except Exception as e:
                update_sync_state(log=f"[-] 素材库请求异常: {e}")
                break

            if "errcode" in data and data["errcode"] != 0:
                update_sync_state(log=f"[-] 素材库返回 [{data.get('errcode')}]: {data.get('errmsg')}")
                break

            items = data.get("item", [])
            total_count = data.get("total_count", 0)
            item_count = data.get("item_count", len(items))

            if not items:
                break

            for item in items:
                update_time = item.get("update_time", int(time.time()))
                pub_date = datetime.datetime.fromtimestamp(update_time).strftime("%Y-%m-%d")
                news_list = item.get("content", {}).get("news_item", [])
                for news in news_list:
                    parsed = parse_news_dict(news, pub_date)
                    if parsed:
                        all_articles.append(parsed)
                        update_sync_state(log=f"  + 素材库获取: 《{parsed['title']}》 ({parsed['date']})")

            mat_offset += item_count
            if mat_offset >= total_count:
                break
            time.sleep(0.3)

        # ---------------------------------------------------------
        # Channel 2: Draft Library (草稿/文章库)
        # ---------------------------------------------------------
        update_sync_state(log="[2/4] 正在扫描微信公众号草稿与图文库 (draft)...")
        draft_offset = 0
        draft_count = 20
        while True:
            try:
                resp = requests.post(
                    f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}",
                    json={"offset": draft_offset, "count": draft_count, "no_content": 0},
                    timeout=20
                )
                data = resp.json()
            except Exception as e:
                update_sync_state(log=f"[-] 草稿库请求异常: {e}")
                break

            if "errcode" in data and data["errcode"] != 0:
                update_sync_state(log=f"[-] 草稿库返回 [{data.get('errcode')}]: {data.get('errmsg')}")
                break

            items = data.get("item", [])
            total_count = data.get("total_count", 0)
            item_count = data.get("item_count", len(items))

            if not items:
                break

            for item in items:
                update_time = item.get("update_time", int(time.time()))
                pub_date = datetime.datetime.fromtimestamp(update_time).strftime("%Y-%m-%d")
                news_list = item.get("content", {}).get("news_item", [])
                for news in news_list:
                    parsed = parse_news_dict(news, pub_date)
                    if parsed:
                        all_articles.append(parsed)
                        update_sync_state(log=f"  + 图文草稿库获取: 《{parsed['title']}》 ({parsed['date']})")

            draft_offset += item_count
            if draft_offset >= total_count:
                break
            time.sleep(0.3)

        # ---------------------------------------------------------
        # Channel 3: FreePublish API (已发表群发图文)
        # ---------------------------------------------------------
        update_sync_state(log="[3/4] 正在检测已群发图文库 (freepublish)...")
        fp_offset = 0
        fp_count = 20
        while True:
            try:
                resp = requests.post(
                    f"https://api.weixin.qq.com/cgi-bin/freepublish/batchget?access_token={token}",
                    json={"offset": fp_offset, "count": fp_count, "no_content": 0},
                    timeout=20
                )
                data = resp.json()
            except Exception:
                break

            if "errcode" in data and data["errcode"] != 0:
                # If unauthorized or not open, quietly skip
                break

            items = data.get("item", [])
            total_count = data.get("total_count", 0)
            item_count = data.get("item_count", len(items))

            if not items:
                break

            for item in items:
                update_time = item.get("update_time", int(time.time()))
                pub_date = datetime.datetime.fromtimestamp(update_time).strftime("%Y-%m-%d")
                news_list = item.get("content", {}).get("news_item", [])
                for news in news_list:
                    parsed = parse_news_dict(news, pub_date)
                    if parsed:
                        all_articles.append(parsed)
                        update_sync_state(log=f"  + 已群发库获取: 《{parsed['title']}》 ({parsed['date']})")

            fp_offset += item_count
            if fp_offset >= total_count:
                break
            time.sleep(0.3)

        # ---------------------------------------------------------
        # Channel 4: Self-Menu Attached Articles (自定义菜单文章)
        # ---------------------------------------------------------
        update_sync_state(log="[4/4] 正在扫描公众号自定义菜单图文链接...")
        try:
            m_resp = requests.get(
                f"https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token={token}",
                timeout=15
            )
            m_data = m_resp.json()
            buttons = m_data.get("selfmenu_info", {}).get("button", [])
            
            def extract_menu_news(btn_list):
                for b in btn_list:
                    if "sub_button" in b and "list" in b["sub_button"]:
                        extract_menu_news(b["sub_button"]["list"])
                    
                    # If button has news_info
                    news_info = b.get("news_info", {}).get("list", [])
                    for n in news_info:
                        pub_date = datetime.datetime.now().strftime("%Y-%m-%d")
                        parsed = parse_news_dict(n, pub_date)
                        if parsed:
                            # If content is empty in menu, scrape directly from content_url
                            if len(parsed.get("content", "")) < 200 and parsed.get("source_url"):
                                scraped = scrape_wechat_article_by_url(parsed["source_url"], download_images=download_images)
                                if scraped and len(scraped.get("content", "")) > 100:
                                    parsed["content"] = scraped["content"]
                                    if scraped.get("date"):
                                        parsed["date"] = scraped["date"]
                            all_articles.append(parsed)
                            update_sync_state(log=f"  + 自定义菜单获取: 《{parsed['title']}》")

                    # If button is view url and links to mp.weixin.qq.com
                    url = b.get("url", "")
                    if url and "mp.weixin.qq.com" in url:
                        scraped = scrape_wechat_article_by_url(url, download_images=download_images)
                        if scraped and scraped["title"] not in seen_titles:
                            seen_titles.add(scraped["title"])
                            all_articles.append(scraped)
                            update_sync_state(log=f"  + 自定义菜单链接解析: 《{scraped['title']}》")

            extract_menu_news(buttons)
        except Exception as e:
            update_sync_state(log=f"[-] 扫描自定义菜单异常: {e}")

        update_sync_state(log=f"全渠道抓取汇总完成，共解析出 {len(all_articles)} 篇高质量图文！")
        return all_articles

# ==============================================================================
# Database Integration & Site Rebuilding
# ==============================================================================
def integrate_articles_into_cms(crawled_articles, trigger_name="manual"):
    """
    Saves new crawled articles into cms_data/articles.json, skips duplicates.
    Triggers generator.publish_site() to compile static pages.
    """
    articles_file = os.path.join(DATA_DIR, "articles.json")
    existing_articles = []
    if os.path.exists(articles_file):
        try:
            with open(articles_file, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
        except Exception as e:
            print(f"[-] Error loading articles.json: {e}")

    existing_titles = {a.get("title", "").strip() for a in existing_articles}
    existing_ids = {a.get("id") for a in existing_articles}

    added_count = 0
    skipped_count = 0

    for article in crawled_articles:
        t = article.get("title", "").strip()
        aid = article.get("id")
        if t in existing_titles or aid in existing_ids:
            skipped_count += 1
            continue

        existing_articles.insert(0, article)
        existing_titles.add(t)
        existing_ids.add(aid)
        added_count += 1

    if added_count > 0:
        try:
            with open(articles_file, "w", encoding="utf-8") as f:
                json.dump(existing_articles, f, ensure_ascii=False, indent=2)
            update_sync_state(log=f"成功将 {added_count} 篇新文章入库 articles.json，正在重新编译静态页面...")
            
            # Trigger generator
            try:
                sys.path.insert(0, os.path.join(WORKSPACE_DIR, "cms_system"))
                import generator
                generator.generate_sitemap()
                threading.Thread(target=generator.publish_site, daemon=True).start()
                update_sync_state(log="静态网站已触发增量更新，包含最新微信文章！")
            except Exception as e:
                update_sync_state(log=f"[-] 网站静态页面重新编译警告: {e}")

        except Exception as e:
            update_sync_state(log=f"[-] 保存 articles.json 失败: {e}")
            return False, added_count, skipped_count
    else:
        update_sync_state(log="全部文章均为最新，未发现新增内容。")

    # Update config stats
    cfg = load_wechat_config()
    cfg["last_sync_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cfg["last_sync_status"] = f"同步完成 (新增 {added_count} 篇, 跳过 {skipped_count} 篇)"
    cfg["total_synced"] = cfg.get("total_synced", 0) + added_count
    save_wechat_config(cfg)

    return True, added_count, skipped_count

# ==============================================================================
# Public Sync Execution Pipelines
# ==============================================================================
def start_official_api_sync_thread(trigger="manual"):
    """Runs the official API sync pipeline in a background thread."""
    if get_sync_state()["is_running"]:
        return False, "已有同步任务正在运行中，请稍候。"

    def runner():
        update_sync_state(
            is_running=True,
            task_id=str(uuid.uuid4())[:8],
            trigger=trigger,
            status="running",
            message="正在同步美尔健微信公众号内容...",
            progress=5,
            total=0,
            current=0,
            added=0,
            skipped=0,
            failed=0,
            logs=[]
        )
        try:
            cfg = load_wechat_config()
            appid = cfg.get("appid", "").strip()
            appsecret = cfg.get("appsecret", "").strip()

            if not appid or not appsecret:
                update_sync_state(
                    is_running=False,
                    status="error",
                    message="未配置微信公众号 AppID 或 AppSecret，请先在配置面板填写！",
                    log="错误：缺少微信公众号 AppID / AppSecret"
                )
                return

            update_sync_state(log=f"启动微信官方同步引擎，连接公众号: {cfg.get('account_name', '美尔健生物')}...")
            syncer = WeChatOfficialSync(appid, appsecret)
            articles = syncer.fetch_all_published_articles(
                download_images=cfg.get("download_images", True),
                default_category=cfg.get("default_category", "新闻资讯")
            )

            update_sync_state(log=f"共拉取到 {len(articles)} 篇图文消息，准备入库...")
            success, added, skipped = integrate_articles_into_cms(articles, trigger_name=trigger)

            update_sync_state(
                is_running=False,
                status="completed",
                progress=100,
                added=added,
                skipped=skipped,
                message=f"同步完成！新增 {added} 篇，跳过已有 {skipped} 篇。",
                log=f"公众号内容抓取同步圆满完成！新增 {added} 篇，跳过 {skipped} 篇。"
            )
        except Exception as e:
            update_sync_state(
                is_running=False,
                status="error",
                message=f"同步中断: {e}",
                log=f"[-] 同步发生异常: {e}"
            )

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    return True, "微信公众号同步任务已启动。"

def start_urls_batch_sync_thread(urls, default_category=None, trigger="urls_batch"):
    """Scrapes a list of article URLs in background."""
    if get_sync_state()["is_running"]:
        return False, "已有同步任务正在运行中，请稍候。"

    def runner():
        cfg = load_wechat_config()
        cat = default_category or cfg.get("default_category", "新闻资讯")
        download_imgs = cfg.get("download_images", True)

        cleaned_urls = []
        for u in urls:
            u = u.strip()
            if u.startswith("http") and "weixin.qq.com" in u:
                cleaned_urls.append(u)

        if not cleaned_urls:
            update_sync_state(
                is_running=False,
                status="error",
                message="未检测到有效的微信公众号文章链接！",
                log="错误：提供的链接不是有效的微信公众号文章 URL。"
            )
            return

        update_sync_state(
            is_running=True,
            task_id=str(uuid.uuid4())[:8],
            trigger=trigger,
            status="running",
            message=f"正在抓取 {len(cleaned_urls)} 篇微信文章...",
            progress=10,
            total=len(cleaned_urls),
            current=0,
            added=0,
            skipped=0,
            failed=0,
            logs=[]
        )

        parsed_articles = []
        failed_count = 0
        for idx, u in enumerate(cleaned_urls):
            update_sync_state(
                current=idx + 1,
                progress=int(10 + (idx / len(cleaned_urls)) * 80),
                log=f"正在抓取并解析第 {idx + 1}/{len(cleaned_urls)} 篇: {u[:45]}..."
            )
            art = scrape_wechat_article_by_url(u, download_images=download_imgs)
            if art:
                art["category"] = cat
                parsed_articles.append(art)
                update_sync_state(log=f"成功抓取: 《{art['title']}》 ({art['date']})")
            else:
                failed_count += 1
                update_sync_state(log=f"[-] 抓取解析失败: {u}")
            time.sleep(0.8)

        update_sync_state(log=f"抓取完毕，解析成功 {len(parsed_articles)} 篇，失败 {failed_count} 篇。正在入库...")
        success, added, skipped = integrate_articles_into_cms(parsed_articles, trigger_name=trigger)

        update_sync_state(
            is_running=False,
            status="completed",
            progress=100,
            added=added,
            skipped=skipped,
            failed=failed_count,
            message=f"导入抓取完成！新增 {added} 篇，跳过 {skipped} 篇，失败 {failed_count} 篇。",
            log=f"微信文章批量抓取完成！新增 {added} 篇，跳过 {skipped} 篇。"
        )

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    return True, f"已开始后台批量抓取 {len(urls)} 篇微信文章。"
