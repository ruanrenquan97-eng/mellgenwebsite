import os
import re
import json
import shutil
from urllib.parse import urlparse

WORKSPACE_DIR = r"d:\Administrator\webapp\美尔健官网"
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")

def load_db():
    products_path = os.path.join(DATA_DIR, "products.json")
    articles_path = os.path.join(DATA_DIR, "articles.json")
    settings_path = os.path.join(DATA_DIR, "settings.json")
    friendlinks_path = os.path.join(DATA_DIR, "friendlinks.json")
    nav_path = os.path.join(DATA_DIR, "nav.json")
    
    products = []
    articles = []
    settings = {}
    friendlinks = []
    nav_links = []
    
    if os.path.exists(products_path):
        with open(products_path, "r", encoding="utf-8") as f:
            products = json.load(f)
    if os.path.exists(articles_path):
        with open(articles_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    if os.path.exists(friendlinks_path):
        with open(friendlinks_path, "r", encoding="utf-8") as f:
            friendlinks = json.load(f)
    if os.path.exists(nav_path):
        with open(nav_path, "r", encoding="utf-8") as f:
            nav_links = json.load(f)
            
    return products, articles, settings, friendlinks, nav_links

# Helper: safe replacement using string slicing to avoid regex group reference errors
def replace_group(pattern, replacement, html, group_index=2, flags=re.DOTALL):
    match = re.search(pattern, html, flags)
    if match:
        start = match.start(group_index)
        end = match.end(group_index)
        return html[:start] + replacement + html[end:]
    return html

def get_product_subcategories(category):
    if category == "化妆品原料":
        return ["化妆品原料", "透皮型重组蛋白/多肽", "重组仿生蛋白", "植物源活性物", "海洋源活性物", "婴儿菌发酵源活性物"]
    elif category == "医用原料":
        return ["医用原料", "重组蛋白", "动物源活性物", "活性抗菌材料"]
    elif category == "食品营养原料":
        return ["食品营养原料", "桃胶多糖", "水母胶原", "灵芝黄酮", "灵芝多糖", "人参多肽", "复合营养素", "婴儿源益生菌"]
    return [category]

def get_article_subcategories(category):
    if category == "合作案例":
        return ["合作案例", "医美行业", "护肤品工厂", "化妆品", "医药行业", "功能类食品", "洗护用品", "女性护理产品"]
    elif category == "新闻资讯":
        return ["新闻资讯", "企业新闻", "技术知识", "常见问答"]
    return [category]


def update_global_contact_info(html_content, settings):
    html_content = html_content.replace("186-9197-8530 / 0755-82926499", settings.get("phone", ""))
    html_content = html_content.replace("186-9197-8530&nbsp;&nbsp;&nbsp;0755-82926499", settings.get("phone", "").replace(" / ", "&nbsp;&nbsp;&nbsp;"))
    html_content = html_content.replace("0755-82926499", settings.get("phone", "").split(" / ")[-1])
    
    html_content = html_content.replace("广东省深圳市大鹏新区葵涌街道生命科学产业园", settings.get("address", ""))
    html_content = html_content.replace("地址：广东省深圳市大鹏新区葵涌街道生命科学产业园", "地址：" + settings.get("address", ""))
    
    html_content = html_content.replace("61791579@qq.com", settings.get("email", ""))
    html_content = html_content.replace("邮箱：61791579@qq.com", "邮箱：" + settings.get("email", ""))
    
    html_content = html_content.replace("61791579", settings.get("qq", ""))
    
    return html_content

def update_friendlinks(html_content, friendlinks):
    links_html = ""
    for fl in friendlinks:
        if fl.get("show", True):
            links_html += f'<a href="{fl["url"]}" title="{fl["name"]}">{fl["name"]}</a> '
    
    # Replace content inside <div class="link_c"> <li lastclass="lasta"> ... </li> </div>
    html_content = replace_group(r'(<div class="link_c">\s*<li[^>]*>)(.*?)(</li>\s*</div>)', links_html, html_content)
    return html_content

def update_navigation(html_content, nav_links, file_rel_path):
    if not nav_links:
        return html_content
        
    # Determine directory depth relative to workspace root
    depth = len(file_rel_path.replace("\\", "/").split("/")) - 1
    prefix = "../" * depth
    if not prefix:
        prefix = "./"
        
    nav_html = "\n"
    # Flatten the tree structure to flat <li> items to fit Mellgen's style safely
    def process_item(item):
        nonlocal nav_html
        url = item.get("url", "")
        # Resolve prefix
        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("//") or url.startswith("/")):
            url = prefix + url.lstrip("./")
        nav_html += f'     <li> <a href="{url}" title="{item["name"]}"> {item["name"]} </a> </li> \n'
        
        # If there are children, render them sequentially to keep it flat but fully present
        for child in item.get("children", []):
            child_url = child.get("url", "")
            if not (child_url.startswith("http://") or child_url.startswith("https://") or child_url.startswith("//") or child_url.startswith("/")):
                child_url = prefix + child_url.lstrip("./")
            nav_html += f'     <li> <a href="{child_url}" title="{child["name"]}"> &nbsp;&nbsp;├ {child["name"]} </a> </li> \n'

    for item in nav_links:
        process_item(item)
        
    nav_html += "   "
    
    pattern = r'(<div class="[^"]*menu[^"]*">.*?<ul>)(.*?)(</ul>)'
    if re.search(pattern, html_content, re.DOTALL):
        html_content = replace_group(pattern, nav_html, html_content, group_index=2)
    return html_content

def generate_product_detail_page(product, base_template_html, settings, nav_links):
    html = base_template_html
    
    seo_title = product.get("seoTitle") or f"{product['title']}-产品中心-{settings.get('company_name', '美尔健生物')}"
    html = re.sub(r'<title>[^<]+</title>', f"<title>{seo_title}</title>", html)
    
    seo_keywords = product.get("seoKeywords")
    if seo_keywords:
        if re.search(r'<meta[^>]+name=["\']keywords["\']', html, re.I):
            html = re.sub(r'(<meta[^>]+name=["\']keywords["\'][^>]+content=["\'])(.*?)(["\'])', f'\\1{seo_keywords}\\3', html, flags=re.I)
        else:
            html = re.sub(r'(<title>[^<]+</title>)', f'\\1\n  <meta name="keywords" content="{seo_keywords}">', html, flags=re.I)
            
    seo_desc = product.get("seoDesc") or product.get("desc")
    if seo_desc:
        if re.search(r'<meta[^>]+name=["\']description["\']', html, re.I):
            html = re.sub(r'(<meta[^>]+name=["\']description["\'][^>]+content=["\'])(.*?)(["\'])', f'\\1{seo_desc}\\3', html, flags=re.I)
        else:
            html = re.sub(r'(<title>[^<]+</title>)', f'\\1\n  <meta name="description" content="{seo_desc}">', html, flags=re.I)
    
    cat = product['category']
    cat_filename = "product_hzpyl.html"
    if cat in ["医用原料", "重组蛋白", "动物源活性物", "活性抗菌材料"]:
        cat_filename = "product_yyyl.html"
    elif cat in ["食品营养原料", "桃胶多糖", "水母胶原", "灵芝黄酮", "灵芝多糖", "人参多肽", "复合营养素", "婴儿源益生菌"]:
        cat_filename = "product_spyyyl.html"
        
    crumbs_pattern = r'(<b>您当前的位置：</b>\s*<a href="\.\./index\.html"[^>]*>\s*首页\s*</a>\s*<span> &gt; </span>\s*<i[^>]*>\s*<a href="\.\./product_index\.html"[^>]*>\s*产品频道\s*</a>\s*<span> &gt; </span>\s*</i>\s*<i[^>]*>\s*<a href="\.\./)([^"]+)("[^>]*>)([^<]+)(</a>)'
    match = re.search(crumbs_pattern, html)
    if match:
        html = (
            html[:match.start(2)] + cat_filename +
            html[match.end(2):match.start(4)] + product["category"] +
            html[match.end(4):]
        )
    
    html = replace_group(r'(<div class="p102-proShow-1-para">.*?<h2>)(.*?)(</h2>)', product["title"], html)
    
    specs_html = "\n"
    for name, value in product.get("specs", {}).items():
        specs_html += f"      <p> {name}：{value} </p>\n"
    specs_html += "     "
    html = replace_group(r'(<div class="p102-proShow-1-para-text">)(.*?)(</div>)', specs_html, html)
    
    img_pattern = r'(<div class="p102-proShow-1-pic">.*?<img alt=")(.*?)(" src=")(.*?)(")'
    match = re.search(img_pattern, html, re.DOTALL)
    if match:
        html = (
            html[:match.start(2)] + product["title"] +
            html[match.end(2):match.start(4)] + f"../{product['image']}" +
            html[match.end(4):]
        )
    
    html = replace_group(r'(<div class="p102-pro-content-desc endit-content">)(.*?)(</div>\s*<!--)', f"\n     {product['content']}\n    ", html)
    
    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, product['link'])
    
    dest_path = os.path.join(WORKSPACE_DIR, product['link'].replace('/', os.sep))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)

def generate_article_detail_page(article, base_template_html, settings, nav_links):
    html = base_template_html
    
    html = re.sub(r'<title>[^<]+</title>', f"<title>{article['title']}-新闻资讯-{settings.get('company_name', '美尔健生物')}</title>", html)
    
    cat_filename = "article_xwzx.html"
    cat = article['category']
    if cat in ["合作案例", "医美行业", "护肤品工厂", "化妆品", "医药行业", "功能类食品", "洗护用品", "女性护理产品"]:
        cat_filename = "article_hzal.html"
    elif cat in ["常见问答"]:
        cat_filename = "article_cjwt.html"
    elif cat in ["企业新闻"]:
        cat_filename = "article_qydt.html"
    elif cat in ["技术知识"]:
        cat_filename = "article_cpbk.html"
        
    crumbs_pattern = r'(<b>您当前的位置：</b>\s*<a href="\.\./index\.html"[^>]*>\s*首页\s*</a>\s*<span> &gt; </span>\s*<i[^>]*>\s*<a href="\.\./)([^"]+)("[^>]*>)([^<]+)(</a>)'
    match = re.search(crumbs_pattern, html)
    if match:
        html = (
            html[:match.start(2)] + cat_filename +
            html[match.end(2):match.start(4)] + article["category"] +
            html[match.end(4):]
        )
    
    html = replace_group(r'(<h1[^>]*>)(.*?)(</h1>)', article["title"], html)
    
    html = replace_group(r'(<span class="p102-info-date">)(.*?)(</span>)', article["date"], html, flags=0)
    
    html = replace_group(r'(<div class="p102-info-content-desc">)(.*?)(</div>\s*<div class="p102-info-key">)', f"\n     {article['content']}\n    ", html)
    
    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, article['link'])
    
    dest_path = os.path.join(WORKSPACE_DIR, article['link'].replace('/', os.sep))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_product_listing_page(file_path, category, products, settings, nav_links):
    if not os.path.exists(file_path):
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    subcats = get_product_subcategories(category)
    cat_products = [p for p in products if p['category'] in subcats]
    
    list_html = "\n"
    for i, p in enumerate(cat_products):
        detail_link = "./" + p["link"]
        image_path = "./" + p["image"]
        list_html += f"""    <dl> 
     <dt> 
      <a href="{detail_link}" target="_blank" title="{p['title']}"><img alt="{p['title']}" src="{image_path}"></a> 
     </dt> 
     <dd> 
      <h4><a href="{detail_link}" target="_blank" title="{p['title']}">{p['title']}</a></h4> 
      <p> {p['desc'][:80]}...<a href="{detail_link}" target="_blank" title="{p['title']}">详情&gt;</a> </p> 
     </dd> 
    </dl> 
"""
        if (i + 1) % 3 == 0 and (i + 1) < len(cat_products):
            list_html += "    <div class=\"clear\"></div>\n"
            
    list_html += "    "
    
    html = replace_group(r'(<div class="hyt-product-list-6">)(.*?)(<div class="clear"></div>\s*</div>)', list_html, html)
        
    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
    html = update_navigation(html, nav_links, rel_path)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_article_listing_page(file_path, category, articles, settings, nav_links):
    if not os.path.exists(file_path):
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    subcats = get_article_subcategories(category)
    cat_articles = [a for a in articles if a['category'] in subcats]
    
    list_html = "\n"
    for a in cat_articles:
        detail_link = "./" + a["link"]
        image_path = "./" + a["image"]
        list_html += f"""   <dl> 
    <dt> 
     <a href="{detail_link}" target="_blank" title="{a['title']}"><img alt="{a['title']}" src="{image_path}" title="{a['title']}"></a> 
    </dt> 
    <dd> 
     <h4><a href="{detail_link}" target="_blank" title="{a['title']}">{a['title']}</a></h4> 
     <div class="p102-info-list-desc">
       {a['desc'][:100]}... 
     </div> 
     <div class="p102-info-list-more"> 
      <a href="{detail_link}" target="_blank" title="{a['title']}">详情 &gt;&gt;</a> 
     </div> 
    </dd> 
   </dl> 
"""
    list_html += "   "
    
    pattern = r'(<div class="p102-info-list">)(.*?)(</div>\s*<div class="p102-pagination-)'
    if not re.search(pattern, html, re.DOTALL):
        pattern = r'(<div class="p102-info-list">)(.*?)(</div>\s*<div class="clear"></div>\s*</div>\s*<div class="g_ft)'
        
    html = replace_group(pattern, list_html, html)
        
    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
    html = update_navigation(html, nav_links, rel_path)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_homepage(products, articles, settings, friendlinks, nav_links):
    index_path = os.path.join(WORKSPACE_DIR, "index.html")
    if not os.path.exists(index_path):
        return
        
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # 1. Update Banners
    banner_html = "\n"
    for b in settings.get("banners", []):
        if b["type"] == "video":
            banner_html += f"""    <div class="swiper-slide"> 
     <div class="ban_txt"> 
      <img src="./images/ban_txt.png"> 
     </div> 
     <video controls="" id="sVideo" loop="" muted> 
      <source src="{b['video']}" type="video/mp4"> 
     </video> 
    </div> 
"""
        else:
            banner_html += f"""     <div class="swiper-slide" data-swiper-autoplay="3000"> 
      <a href="./{b['link']}" title="{b['title']}"><img alt="{b['title']}" src="./{b['image']}" title="{b['title']}"></a> 
     </div> 
"""
    banner_html += "   "
    
    html = replace_group(r'(<div class="swiper-wrapper">)(.*?)(</div>\s*<div class="swiper-pagination">)', banner_html, html)
        
    # 2. Update Product Showcase (g_fa tabs)
    hzp = [p for p in products if p['category'] in get_product_subcategories("化妆品原料")][:5]
    yyy = [p for p in products if p['category'] in get_product_subcategories("医用原料")][:3]
    spy = [p for p in products if p['category'] in get_product_subcategories("食品营养原料")][:7]
    
    hzp_links = "\n         " + "\n          ".join([f'<a href="./{p["link"]}" title="{p["title"]}">{p["title"]} </a>' for p in hzp]) + "\n          "
    yyy_links = "\n         " + "\n          ".join([f'<a href="./{p["link"]}" title="{p["title"]}">{p["title"]} </a>' for p in yyy]) + "\n          "
    spy_links = "\n         " + "\n          ".join([f'<a href="./{p["link"]}" title="{p["title"]}">{p["title"]} </a>' for p in spy]) + "\n          "
    
    html = replace_group(r'(化妆品原料</a></h4>\s*<p>)(.*?)(</p>)', hzp_links, html)
    html = replace_group(r'(医用原料</a></h4>\s*<p>)(.*?)(</p>)', yyy_links, html)
    html = replace_group(r'(食品营养原料</a></h4>\s*<p>)(.*?)(</p>)', spy_links, html)
    
    # 3. Update case studies
    cases = [a for a in articles if a['category'] in get_article_subcategories("合作案例")][:10]
    case_list_html = "\n"
    for c in cases:
        case_list_html += f'      <li class="swiper-slide"><a href="./{c["link"]}" target="_blank" title="{c["title"]}"><i><img alt="{c["title"]}" src="./{c["image"]}" title="{c["title"]}"><span><img alt="" src="./images/anspico.png"></span></i><em>{c["title"]}</em></a></li> \n'
    case_list_html += "    "
    
    html = replace_group(r'(<ul class="f_cb swiper-wrapper">)(.*?)(</ul>\s*</div>\s*</div>\s*\n\s*</div>\s*<!-- 新闻资讯 -->)', case_list_html, html)
    
    # 4. Update News tabs
    qydt_news = [a for a in articles if a['category'] in get_article_subcategories("企业新闻")][:4]
    cpbk_news = [a for a in articles if a['category'] in get_article_subcategories("技术知识")][:4]
    cjwt_news = [a for a in articles if a['category'] in get_article_subcategories("常见问答")][:4]
    
    def make_news_tab_html(news_list):
        tab_html = "\n"
        for n in news_list:
            tab_html += f"""        <dl class="cur"> 
         <a href="./{n['link']}" target="_blank" title="{n['title']}"> 
          <dt> 
           <h4>{n['title'][:32]}...</h4> 
           <i><img alt="{n['title']}" src="./{n['image']}" title="{n['title']}"></i> 
          </dt> 
          <dd> 
           <p>{n['desc'][:80]}...</p> 
           <span><em>{n['date']}</em><i><img src="./images/newmore.png"></i></span> 
          </dd> </a> 
        </dl> 
"""
        tab_html += "       "
        return tab_html
        
    qydt_html = make_news_tab_html(qydt_news)
    cpbk_html = make_news_tab_html(cpbk_news)
    cjwt_html = make_news_tab_html(cjwt_news)
    
    news_pattern = r'(<div class="tabsnew f_cb">.*?<div class="js-swiper-tab">.*?<div class="swiper-wrapper">.*?<div class="swiper-slide">\s*<div class="newcon">)(.*?)(</div>\s*</div>\s*<div class="swiper-slide">\s*<div class="newcon">)(.*?)(</div>\s*</div>\s*<div class="swiper-slide">\s*<div class="newcon">)(.*?)(</div>\s*</div>)'
    match = re.search(news_pattern, html, re.DOTALL)
    if match:
        html = (
            html[:match.start(2)] + qydt_html +
            html[match.end(2):match.start(4)] + cpbk_html +
            html[match.end(4):match.start(6)] + cjwt_html +
            html[match.end(6):]
        )
        
    # 5. Update Friendship Links
    html = update_friendlinks(html, friendlinks)
    
    # Apply contact updates
    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, "index.html")
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_all_footers_headers_and_nav(settings, nav_links):
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        if "cms_system" in root:
            continue
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    new_content = update_global_contact_info(content, settings)
                    
                    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
                    new_content = update_navigation(new_content, nav_links, rel_path)
                    
                    if new_content != content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"[-] Error updating header/footer in {file}: {e}")

def update_sitemaps(products, articles):
    sitemap_xml_path = os.path.join(WORKSPACE_DIR, "sitemap.xml")
    if os.path.exists(sitemap_xml_path):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += '  <url><loc>http://www.mellgen.com/</loc><priority>1.0</priority></url>\n'
        list_pages = [
            "product_hzpyl.html", "product_yyyl.html", "product_spyyyl.html", "product_index.html",
            "article_xwzx.html", "article_hzal.html", "article_cjwt.html", "article_qydt.html", "article_cpbk.html",
            "helps/yloemd.html", "helps/tptjs.html", "helps/gymej.html", "helps/lxwm.html"
        ]
        for page in list_pages:
            xml += f'  <url><loc>http://www.mellgen.com/{page}</loc><priority>0.8</priority></url>\n'
        for p in products:
            xml += f'  <url><loc>http://www.mellgen.com/{p["link"]}</loc><priority>0.6</priority></url>\n'
        for a in articles:
            xml += f'  <url><loc>http://www.mellgen.com/{a["link"]}</loc><priority>0.5</priority></url>\n'
        xml += '</urlset>\n'
        with open(sitemap_xml_path, "w", encoding="utf-8") as f:
            f.write(xml)

def publish_site():
    print("[*] Starting site regeneration and publishing...")
    products, articles, settings, friendlinks, nav_links = load_db()
    
    # 1. Update listing pages
    update_product_listing_page(os.path.join(WORKSPACE_DIR, "product_hzpyl.html"), "化妆品原料", products, settings, nav_links)
    update_product_listing_page(os.path.join(WORKSPACE_DIR, "product_yyyl.html"), "医用原料", products, settings, nav_links)
    update_product_listing_page(os.path.join(WORKSPACE_DIR, "product_spyyyl.html"), "食品营养原料", products, settings, nav_links)
    
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_xwzx.html"), "新闻资讯", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_hzal.html"), "合作案例", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_cjwt.html"), "常见问答", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_qydt.html"), "企业新闻", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_cpbk.html"), "技术知识", articles, settings, nav_links)
    
    # 2. Re-generate all product details
    template_product_path = os.path.join(WORKSPACE_DIR, "products", "tphtct.html")
    if os.path.exists(template_product_path):
        with open(template_product_path, "r", encoding="utf-8") as tf:
            base_product_html = tf.read()
        for p in products:
            try:
                generate_product_detail_page(p, base_product_html, settings, nav_links)
            except Exception as e:
                print(f"[-] Error generating page for product {p['id']}: {e}")
                
    # 3. Re-generate all article details
    template_article_path = os.path.join(WORKSPACE_DIR, "articles", "jsjjtp.html")
    if os.path.exists(template_article_path):
        with open(template_article_path, "r", encoding="utf-8") as tf:
            base_article_html = tf.read()
        for a in articles:
            try:
                generate_article_detail_page(a, base_article_html, settings, nav_links)
            except Exception as e:
                print(f"[-] Error generating page for article {a['id']}: {e}")
                
    # 4. Update homepage structures
    update_homepage(products, articles, settings, friendlinks, nav_links)
    
    # Update duplicate/other homepage files if they exist (like mellgen_home.html)
    other_home = os.path.join(WORKSPACE_DIR, "mellgen_home.html")
    if os.path.exists(other_home):
        try:
            with open(other_home, "r", encoding="utf-8") as f:
                oh_html = f.read()
            oh_html = update_friendlinks(oh_html, friendlinks)
            oh_html = update_global_contact_info(oh_html, settings)
            oh_html = update_navigation(oh_html, nav_links, "mellgen_home.html")
            with open(other_home, "w", encoding="utf-8") as f:
                f.write(oh_html)
        except Exception:
            pass
            
    # 5. Global footer/header/nav propagates
    update_all_footers_headers_and_nav(settings, nav_links)
    
    # 6. Sitemaps
    update_sitemaps(products, articles)
    
    print("[OK] Site publishing complete!")

if __name__ == "__main__":
    publish_site()
