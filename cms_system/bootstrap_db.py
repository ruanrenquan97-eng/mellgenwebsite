import os
import re
import json
from urllib.parse import unquote

WORKSPACE_DIR = r"d:\Administrator\webapp\美尔健官网"
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")

os.makedirs(DATA_DIR, exist_ok=True)

# Helper: clean HTML tag text
def clean_text(html):
    return re.sub(r'<[^>]+>', '', html).strip()

def bootstrap_products():
    print("[*] Bootstrapping products database...")
    # List of categories and their corresponding HTML listing files
    list_files = {
        "化妆品原料": "product_hzpyl.html",
        "医用原料": "product_yyyl.html",
        "食品营养原料": "product_spyyyl.html",
    }
    
    products = []
    seen_links = set()
    
    for category, filename in list_files.items():
        file_path = os.path.join(WORKSPACE_DIR, filename)
        if not os.path.exists(file_path):
            print(f"[-] Category file not found: {filename}")
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
            
        # Extract product blocks: <dl> ... </dl> inside the product list area
        dl_pattern = r'<dl>\s*<dt>\s*<a href=["\']([^"\']+)["\'][^>]*><img alt=["\']([^"\']+)["\'] src=["\']([^"\']+)["\'][^>]*></a>\s*</dt>\s*<dd>\s*<h4><a[^>]*>([^<]+)</a></h4>\s*<p>(.*?)</p>\s*</dd>\s*</dl>'
        matches = re.findall(dl_pattern, html, re.DOTALL)
        
        for link, alt, img, title, desc in matches:
            # Clean link: remove leading ./ if any
            clean_link = link.lstrip('./')
            if clean_link in seen_links:
                continue
                
            seen_links.add(clean_link)
            
            # Extract content from detail page
            detail_path = os.path.join(WORKSPACE_DIR, clean_link.replace('/', os.sep))
            content_html = ""
            specs = {}
            
            if os.path.exists(detail_path):
                with open(detail_path, "r", encoding="utf-8") as df:
                    detail_html = df.read()
                    
                # 1. Extract content inside `<div class="p102-pro-content-desc endit-content">`
                content_match = re.search(r'<div class="p102-pro-content-desc endit-content">(.*?)</div>\s*<!--', detail_html, re.DOTALL)
                if not content_match:
                    content_match = re.search(r'<div class="p102-pro-content-desc endit-content">(.*?)</div>\s*</div>\s*</div>\s*</div>\s*<!--', detail_html, re.DOTALL)
                if not content_match:
                    content_match = re.search(r'<div class="p102-pro-content-desc endit-content">(.*?)</div>\s*</div>\s*</div>\s*<div class="p102-pro-content">', detail_html, re.DOTALL)
                if not content_match:
                    content_match = re.search(r'<div class="p102-pro-content-desc endit-content">(.*?)</div>', detail_html, re.DOTALL)
                    
                if content_match:
                    content_html = content_match.group(1).strip()
                    
                # 2. Extract top specs (INCI, etc.) - usually in <div class="p102-proShow-1-para">
                spec_pattern = r'<p>\s*(.*?)[：:]\s*(.*?)\s*</p>'
                spec_matches = re.findall(spec_pattern, detail_html)
                for name, value in spec_matches:
                    clean_name = clean_text(name)
                    clean_val = clean_text(value)
                    if clean_name and clean_name not in ["您当前的位置", "主营产品"]:
                        specs[clean_name] = clean_val
                        
            # Normalize description
            clean_desc = clean_text(desc).replace("详情>", "").replace("详情&gt;", "").strip()
            
            product_id = os.path.splitext(os.path.basename(clean_link))[0]
            
            products.append({
                "id": product_id,
                "title": title.strip(),
                "category": category,
                "image": img.lstrip('./'),
                "desc": clean_desc,
                "link": clean_link,
                "content": content_html,
                "specs": specs
            })
            
    with open(os.path.join(DATA_DIR, "products.json"), "w", encoding="utf-8") as pf:
        json.dump(products, pf, ensure_ascii=False, indent=2)
        
    print(f"[OK] Extracted {len(products)} products and saved to products.json")


def bootstrap_articles():
    print("[*] Bootstrapping articles database...")
    # List of categories and their corresponding HTML listing files
    list_files = {
        "新闻资讯": "article_xwzx.html",
        "合作案例": "article_hzal.html",
        "常见问答": "article_cjwt.html",
        "企业新闻": "article_qydt.html",
        "技术知识": "article_cpbk.html",
    }
    
    articles = []
    seen_links = set()
    
    for category, filename in list_files.items():
        file_path = os.path.join(WORKSPACE_DIR, filename)
        if not os.path.exists(file_path):
            print(f"[-] Category file not found: {filename}")
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
            
        # Extract article blocks from listing files
        dl_pattern = r'<dl>\s*<dt>\s*<a href=["\']([^"\']+)["\'][^>]*><img alt=["\']([^"\']+)["\'] src=["\']([^"\']+)["\'][^>]*></a>\s*</dt>\s*<dd>\s*<h4><a href=["\']([^"\']+)["\'][^>]*>([^<]+)</a></h4>\s*<div class="p102-info-list-desc">(.*?)</div>'
        matches = re.findall(dl_pattern, html, re.DOTALL)
        
        for link, alt, img, link2, title, desc in matches:
            clean_link = link.lstrip('./')
            if clean_link in seen_links:
                continue
                
            seen_links.add(clean_link)
            
            # Read article detail page
            detail_path = os.path.join(WORKSPACE_DIR, clean_link.replace('/', os.sep))
            content_html = ""
            date_str = ""
            
            if os.path.exists(detail_path):
                with open(detail_path, "r", encoding="utf-8") as df:
                    detail_html = df.read()
                    
                content_match = re.search(r'<div class="p102-info-content-desc">(.*?)</div>\s*<div class="p102-info-key">', detail_html, re.DOTALL)
                if not content_match:
                    content_match = re.search(r'<div class="p102-info-content-desc">(.*?)</div>\s*</div>\s*<div class="p102-info-key">', detail_html, re.DOTALL)
                if not content_match:
                    content_match = re.search(r'<div class="p102-info-content-desc">(.*?)</div>', detail_html, re.DOTALL)
                    
                if content_match:
                    content_html = content_match.group(1).strip()
                    
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', detail_html)
                if date_match:
                    date_str = date_match.group(1)
            
            if not date_str:
                link_pos = html.find(clean_link)
                if link_pos != -1:
                    chunk = html[link_pos:link_pos+1000]
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', chunk)
                    if date_match:
                        date_str = date_match.group(1)
            
            if not date_str:
                date_str = "2025-07-02"
                
            article_id = os.path.splitext(os.path.basename(clean_link))[0]
            
            articles.append({
                "id": article_id,
                "title": title.strip(),
                "category": category,
                "image": img.lstrip('./'),
                "desc": clean_text(desc).strip(),
                "link": clean_link,
                "content": content_html,
                "date": date_str
            })
            
    with open(os.path.join(DATA_DIR, "articles.json"), "w", encoding="utf-8") as af:
        json.dump(articles, af, ensure_ascii=False, indent=2)
        
    print(f"[OK] Extracted {len(articles)} articles and saved to articles.json")


def bootstrap_settings():
    print("[*] Bootstrapping settings...")
    settings_path = os.path.join(DATA_DIR, "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = {}
        
    settings.update({
        "company_name": "美尔健（深圳）生物科技有限公司",
        "phone": "186-9197-8530 / 0755-82926499",
        "email": "61791579@qq.com",
        "address": "广东省深圳市大鹏新区葵涌街道生命科学产业园",
        "qq": "61791579",
        "seo_title": "美尔健生物|医用原料-化妆品原料-食品营养原料",
        "seo_keywords": "医用原料,化妆品原料,食品营养原料",
        "seo_description": "医用原料,化妆品原料,食品营养原料提供商，美尔健生物拥有来自各大科研院所的高效透皮肽技术。"
    })
    
    # Extract Banners from index.html if not already present
    if not settings.get("banners"):
        settings["banners"] = []
        index_path = os.path.join(WORKSPACE_DIR, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                html = f.read()
                
            slide_pattern = r'<div class="swiper-slide"[^>]*>\s*<a href=["\']([^"\']+)["\'][^>]*><img alt=["\']([^"\']+)["\'] src=["\']([^"\']+)["\'][^>]*></a>\s*</div>'
            slides = re.findall(slide_pattern, html)
            for link, title, img in slides:
                settings["banners"].append({
                    "type": "image",
                    "link": link.lstrip('./'),
                    "title": title,
                    "image": img.lstrip('./')
                })
                
            # Also look for video slide
            video_match = re.search(r'<video[^>]*>.*?<source src=["\']([^"\']+)["\']', html, re.DOTALL)
            if video_match:
                settings["banners"].insert(0, {
                    "type": "video",
                    "link": "",
                    "title": "透皮肽技术视频",
                    "video": video_match.group(1),
                    "image": "images/ban_txt.png"
                })
        
    # Make sure we preserve the accounts we created
    if "accounts" not in settings:
        settings["accounts"] = [
            {"username": "admin", "password": "admin123", "role": "管理员", "name": "系统管理员"},
            {"username": "kefu", "password": "kefu888", "role": "客服", "name": "在线客服"}
        ]
        
    with open(settings_path, "w", encoding="utf-8") as sf:
        json.dump(settings, sf, ensure_ascii=False, indent=2)
        
    print("[OK] Updated settings.json")

def main():
    bootstrap_products()
    bootstrap_articles()
    bootstrap_settings()
    print("[*] Database bootstrap complete!")

if __name__ == "__main__":
    main()
