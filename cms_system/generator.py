import os
import re
import json
import shutil
import threading
from urllib.parse import urlparse

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if '\ufffd' in WORKSPACE_DIR or not os.path.exists(WORKSPACE_DIR) or not os.path.exists(os.path.join(WORKSPACE_DIR, "cms_system")):
    WORKSPACE_DIR = os.path.abspath(os.path.normpath('E:/\u79c1\u6709\u4e91/\u6211\u7684AI\u7ba1\u7406\u7cfb\u7edf/mellgen_website'))
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")
_publish_lock = threading.Lock()

def is_online_article(a, settings=None):
    if not isinstance(a, dict):
        return False
    show_val = a.get("show")
    if show_val is False or str(show_val).strip().lower() in ["false", "0", "off", "no"]:
        return False
    status_val = str(a.get("status", "")).strip().lower()
    if status_val in ["offline", "draft", "hidden", "takedown"]:
        return False
    if show_val is not True and str(show_val).strip().lower() not in ["true", "1", "on", "yes"] and status_val != "published":
        return False
        
    if settings:
        cat = a.get("category", "")
        cat_vis = dict(settings.get("article_categories_visibility") or {})
        if settings.get("show_case_section", True) is False:
            cat_vis["合作案例"] = False
            cat_vis["行业案例"] = False
        if cat in cat_vis and cat_vis[cat] is False:
            return False
    return True

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
    
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    if os.path.exists(products_path):
        with open(products_path, "r", encoding="utf-8") as f:
            all_products = json.load(f)
        products = [p for p in all_products if p.get("show", True) is not False and p.get("status") != "offline"]
        products.sort(key=lambda x: (x.get("sort", 99999) if isinstance(x.get("sort"), (int, float)) else 99999, x.get("id", "")))
    if os.path.exists(articles_path):
        with open(articles_path, "r", encoding="utf-8") as f:
            all_articles = json.load(f)
        articles = [a for a in all_articles if is_online_article(a, settings)]
    if os.path.exists(friendlinks_path):
        with open(friendlinks_path, "r", encoding="utf-8") as f:
            friendlinks = json.load(f)
    if os.path.exists(nav_path):
        with open(nav_path, "r", encoding="utf-8") as f:
            nav_links = json.load(f)
            
    return products, articles, settings, friendlinks, nav_links

DOMAIN_BASE = "https://www.mellgen.com"

def generate_canonical_and_hreflang_tags(rel_path):
    rel_norm = rel_path.replace("\\", "/").strip("/")
    is_en = rel_norm.startswith("en/")
    if is_en:
        core_rel = rel_norm[3:].strip("/")
    else:
        core_rel = rel_norm
        
    if core_rel in ["index.html", ""]:
        zh_url = f"{DOMAIN_BASE}/"
        en_url = f"{DOMAIN_BASE}/en/"
    else:
        zh_url = f"{DOMAIN_BASE}/{core_rel}"
        en_url = f"{DOMAIN_BASE}/en/{core_rel}"
        
    canonical_url = en_url if is_en else zh_url
    x_default_url = zh_url
    
    tags = [
        f'<link rel="canonical" href="{canonical_url}">',
        f'<link rel="alternate" hreflang="zh-CN" href="{zh_url}">',
        f'<link rel="alternate" hreflang="en" href="{en_url}">',
        f'<link rel="alternate" hreflang="x-default" href="{x_default_url}">'
    ]
    return "\n  ".join(tags)

def generate_open_graph_tags(title, description, image_url, page_rel, og_type="website"):
    clean_desc = (description or "").replace('"', '&quot;').replace('\n', ' ')[:200]
    clean_title = (title or "").replace('"', '&quot;')
    
    if not image_url or not isinstance(image_url, str):
        full_image = f"{DOMAIN_BASE}/images/ban_txt.png"
    elif image_url.startswith("http"):
        full_image = image_url
    else:
        full_image = f"{DOMAIN_BASE}/{image_url.lstrip('./').lstrip('/')}"
        
    if page_rel in ["index.html", ""]:
        full_url = f"{DOMAIN_BASE}/"
    elif page_rel.startswith("http"):
        full_url = page_rel
    else:
        full_url = f"{DOMAIN_BASE}/{page_rel.lstrip('./').lstrip('/')}"
        
    tags = [
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{clean_title}">',
        f'<meta property="og:description" content="{clean_desc}">',
        f'<meta property="og:url" content="{full_url}">',
        f'<meta property="og:site_name" content="美尔健生物 | Mellgen Bio">',
        f'<meta property="og:image" content="{full_image}">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{clean_title}">',
        f'<meta name="twitter:description" content="{clean_desc}">',
        f'<meta name="twitter:image" content="{full_image}">'
    ]
    return "\n  ".join(tags)

def generate_verification_meta(settings):
    tags = []
    g_code = (settings.get("google_site_verification") or "").strip()
    if g_code:
        m = re.search(r'content=["\']([^"\']+)["\']', g_code)
        val = m.group(1) if m else g_code
        tags.append(f'<meta name="google-site-verification" content="{val}">')
        
    b_code = (settings.get("bing_site_verification") or "").strip()
    if b_code:
        m = re.search(r'content=["\']([^"\']+)["\']', b_code)
        val = m.group(1) if m else b_code
        tags.append(f'<meta name="msvalidate.01" content="{val}">')
        
    bd_code = (settings.get("baidu_site_verification") or "").strip()
    if bd_code:
        m = re.search(r'content=["\']([^"\']+)["\']', bd_code)
        val = m.group(1) if m else bd_code
        tags.append(f'<meta name="baidu-site-verification" content="{val}">')
        
    return "\n  ".join(tags) if tags else ""

def inject_meta_block_into_head(html, block_content, block_id="seo-meta-block"):
    """
    Safely injects or replaces a designated SEO block in the HTML head
    """
    wrapped = f"<!-- [{block_id}] -->\n  {block_content}\n  <!-- [/{block_id}] -->"
    pattern = rf'<!-- \[{block_id}\] -->[\s\S]*?<!-- \[/{block_id}\] -->'
    if re.search(pattern, html):
        return re.sub(pattern, wrapped, html)
    elif '</head>' in html:
        return html.replace('</head>', f'  {wrapped}\n</head>')
    return html

# Helper: safe replacement using string slicing to avoid regex group reference errors
def replace_group(pattern, replacement, html, group_index=2, flags=re.DOTALL):
    match = re.search(pattern, html, flags)
    if match:
        start = match.start(group_index)
        end = match.end(group_index)
        return html[:start] + replacement + html[end:]
    return html

def get_product_subcategories(category):
    if category in ["化妆品原料", "cat_hzpyl", "全部", "all", "原料产品中心", "产品中心", "产品频道"]:
        return [
            "化妆品原料", "高渗透型重组蛋白/多肽", "重组仿生蛋白", "植物源活性物", 
            "海洋源活性物", "婴儿菌发酵源活性物", "植物提取物", "仿生生物原料", 
            "仿生原料", "细胞营养素", "生物发酵原料", "生物酶", "水生原料", 
            "动物源活性物", "焕亮因子"
        ]
    elif category in ["高渗透型重组蛋白/多肽", "cat_tpxzzd"]:
        return ["高渗透型重组蛋白/多肽"]
    elif category in ["重组仿生蛋白", "cat_zzfsdb", "重组蛋白", "cat_zzdb"]:
        return ["重组仿生蛋白", "重组蛋白", "仿生生物原料", "仿生原料"]
    elif category in ["植物源活性物", "植物提取物", "cat_zwyhxw", "灵芝多糖", "cat_lzdt", "桃胶多糖"]:
        return ["植物源活性物", "植物提取物", "灵芝多糖", "桃胶多糖"]
    elif category in ["海洋源活性物", "cat_hyyhxw", "水母胶原"]:
        return ["海洋源活性物", "水生原料", "生物发酵原料", "生物酶", "水母胶原"]
    elif category in ["婴儿菌发酵源活性物", "cat_yejfjy", "生物发酵原料", "cat_swfjyl"]:
        return ["婴儿菌发酵源活性物", "生物发酵原料"]
    elif category in ["动物源活性物", "仿生生物原料", "仿生原料", "cat_dwyhxw"]:
        return ["动物源活性物", "仿生生物原料", "仿生原料"]
    elif category in ["细胞营养素", "复合营养素", "cat_xbyys", "cat_fhyys"]:
        return ["细胞营养素", "复合营养素"]
    return [category]

def get_article_subcategories(category):
    if category in ["检测报告", "三方权威报告", "实验室数据研究", "实验室研究数据"]:
        return ["检测报告", "三方权威报告", "实验室数据研究", "实验室研究数据"]
    elif category == "合作案例":
        return ["合作案例", "三方权威报告", "实验室研究数据", "客户合作", "应用场景", "实验室数据研究", "检测报告"]
    elif category in ["三方权威报告", "实验室数据研究"]:
        return ["三方权威报告", "实验室数据研究"]
    elif category == "实验室研究数据":
        return ["实验室研究数据"]
    elif category == "客户合作":
        return ["客户合作"]
    elif category in ["应用场景", "医美行业", "护肤品工厂", "化妆品", "健康护理行业", "功能类食品", "洗护用品", "女性护理产品"]:
        return ["应用场景", "医美行业", "护肤品工厂", "化妆品", "健康护理行业", "功能类食品", "洗护用品", "女性护理产品"]
    elif category == "新闻资讯":
        return ["新闻资讯", "企业新闻", "科普研究", "技术知识", "常见问答"]
    elif category == "企业新闻":
        return ["企业新闻", "新闻资讯"]
    elif category in ["科普研究", "技术知识"]:
        return ["科普研究", "技术知识"]
    return [category]


def update_global_contact_info(html_content, settings):
    # 1. Clean repeating '广东省' and update address cleanly
    address_val = (settings.get("address", "") or "").strip()
    # Normalize address_val to avoid duplicate province
    if address_val:
        address_val = re.sub(r'^(?:广东省\s*)+', '广东省', address_val)
    else:
        address_val = "广东省深圳市大鹏新区葵涌街道生命科学产业园A23栋 3楼"

    # Collapse any existing multiple '广东省' in HTML
    html_content = re.sub(r'(?:广东省\s*)+', '广东省', html_content)
    # Replace in address block
    html_content = re.sub(
        r'(地址：\s*)(?:广东省\s*)*(?:深圳市大鹏新区葵涌街道(?:三溪社区金业大道140号|金业大道140号)?生命科学产业园[A-Za-z0-9栋 楼/、\-]*)',
        r'\g<1>' + address_val,
        html_content
    )
    
    # 2. Robust phone replacement across headers, footers, and articles
    phone_val = (settings.get("phone", "") or "").strip()
    if not phone_val:
        # Check contact dict
        c = settings.get("contact", {})
        if isinstance(c, dict):
            p = c.get("phone", "").strip()
            t = c.get("tel", "").strip()
            if t and p:
                phone_val = f"{t} / {p}"
            elif p:
                phone_val = p
            elif t:
                phone_val = t
    if not phone_val:
        phone_val = "0755-82926499 / 136-9197-8530"

    parts = [p.strip() for p in re.split(r'[/,，、&;]+|\s{2,}', phone_val) if p.strip() and p.strip() not in ['nbsp']]
    if len(parts) >= 2:
        phone_slash = " / ".join(parts[:2])
        phone_nbsp = "&nbsp;&nbsp;&nbsp;".join(parts[:2])
    elif len(parts) == 1:
        phone_slash = parts[0]
        phone_nbsp = parts[0]
    else:
        phone_slash = phone_val
        phone_nbsp = phone_val.replace(" / ", "&nbsp;&nbsp;&nbsp;")

    # Replace in footer .ftel: <div class="ftel">\s*.*?\s*</div>
    html_content = re.sub(
        r'(<div class="ftel">)[\s\S]*?(</div>)',
        r'\1\n       ' + phone_nbsp + r'\n     \2',
        html_content
    )

    # Replace in top header phone: <b>...</b> inside p102-top-l
    html_content = re.sub(
        r'(<div class="p102-top-l">[\s\S]*?<b>)[\d\- /&;a-zA-Z]+(</b>)',
        r'\1' + phone_slash + r'\2',
        html_content
    )

    # Replace in article declaration footer note: 欢迎致电全国服务热线：...。
    html_content = re.sub(
        r'(欢迎致电全国服务热线：)[\d\- /&;、]+(。)',
        r'\1' + phone_slash + r'\2',
        html_content
    )

    # 3. Email replacement
    email_val = (settings.get("email", "") or "").strip() or "61791579@qq.com"
    html_content = re.sub(r'邮箱：[\w\.-]+@[\w\.-]+', '邮箱：' + email_val, html_content)
    html_content = re.sub(r'<h3>\s*电子邮箱\s*</h3>\s*<span>[^<]+</span>', f'<h3>电子邮箱</h3>\n                    <span>{email_val}</span>', html_content)

    # 4. QQ replacement
    qq_val = (settings.get("qq", "") or "").strip() or "61791579"
    html_content = re.sub(r'<h3>\s*QQ\s*</h3>\s*<span>\d+</span>', f'<h3>QQ</h3>\n                    <span>{qq_val}</span>', html_content)

    return html_content


def sync_all_contact_to_site(settings=None):
    """把最新的联系方式（电话、地址、邮箱、QQ）全量同步更新至整站所有 HTML 页面"""
    if settings is None:
        settings_path = os.path.join(DATA_DIR, "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {}

    updated_count = 0
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        if any(x in root for x in ['.git', '.venv', 'backup', 'cms_data_backup', 'brain']):
            continue
        for f in files:
            if f.endswith('.html'):
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f_in:
                        orig = f_in.read()
                    new_html = update_global_contact_info(orig, settings)
                    if new_html != orig:
                        with open(fp, "w", encoding="utf-8") as f_out:
                            f_out.write(new_html)
                        updated_count += 1
                except Exception as e:
                    pass
    print(f"[generator] 全站联系方式与地址清理同步完成，更新了 {updated_count} 个页面。")
    return updated_count


def update_friendlinks(html_content, friendlinks):
    active_links = [fl for fl in friendlinks if fl.get("show", True)]
    links_html = ""
    for fl in active_links:
        links_html += f'<a href="{fl["url"]}" title="{fl["name"]}">{fl["name"]}</a> '
    
    # Replace content inside <div class="link_c"> <li lastclass="lasta"> ... </li> </div>
    html_content = replace_group(r'(<div class="link_c">\s*<li[^>]*>)(.*?)(</li>\s*</div>)', links_html, html_content)
    
    # If no active links, hide the entire friendly links block; otherwise ensure it is visible
    if not active_links:
        html_content = re.sub(r'<div class="g_link f_fw[^"]*"[^>]*>', '<div class="g_link f_fw hidden" style="display: none !important;">', html_content)
    else:
        html_content = re.sub(r'<div class="g_link f_fw[^"]*"[^>]*>', '<div class="g_link f_fw">', html_content)
        
    return html_content

def sync_friendlinks_to_pages(friendlinks=None):
    if friendlinks is None:
        friendlinks_path = os.path.join(DATA_DIR, "friendlinks.json")
        friendlinks = []
        if os.path.exists(friendlinks_path):
            try:
                with open(friendlinks_path, "r", encoding="utf-8") as f:
                    friendlinks = json.load(f)
            except Exception:
                friendlinks = []
                
    target_files = [
        os.path.join(WORKSPACE_DIR, "index.html"),
        os.path.join(WORKSPACE_DIR, "mellgen_home.html"),
        os.path.join(WORKSPACE_DIR, "en", "index.html"),
        os.path.join(WORKSPACE_DIR, "en", "mellgen_home.html"),
    ]
    for fp in target_files:
        if os.path.exists(fp):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                updated = update_friendlinks(content, friendlinks)
                if updated != content:
                    with open(fp, "w", encoding="utf-8") as f:
                        f.write(updated)
            except Exception as e:
                print(f"[-] Error syncing friendlinks to {fp}: {e}")


def update_navigation(html_content, nav_links, file_rel_path, settings=None):
    if not nav_links:
        return html_content
        
    if settings is None:
        try:
            with open(os.path.join(DATA_DIR, "settings.json"), "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            settings = {}

    show_case = settings.get("show_case_section", True) is not False
    cat_vis = dict(settings.get("article_categories_visibility") or {})
    if not show_case:
        cat_vis["合作案例"] = False
        cat_vis["行业案例"] = False
        
    # Determine directory depth relative to workspace root
    depth = len(file_rel_path.replace("\\", "/").split("/")) - 1
    prefix = "../" * depth
    if not prefix:
        prefix = "./"
        
    nav_html = "\n"
    # Flatten the tree structure to flat <li> items to fit Mellgen's style safely
    def process_item(item):
        nonlocal nav_html
        item_name = item.get("name", "")
        if cat_vis.get(item_name) is False:
            return
            
        url = item.get("url", "")
        # Resolve prefix
        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("//") or url.startswith("/")):
            url = prefix + url.lstrip("./")
        nav_html += f'     <li> <a href="{url}" title="{item["name"]}"> {item["name"]} </a> </li> \n'
        
        # If there are children, render them sequentially to keep it flat but fully present
        for child in item.get("children", []):
            if child.get("show") is False or child.get("status") == "hidden":
                continue
            child_name = child.get("name", "")
            if cat_vis.get(child_name) is False:
                continue
            if child_name in ["三方权威报告", "实验室研究数据"] and cat_vis.get("检测报告") is False:
                continue
            child_url = child.get("url", "")
            if not (child_url.startswith("http://") or child_url.startswith("https://") or child_url.startswith("//") or child_url.startswith("/")):
                child_url = prefix + child_url.lstrip("./")
            nav_html += f'     <li class="is-sub-item" style="display:none;"> <a href="{child_url}" title="{child["name"]}"> &nbsp;&nbsp;├ {child["name"]} </a> </li> \n'

    for item in nav_links:
        if item.get("show") is False or item.get("status") == "hidden":
            continue
        item_name = item.get("name", "")
        if cat_vis.get(item_name) is False:
            continue
        if not show_case and (item_name in ["合作案例", "行业案例"] or "article_hzal" in item.get("url", "")):
            continue
        process_item(item)
        
    nav_html += "   "
    
    pattern = r'(<div class="[^"]*menu[^"]*">.*?<ul>)(.*?)(</ul>)'
    if re.search(pattern, html_content, re.DOTALL):
        html_content = replace_group(pattern, nav_html, html_content, group_index=2)
    return html_content

DEFAULT_DISCLAIMER = """【法规合规与专业同行免责声明】
1. 本网页展示的所有原料产品技术参数、活性机理、科研实验数据（包括细胞实验、生化模型等体外数据）及相关文献资料，仅供化妆品品牌方研发工程师、配方师、产品策划及高校科研机构进行同行专业技术探讨与配方研发参考，并非针对终端消费者的产品功效宣称、商业承诺或医疗建议。
2. 根据《化妆品监督管理条例》、《化妆品功效宣称评价规范》等相关法律法规，使用本原料的化妆品成品企业应独立对其终产品的安全性、稳定性和功效宣称负责，并依法完成终产品的功效宣称评价与国家NMPA平台备案/注册申报，不得直接将本技术资料中有关原料的体外/细胞实验结论直接作为终端化妆品功效依据。
3. 本公司对因客户不当使用、超范围宣称或未经验证配伍导致的任何直接或间接法律与质量责任不承担连带责任。"""

def render_product_b2b_sections(product):
    rd = product.get("rd_info") or {}
    proc = product.get("procurement_info") or {}
    mkt = product.get("marketing_info") or {}
    disclaimer = product.get("disclaimer") or DEFAULT_DISCLAIMER

    has_rd = any(bool(v) for v in rd.values()) if isinstance(rd, dict) else False
    has_proc = any(bool(v) for v in proc.values()) if isinstance(proc, dict) else False
    has_mkt = any(bool(v) for v in mkt.values()) if isinstance(mkt, dict) else False

    out = []
    out.append('\n<!-- ==================== B2B PROFESSIONAL DOSSIER & DISCLAIMER ==================== -->')
    out.append('<div class="mellgen-b2b-section" style="width:1200px; margin: 45px auto 25px auto; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'PingFang SC\', \'Microsoft YaHei\', sans-serif; box-sizing: border-box;">')

    if has_rd or has_proc or has_mkt:
        out.append('  <div style="text-align: center; margin-bottom: 35px;">')
        out.append('    <h3 style="font-size: 26px; color: #174778; font-weight: 700; margin: 0 0 8px 0; letter-spacing: 0.5px;">原料专业技术与供应档案</h3>')
        out.append('    <p style="font-size: 14px; color: #64748b; margin: 0;">针对研发工程师、采购供应链及产品策划的专属深度技术与准入资料</p>')
        out.append('  </div>')

    # 1. 配方研发工程师专区
    if has_rd:
        out.append('  <!-- 研发配方工程师专区 -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #174778 0%, #1d5b99 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">🔬</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">配方研发工程师指南 (R&D Technical Dossier)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #93c5fd; font-size: 12px;">配方应用 · 理化参数 · 稳定性与配伍</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px;">')
        out.append('      <table style="width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155;">')
        
        rd_items = [
            ("INCI名称（中文）", rd.get("inci_cn"), "INCI名称（英文）", rd.get("inci_en")),
            ("CAS 号", rd.get("cas"), "建议添加量", rd.get("dosage")),
            ("适宜 pH 范围", rd.get("ph_range"), "加工耐温工艺", rd.get("heat_tolerance")),
            ("外观性状与气味", rd.get("appearance"), "溶解性与溶解方式", rd.get("solubility")),
        ]
        
        for label1, val1, label2, val2 in rd_items:
            if val1 or val2:
                out.append('        <tr style="border-bottom: 1px solid #f1f5f9;">')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 15%; font-weight: 600; color: #475569; white-space: nowrap;">{label1}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 35%; color: #1e293b;">{val1 or "—"}</td>')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 15%; font-weight: 600; color: #475569; white-space: nowrap;">{label2}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 35%; color: #1e293b;">{val2 or "—"}</td>')
                out.append('        </tr>')
                
        out.append('      </table>')
        
        if rd.get("compatibility"):
            out.append('      <div style="margin-top: 16px; padding: 12px 18px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; font-size: 13px; color: #166534; line-height: 1.6;">')
            out.append(f'        <strong>💡 配伍建议与复配禁忌：</strong>{rd.get("compatibility")}')
            out.append('      </div>')
            
        out.append('    </div>')
        out.append('  </div>')

    # 2. 采购与合规供应专区
    if has_proc:
        out.append('  <!-- 采购与合规供应专区 -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">📦</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">采购与合规供应档案 (Procurement & Compliance)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #ccfbf1; font-size: 12px;">NMPA报送码 · 现货起订 · 索样支持 · 资质随货</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px;">')
        out.append('      <table style="width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155;">')
        
        proc_items = [
            ("NMPA监管机构原料报送码", proc.get("nmpa_code"), "供货包装规格", proc.get("packaging")),
            ("最小起订量 (MOQ)", proc.get("moq"), "供货交期", proc.get("lead_time")),
            ("储存条件", proc.get("storage"), "保质期 (Shelf Life)", proc.get("shelf_life")),
            ("研发索样支持", proc.get("sample_policy"), "随货资质报告", proc.get("qualifications")),
        ]
        
        for label1, val1, label2, val2 in proc_items:
            if val1 or val2:
                val1_display = f'<span style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; color: #047857; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-family: monospace; border: 1px solid #a7f3d0;">✓ {val1}</span>' if label1 == "NMPA监管机构原料报送码" and val1 else (val1 or "—")
                out.append('        <tr style="border-bottom: 1px solid #f1f5f9;">')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 15%; font-weight: 600; color: #475569; white-space: nowrap;">{label1}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 35%; color: #1e293b;">{val1_display}</td>')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 15%; font-weight: 600; color: #475569; white-space: nowrap;">{label2}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 35%; color: #1e293b;">{val2 or "—"}</td>')
                out.append('        </tr>')
                
        out.append('      </table>')
        out.append('    </div>')
        out.append('  </div>')

    # 3. 策划与营销卖点
    if has_mkt:
        out.append('  <!-- 策划与营销卖点 -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #b45309 0%, #d97706 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">💡</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">产品策划与营销卖点 (Marketing Highlights)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #fef3c7; font-size: 12px;">核心机理 · 功效宣称 · 推荐剂型 · 专利科研背书</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px; display: flex; flex-direction: column; gap: 16px;">')
        
        if mkt.get("mechanism"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">🧬 核心科技壁垒与作用机理：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; line-height: 1.7; color: #475569; background: #fffbeb; padding: 12px 16px; border-radius: 6px; border: 1px solid #fef3c7;">{mkt.get("mechanism")}</p>')
            out.append('      </div>')
            
        if mkt.get("claims"):
            raw_claims = mkt.get("claims")
            if isinstance(raw_claims, list):
                claims_list = [str(c).strip() for c in raw_claims if str(c).strip()]
            else:
                claims_list = [c.strip() for c in str(raw_claims).replace('，', ',').replace('、', ',').split(',') if c.strip()]
            claims_tags = [f'<span style="background: #f1f5f9; color: #1e293b; padding: 4px 12px; border-radius: 100px; font-size: 12.5px; font-weight: 600; border: 1px solid #cbd5e1;">🏷️ {c}</span>' for c in claims_list]
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 700; color: #1e293b;">✨ 核心卖点关键词：</h5>')
            out.append(f'        <div style="display: flex; flex-wrap: wrap; gap: 8px;">{"".join(claims_tags)}</div>')
            out.append('      </div>')
            
        if mkt.get("applications"):
            raw_app = mkt.get("applications")
            app_str = "、".join(raw_app) if isinstance(raw_app, list) else str(raw_app)
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">🧴 推荐适用产品品类与剂型：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{app_str}</p>')
            out.append('      </div>')
            
        if mkt.get("patents"):
            raw_pat = mkt.get("patents")
            pat_str = "<br>".join(raw_pat) if isinstance(raw_pat, list) else str(raw_pat)
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">📜 专利技术背书与科研合作：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{pat_str}</p>')
            out.append('      </div>')
            
        out.append('    </div>')
        out.append('  </div>')

    # 4. 法规合规与免责声明
    out.append('  <!-- 法规合规与免责声明 -->')
    out.append('  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #174778; border-radius: 6px; padding: 20px 24px; margin-top: 25px;">')
    out.append('    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">')
    out.append('      <span style="font-size: 16px;">⚖️</span>')
    out.append('      <h4 style="margin: 0; font-size: 14.5px; font-weight: 700; color: #1e293b; letter-spacing: 0.3px;">合规与专业同行免责声明</h4>')
    out.append('    </div>')
    
    disc_paragraphs = [p.strip() for p in disclaimer.split('\n') if p.strip()]
    out.append('    <div style="font-size: 12px; line-height: 1.8; color: #64748b;">')
    for p in disc_paragraphs:
        out.append(f'      <p style="margin: 4px 0;">{p}</p>')
    out.append('    </div>')
    out.append('  </div>')

    out.append('</div>')
    out.append('<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->\n')
    return '\n'.join(out)

ARTICLE_STOPWORDS = {
    "水", "1,2-己二醇", "丁二醇", "甘油", "苯氧乙醇", "多肽", "胶原蛋白", "重组蛋白", "蛋白",
    "化妆品原料", "原料", "活性物", "提取物", "发酵产物", "生物原料", "高渗透型重组蛋白/多肽",
    "重组仿生蛋白", "植物源活性物", "海洋源活性物", "复合营养素", "动物源活性物", "全水溶",
    "十肽-4", "水溶性", "无色", "透明液体"
}

def get_product_distinctive_terms(p):
    terms = set()
    pid = (p.get("id") or "").strip().lower()
    if pid:
        terms.add(pid)
    
    title = (p.get("title") or "").strip()
    if title:
        terms.add(title.lower())
        for part in re.split(r'[（\(\)）\s/]+', title):
            clean = part.strip().lower()
            if len(clean) >= 2 and clean not in ARTICLE_STOPWORDS:
                terms.add(clean)
                
    inci = (p.get("specs", {}).get("INCI中文") or p.get("rd_info", {}).get("inci_cn") or "")
    if inci:
        for item in inci.split("、"):
            c = item.strip().lower()
            if len(c) >= 3 and c not in ARTICLE_STOPWORDS:
                terms.add(c)
                
    mkt = p.get("marketing_info", {})
    if isinstance(mkt, dict):
        claims = mkt.get("claims", "")
        for c in claims.split(","):
            c = c.strip().lower()
            if len(c) >= 4 and c not in ARTICLE_STOPWORDS:
                terms.add(c)
                
    return [t for t in terms if t not in ARTICLE_STOPWORDS and len(t) >= 2]

def get_related_articles_for_product(product, all_articles, max_count=4):
    if not all_articles or not product:
        return []
    pid = (product.get("id") or "").strip().lower()
    title = (product.get("title") or "").strip().lower()
    
    matched = []
    seen_ids = set()
    
    for a in all_articles:
        aid = a.get("id")
        if not aid or aid in seen_ids:
            continue
            
        rel = (a.get("related_product") or "").strip().lower()
        if not rel or rel == "none":
            continue
            
        if a.get("show") is False or a.get("status") == "offline" or a.get("status") == "deleted" or a.get("is_deleted"):
            continue
            
        # Strictly verify that this article is associated with THIS product
        if rel == pid or rel == title or (len(rel) >= 3 and (rel in pid or rel in title or pid in rel or title in rel)):
            matched.append(a)
            seen_ids.add(aid)
            
    # Sort matched articles by date descending
    matched.sort(key=lambda x: x.get("date", ""), reverse=True)
    return matched[:max_count]

def render_product_related_articles_section(product, all_articles, is_en=False):
    matched_articles = get_related_articles_for_product(product, all_articles, max_count=4)
    if not matched_articles:
        return ""
        
    section_title = "Recommended Reading" if is_en else "推荐阅读"
    read_more_text = "Read More →" if is_en else "阅读全文 →"
    prefix = "../../" if is_en else "../"
    art_prefix = "../articles/"
    
    cards_html = []
    for a in matched_articles:
        aid = a.get("id", "")
        atitle = a.get("title", "")
        adesc = (a.get("desc") or "").strip()
        clean_desc = re.sub(r'<[^>]+>', '', adesc).replace('&quot;', '"').replace('&nbsp;', ' ')
        if len(clean_desc) > 90:
            clean_desc = clean_desc[:88] + "..."
            
        aimg = a.get("image") or "resource/images/ban_txt.png"
        if aimg.startswith("http"):
            full_img_src = aimg
        elif aimg.startswith("/"):
            full_img_src = f"{prefix}{aimg.lstrip('/')}"
        else:
            full_img_src = f"{prefix}{aimg}"
            
        adate = a.get("date") or "2026"
        acat = a.get("category") or ("Technical Insights" if is_en else "技术文献")
        alink = f"{art_prefix}{aid}.html"
        
        card = f'''    <div class="product-related-article-card">
      <a href="{alink}" target="_blank" class="product-related-article-thumb" title="{atitle}">
        <img src="{full_img_src}" alt="{atitle}">
        <span class="product-related-article-badge">{acat}</span>
      </a>
      <div class="product-related-article-body">
        <div class="product-related-article-meta">
          <span>📅 {adate}</span>
          <span style="color:#0284c7;font-weight:600;">{'Science Research' if is_en else '科普研究'}</span>
        </div>
        <h4 class="product-related-article-title">
          <a href="{alink}" target="_blank" title="{atitle}">{atitle}</a>
        </h4>
        <p class="product-related-article-desc">
          {clean_desc}
        </p>
        <div class="product-related-article-more">
          <a href="{alink}" target="_blank">
            {read_more_text}
          </a>
        </div>
      </div>
    </div>'''
        cards_html.append(card)
        
    cards_str = "\n".join(cards_html)
    
    section_html = f'''<!-- ==================== RECOMMENDED ARTICLES / 推荐阅读 ==================== -->
<div class="product-related-articles-section blk blk-main" style="width:1200px;margin:35px auto 40px auto;"> 
 <h4 class="p102-pro-content-title">{section_title}</h4> 
 <div class="product-related-articles-list"> 
{cards_str}
 </div> 
 <div class="clear"></div> 
</div>
<!-- ==================== END RECOMMENDED ARTICLES ==================== -->'''
    return section_html

def generate_product_detail_page(product, base_template_html, settings, nav_links, all_articles=None):
    dest_path = os.path.join(WORKSPACE_DIR, product['link'].replace('/', os.sep))
    if os.path.exists(dest_path):
        with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        if len(html) < 1000:
            html = base_template_html
    else:
        html = base_template_html
    
    seo_title = product.get("seoTitle") or f"{product['title']}-产品中心-{settings.get('company_name', '美尔健生物')}"
    html = re.sub(r'<title>[^<]+</title>', f"<title>{seo_title}</title>", html)
    
    seo_keywords = product.get("seoKeywords")
    if seo_keywords:
        if re.search(r'<meta[^>]+name=["\']keywords["\']', html, re.I):
            html = re.sub(r'(<meta[^>]+name=["\']keywords["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{seo_keywords}{m.group(3)}', html, flags=re.I)
        else:
            html = re.sub(r'(<title>[^<]+</title>)', lambda m: f'{m.group(1)}\n  <meta name="keywords" content="{seo_keywords}">', html, flags=re.I)
            
    seo_desc = product.get("seoDesc") or product.get("desc")
    if seo_desc:
        if re.search(r'<meta[^>]+name=["\']description["\']', html, re.I):
            html = re.sub(r'(<meta[^>]+name=["\']description["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{seo_desc}{m.group(3)}', html, flags=re.I)
        else:
            html = re.sub(r'(<title>[^<]+</title>)', lambda m: f'{m.group(1)}\n  <meta name="description" content="{seo_desc}">', html, flags=re.I)

    cat = product.get('category', '')
    if cat in ["高渗透型重组蛋白/多肽"]:
        cat_filename = "product_tpxzzd.html"
    elif cat in ["重组仿生蛋白", "重组蛋白"]:
        cat_filename = "product_zzfsdb.html"
    elif cat in ["植物源活性物", "植物提取物", "灵芝多糖"]:
        cat_filename = "product_zwyhxw.html"
    elif cat in ["海洋源活性物", "水母胶原"]:
        cat_filename = "product_hyyhxw.html"
    elif cat in ["婴儿菌发酵源活性物", "生物发酵原料"]:
        cat_filename = "product_yejfjy.html"
    elif cat in ["动物源活性物", "仿生生物原料"]:
        cat_filename = "product_dwyhxw.html"
    else:
        cat_filename = "product_hzpyl.html"

    # 1. Canonical & Multi-language (Hreflang)
    can_href_tags = generate_canonical_and_hreflang_tags(product.get("link", ""))
    html = inject_meta_block_into_head(html, can_href_tags, block_id="seo-canonical-hreflang")

    # 2. Open Graph & Twitter Cards for social/AI bot crawling
    og_tags = generate_open_graph_tags(
        title=seo_title,
        description=seo_desc or product.get("desc", ""),
        image_url=product.get("image", ""),
        page_rel=product.get("link", ""),
        og_type="product"
    )
    html = inject_meta_block_into_head(html, og_tags, block_id="seo-opengraph")

    # 3. Schema.org JSON-LD structured data with Product + BreadcrumbList for Google rich snippets
    domain_url = "https://www.mellgen.com"
    prod_full_url = f"{domain_url}/{product.get('link', '').lstrip('/')}"
    prod_img_url = f"{domain_url}/{product.get('image', '').lstrip('/')}" if product.get('image') else f"{domain_url}/images/ban_txt.png"
    
    ld_json_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Product",
                "name": product["title"],
                "description": seo_desc or product.get("desc", ""),
                "category": product.get("category", "化妆品原料"),
                "url": prod_full_url,
                "image": prod_img_url,
                "brand": {
                    "@type": "Brand",
                    "name": settings.get("company_name", "美尔健生物")
                },
                "manufacturer": {
                    "@type": "Organization",
                    "name": "美尔健（深圳）生物科技有限公司",
                    "url": domain_url
                },
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "priceCurrency": "CNY",
                    "price": "0",
                    "url": prod_full_url
                }
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首页",
                        "item": f"{domain_url}/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": product.get("category", "产品中心"),
                        "item": f"{domain_url}/{cat_filename}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": product["title"],
                        "item": prod_full_url
                    }
                ]
            }
        ]
    }
    ld_script = f'<script type="application/ld+json">\n{json.dumps(ld_json_data, ensure_ascii=False, indent=2)}\n</script>'
    html = inject_meta_block_into_head(html, ld_script, block_id="schema-jsonld")
        
    crumbs_pattern = r'(<b>您当前的位置：</b>\s*<a href="\.\./index\.html"[^>]*>\s*首页\s*</a>\s*<span> &gt; </span>\s*<i[^>]*>\s*<a href="\.\./product_index\.html"[^>]*>\s*产品频道\s*</a>\s*<span> &gt; </span>\s*</i>\s*<i[^>]*>\s*<a href="\.\./)([^"]+)("[^>]*>)([^<]+)(</a>)'
    match = re.search(crumbs_pattern, html)
    if match:
        html = (
            html[:match.start(2)] + cat_filename +
            html[match.end(2):match.start(4)] + product["category"] +
            html[match.end(4):]
        )
    
    # Update Title
    title_pattern = r'(<h1[^>]*class="p102-proShow-1-title"[^>]*>)(.*?)(</h1>)'
    if re.search(title_pattern, html, re.DOTALL):
        html = re.sub(r'(<h1\s+title=")(.*?)(")', lambda m: f'{m.group(1)}{product["title"]}{m.group(3)}', html)
        html = replace_group(title_pattern, f"\n        {product['title']} \n      ", html)
    elif re.search(r'(<div class="p102-proShow-1-para">.*?<h2>)(.*?)(</h2>)', html, re.DOTALL):
        html = replace_group(r'(<div class="p102-proShow-1-para">.*?<h2>)(.*?)(</h2>)', product["title"], html)

    # Update Category Subtitle
    cat_sub_pattern = r'(<div class="p102-proShow-1-text">\s*<h1[^>]*>.*?</h1>\s*<p>)(.*?)(</p>)'
    if re.search(cat_sub_pattern, html, re.DOTALL):
        html = replace_group(cat_sub_pattern, product.get("category", "化妆品原料"), html)
    
    # Update Top Brief Specs & Description
    # Update Top Brief Specs & Description (Compact & clean, preventing overflow into action buttons)
    specs_p_html = []
    if product.get("desc"):
        specs_p_html.append(f'<p style="line-height: 1.6; margin-bottom: 8px; color: #475569; font-size: 13.5px;">{product["desc"]}</p>')
    
    rd = product.get("rd_info", {})
    inci = rd.get("inci_cn") or product.get("specs", {}).get("INCI中文")
    if inci:
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>INCI名称：</strong>{inci}</p>')
        
    app_val = rd.get("appearance") or product.get("specs", {}).get("外观性状")
    sol_val = rd.get("solubility") or product.get("specs", {}).get("溶解性")
    if app_val or sol_val:
        app_sol = f"{app_val or ''}，{sol_val or ''}".strip('，')
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>性状及溶解性：</strong>{app_sol}</p>')
        
    dosage = rd.get("dosage") or product.get("specs", {}).get("建议添加量")
    if dosage:
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>建议添加量：</strong>{dosage}</p>')
        
    top_specs_content = "\n" + "\n".join(specs_p_html) + "\n "
    
    desc_box_pattern = r'(<div class="p102-proShow-1-desc">)(.*?)(</div>\s*<div class="p102-proShow-1-tel">)'
    if re.search(desc_box_pattern, html, re.DOTALL):
        html = replace_group(desc_box_pattern, top_specs_content, html)
    elif re.search(r'(<div class="p102-proShow-1-para-text">)(.*?)(</div>)', html, re.DOTALL):
        html = replace_group(r'(<div class="p102-proShow-1-para-text">)(.*?)(</div>)', top_specs_content, html)
    
    # Update/Reconstruct Left Column (Image, Corner Tag, Sample Bar, Size) cleanly and deterministically
    clean_left_block = f'''<div class="p102-proShow-1-left">
    <div class="product-sample-corner-tag" style="position: absolute; left: 14px; top: 14px; z-index: 6; background: rgba(15, 23, 42, 0.78); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); color: #ffffff; font-size: 12px; font-weight: 600; padding: 3px 9px; border-radius: 4px; display: inline-flex; align-items: center; gap: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.2); pointer-events: none;"><span style="width: 6px; height: 6px; background: #38bdf8; border-radius: 50%; display: inline-block;"></span>寄样图 (Sample Packaging)</div> 
    <div class="p102-proShow-1-prev"></div> 
    <div class="p102-proShow-1-next"></div> 
    <div class="p102-proShow-1-pic"> 
     <ul class="clearafter"> 
       <li><img alt="{product['title']}" src="../{product['image']}" title="{product['title']}"></li> 
     </ul> 
    </div> 
    <div class="product-detail-sample-bar" style="margin: 10px 14px 12px 14px; padding: 9px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #0284c7; border-radius: 4px; display: flex; align-items: center; justify-content: space-between; box-sizing: border-box;">
      <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
        <span style="display: inline-flex; align-items: center; gap: 4px; background: #0284c7; color: #ffffff; font-size: 12px; font-weight: 600; padding: 2px 7px; border-radius: 3px;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          寄样图
        </span>
        <span style="color: #475569; font-size: 12.5px;">实物规格：30g/50g 研发打样测试装（支持顺丰寄样）</span>
      </div>
      <a href="../helps/lxwm.html" target="_blank" style="display: inline-flex; align-items: center; gap: 4px; color: #0284c7; font-size: 12px; font-weight: 600; text-decoration: none; white-space: nowrap;">
        申请寄样 &gt;
      </a>
    </div>
    <div class="p102-proShow-1-size"></div> 
   </div>\n   '''

    left_pattern = r'<div class="p102-proShow-1-left"[^>]*>[\s\S]*?(?=\s*<div class="p102-proShow-1-right">)'
    if re.search(left_pattern, html):
        html = re.sub(left_pattern, clean_left_block, html)

    # Render B2B sections (R&D, Procurement, Marketing, Disclaimer)
    b2b_html = render_product_b2b_sections(product)
    
    # Clean any and all previous B2B sections first (wherever they may be located)
    b2b_clean_pattern = r'<!-- ==================== B2B PROFESSIONAL DOSSIER & DISCLAIMER ==================== -->[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->'
    html = re.sub(b2b_clean_pattern, '', html)
    html = re.sub(r'<div class="mellgen-b2b-section"[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->', '', html)

    full_content = f"{product['content']}\n{b2b_html}" if product.get("content") else b2b_html
    content_pattern = r'(<div class="p102-pro-content-desc endit-content">)([\s\S]*?)((?:\s*</div>){3,5}\s*<div class="k12-cx-xgcp-4pl-fx1-1-01)'
    match = re.search(content_pattern, html)
    if match:
        html = html[:match.start(2)] + f"\n     {full_content}\n    " + html[match.end(2):]
    else:
        content_pattern_fallback = r'(<div class="p102-pro-content-desc endit-content">)([\s\S]*?)((?:\s*</div>){3,5}\s*<!--)'
        match_fb = re.search(content_pattern_fallback, html)
        if match_fb:
            html = html[:match_fb.start(2)] + f"\n     {full_content}\n    " + html[match_fb.end(2):]

    if all_articles is None:
        art_file = os.path.join(DATA_DIR, "articles.json")
        if os.path.exists(art_file):
            with open(art_file, "r", encoding="utf-8") as f:
                all_articles = json.load(f)
        else:
            all_articles = []

    # 5. Clean up & Normalize Bottom Recommendations (ensure exactly one clean block, no duplicated blocks or empty news-info blocks)
    standard_rec_block = '''<div class="k12-cx-xgcp-4pl-fx1-1-01 blk blk-main" style="width:1200px;margin:30px auto;"> 
 <h4 class="p102-pro-content-title">推荐产品</h4> 
 <div class="k12-cx-xgcp-4pl-fx1-1-01-list"> 
   <dl> 
    <dt> 
     <a href="../products/tphtct.html" target="_blank" title="cTDP促透环肽"> <img alt="cTDP促透环肽" src="../resource/images/9b89259b4fb24ad2bcc390737279f8ff_44.jpg" title="cTDP促透环肽"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/tphtct.html" target="_blank" title="cTDP促透环肽"> cTDP促透环肽 </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       打开皮肤吸收通道的肌肤之钥，生物透皮技术核心载体，助力10000+Da.大分子高渗透吸收，功效护肤的高效促渗方案。
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/tphtct.html" target="_blank" title="cTDP促透环肽"></a> 
     </div> 
    </dd> 
   </dl> 
   <dl> 
    <dt> 
     <a href="../products/tpxldb.html" target="_blank" title="透皮纤连蛋白 (TFNpro)"> <img alt="透皮纤连蛋白 (TFNpro)" src="../resource/images/9b89259b4fb24ad2bcc390737279f8ff_30.jpg" title="透皮纤连蛋白 (TFNpro)"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/tpxldb.html" target="_blank" title="透皮纤连蛋白 (TFNpro)"> 透皮纤连蛋白 (TFNpro) </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       突破大分子透皮壁垒，专研穿膜肽紧密锚定真皮纤维网，促生胶原，修护肌底损伤。
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/tpxldb.html" target="_blank" title="透皮纤连蛋白 (TFNpro)"></a> 
     </div> 
    </dd> 
   </dl> 
   <dl> 
    <dt> 
     <a href="../products/mellpr8670.html" target="_blank" title="5D胶原蛋白 (5Dcollagen)"> <img alt="5D胶原蛋白 (5Dcollagen)" src="../resource/images/b8a942ac10c0484bbb9d2eb5ab7ed6ce_13.jpg" title="5D胶原蛋白 (5Dcollagen)"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/mellpr8670.html" target="_blank" title="5D胶原蛋白 (5Dcollagen)"> 5D胶原蛋白 (5Dcollagen) </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       含Ⅰ型、Ⅲ型、Ⅳ型、Ⅶ型及XVII型胶原组装5维网络，实现真皮、角质层与DEJ基底膜带多层修护。
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/mellpr8670.html" target="_blank" title="5D胶原蛋白 (5Dcollagen)"></a> 
     </div> 
    </dd> 
   </dl> 
   <dl class="p14-product-clear"> 
    <dt> 
     <a href="../products/yskmyz.html" target="_blank" title="益生舒缓因子 (依诺舒)"> <img alt="益生舒缓因子 (依诺舒)" src="../resource/images/9b89259b4fb24ad2bcc390737279f8ff_22.jpg" title="益生舒缓因子 (依诺舒)"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/yskmyz.html" target="_blank" title="益生舒缓因子 (依诺舒)"> 益生舒缓因子 (依诺舒) </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       提取天然高分支多糖分子，构建隐形透气水网膜，强韧皮肤物理屏障，长效保湿舒缓敏感。
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/yskmyz.html" target="_blank" title="益生舒缓因子 (依诺舒)"></a> 
     </div> 
    </dd> 
   </dl> 
 </div> 
 <div class="clear"></div> 
</div>'''
    articles_rec_block = render_product_related_articles_section(product, all_articles, is_en=False)
    combined_rec_block = standard_rec_block
    if articles_rec_block:
        combined_rec_block += "\n\n  " + articles_rec_block

    safe_rec_pattern = r'(<div class=["\']k12-cx-xgcp-4pl-fx1-1-01[\s\S]*?)(?=\s*<div class=["\']g_ft f_fw["\'])'
    if re.search(safe_rec_pattern, html):
        html = re.sub(safe_rec_pattern, combined_rec_block.replace('\\', '\\\\') + '\n\n  ', html)
    elif '<div class="g_ft f_fw"' in html:
        html = html.replace('<div class="g_ft f_fw"', combined_rec_block + '\n\n  <div class="g_ft f_fw"', 1)


    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, product['link'])
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if not html or len(html) < 1000:
        print(f"[-] Warning: generated html for product {product.get('id')} is too short ({len(html) if html else 0} chars), skipping write.")
        return False
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def generate_article_detail_page(article, base_template_html, settings, nav_links, all_online_articles=None):
    if not base_template_html or len(base_template_html) < 1000:
        print(f"[-] Error: base_template_html is missing or too short ({len(base_template_html) if base_template_html else 0} chars), skipping article {article.get('id')}.")
        return False
    html = base_template_html
    
    art_title = f"{article['title']}-新闻资讯-{settings.get('company_name', '美尔健生物')}"
    html = re.sub(r'<title>[^<]+</title>', f"<title>{art_title}</title>", html)
    
    cat_filename = "article_xwzx.html"
    cat = article.get('category', '')
    subcat = article.get('sub_category', '')
    if subcat in ["三方权威报告", "实验室数据研究"] or cat in ["三方权威报告", "实验室数据研究"]:
        cat_filename = "article_syssj.html"
    elif subcat == "实验室研究数据":
        cat_filename = "article_sysyanjiu.html"
    elif subcat == "客户合作":
        cat_filename = "article_khhz.html"
    elif subcat == "应用场景":
        cat_filename = "article_yycj.html"
    elif cat in ["合作案例", "医美行业", "护肤品工厂", "化妆品", "健康护理行业", "功能类食品", "洗护用品", "女性护理产品"]:
        cat_filename = "article_hzal.html"
    elif cat in ["常见问答"]:
        cat_filename = "article_cjwt.html"
    elif cat in ["企业新闻"]:
        cat_filename = "article_qydt.html"
    elif cat in ["技术知识", "科普研究"]:
        cat_filename = "article_cpbk.html"
        
    crumbs_pattern = r'(<b>您当前的位置：</b>\s*<a href="\.\./index\.html"[^>]*>\s*首页\s*</a>\s*<span> &gt; </span>\s*<i[^>]*>\s*<a href="\.\./)([^"]+)("[^>]*>)([^<]+)(</a>)'
    match = re.search(crumbs_pattern, html)
    if match:
        html = (
            html[:match.start(2)] + cat_filename +
            html[match.end(2):match.start(4)] + article["category"] +
            html[match.end(4):]
        )
    
    last_crumb_pattern = r'(<i[^>]*>\s*<a href="\.\./articles/[^"]*"[^>]*>)(.*?)(</a>\s*</i>\s*</div>)'
    if re.search(last_crumb_pattern, html):
        html = re.sub(last_crumb_pattern, rf'<i class=""> <a href="../{article["link"]}" title="{article["title"]}"> {article["title"]} </a> </i>\n </div>', html)

    html = replace_group(r'(<h1[^>]*>)(.*?)(</h1>)', article["title"], html)
    html = re.sub(r'<h1[^>]*title="[^"]*"', f'<h1 title="{article["title"]}"', html)
    
    html = replace_group(r'(<span class="p102-info-date">)(.*?)(</span>)', article["date"], html, flags=0)
    html = re.sub(r'发布日期：\d{4}-\d{2}-\d{2}', f'发布日期：{article.get("date", "")}', html)
    
    content_pattern = r'(<div class="p102-info-content endit-content">)(.*?)(</div>\s*<div class="clear"></div>)'
    
    # Normalize relative image paths based on target page depth
    art_content = article.get("content", "")
    rel_depth = article.get("link", "").count("/")
    root_prefix = "../" * rel_depth if rel_depth > 0 else "./"
    art_content = re.sub(r'src=["\'](?:\.\./)*resource/images/', f'src="{root_prefix}resource/images/', art_content)
    art_content = re.sub(r'src=["\'](?:\.\./)*resource/reports/images/', f'src="{root_prefix}resource/reports/images/', art_content)
    art_content = re.sub(r'src=["\'](?:\.\./)*images/', f'src="{root_prefix}images/', art_content)
    
    # Ensure legal disclaimer and normalized footer note are present
    disclaimer_html = """    <div class="article-disclaimer-box" style="margin-top:20px;padding:15px 18px;background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #7fb435;border-radius:6px;font-size:12.5px;color:#64748b;line-height:1.8;">
        <div style="font-weight:700;color:#1e293b;font-size:13px;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
            <span style="color:#7fb435;">⚖️</span> 版权与合规免责声明
        </div>
        <p style="margin:0 0 6px 0;">1. <strong>专业研发与学术参考：</strong>本站刊载之技术科普、学术文献、配方机理及实验数据探讨，仅供化妆品研发工程师、配方师及科研专业人士交流参考，不作为针对终端消费者的直接功效承诺或医疗/诊断建议。</p>
        <p style="margin:0 0 6px 0;">2. <strong>成品合规与宣称责任：</strong>化妆品品牌商及成品制造方应依据国家法律法规（如《化妆品监督管理条例》、《化妆品功效宣称评价规范》等），独立对其终产品的安全性、稳定性及功效宣称负责，并依法完成备案申报与功效评价。</p>
        <p style="margin:0;">3. <strong>知识产权与内容说明：</strong>本站部分内容或图片摘引自公开学术文献或专业资讯，版权归原作者所有，仅作学术分享与技术探讨。若涉及版权争议请联系核实；对于因客户不当使用或超范围宣称所引发的后果，本司不承担法律责任。</p>
    </div>"""

    if "article-disclaimer-box" not in art_content:
        if "article-footer-note" in art_content:
            art_content = re.sub(r'(<div class="article-footer-note"[^>]*>.*?</div>)', r'\1\n' + disclaimer_html, art_content, flags=re.DOTALL)
        else:
            art_content += f"\n{disclaimer_html}\n"

    art_content = art_content.replace("G55-82926499", "0755-82926499")

    if re.search(content_pattern, html, re.DOTALL):
        html = replace_group(content_pattern, f"\n     {art_content}\n    ", html)
    else:
        alt_pattern = r'(<div class="p102-info-content[^"]*">)(.*?)(</div>\s*<div class="clear"></div>)'
        if re.search(alt_pattern, html, re.DOTALL):
            html = replace_group(alt_pattern, f"\n     {art_content}\n    ", html)

    # Resolve all_online_articles if not provided
    if all_online_articles is None:
        all_articles_path = os.path.join(DATA_DIR, "articles.json")
        if os.path.exists(all_articles_path):
            try:
                with open(all_articles_path, "r", encoding="utf-8") as f:
                    all_online_articles = [x for x in json.load(f) if is_online_article(x, settings)]
            except Exception:
                all_online_articles = []
        else:
            all_online_articles = []

    # Filter strictly to other online articles
    other_online = [x for x in (all_online_articles or []) if x.get('id') != article.get('id') and is_online_article(x, settings)]

    # 1. Update Related Recommendations (相关推荐) - ONLY ONLINE ARTICLES
    curr_cat = article.get('category')
    curr_subcat = article.get('sub_category')
    same_cat_arts = [x for x in other_online if (curr_subcat and x.get('sub_category') == curr_subcat) or (curr_cat and x.get('category') == curr_cat)]
    diff_cat_arts = [x for x in other_online if x not in same_cat_arts]
    rel_candidates = same_cat_arts + diff_cat_arts
    selected_rel = rel_candidates[:2]

    rel_pattern = r'<div class="p102-info-related">[\s\S]*?<div class="clear"></div>\s*</div>\s*</div>'
    if selected_rel:
        rel_html = '<div class="p102-info-related">\n <h3 class="p102-info-11-title">相关推荐</h3>\n <div class="p102-info-related-list">\n'
        for ra in selected_rel:
            ra_link = ra.get("link", "").replace("\\", "/")
            if not ra_link.startswith("./") and not ra_link.startswith("../") and not ra_link.startswith("/"):
                ra_link = "../" + ra_link
            ra_img = (ra.get("image") or "images/ban_txt.png").replace("\\", "/")
            if not ra_img.startswith("./") and not ra_img.startswith("../") and not ra_img.startswith("/") and not ra_img.startswith("http"):
                ra_img = "../" + ra_img
            ra_desc = (ra.get("desc") or "")[:70].strip()
            rel_html += f"""    <dl> 
     <dt> 
      <a href="{ra_link}" title="{ra['title']}"><img alt="{ra['title']}" src="{ra_img}" title="{ra['title']}"></a> 
     </dt> 
     <dd> 
      <h4><a href="{ra_link}" title="{ra['title']}">{ra['title']}</a></h4> 
      <p> {ra_desc}... <a href="{ra_link}" title="{ra['title']}">【详情+】</a> </p> 
     </dd> 
    </dl>\n"""
        rel_html += '   <div class="clear"></div>\n </div>\n</div>'
        html = re.sub(rel_pattern, rel_html, html)
    else:
        # If no online articles to recommend, remove related block completely
        html = re.sub(rel_pattern, '', html)

    # 2. Update Latest News (最新资讯) - ONLY ONLINE ARTICLES
    latest_pattern = r'<div class="p102-info-latest">[\s\S]*?</ul>\s*</div>'
    sorted_latest = sorted(other_online, key=lambda x: x.get('date', ''), reverse=True)[:8]
    if sorted_latest:
        latest_html = '<div class="p102-info-latest">\n <h3 class="p102-info-12-title">最新资讯</h3>\n <ul class="clearafter">\n'
        half = (len(sorted_latest) + 1) // 2
        col1 = sorted_latest[:half]
        col2 = sorted_latest[half:]
        
        latest_html += '    <li>\n'
        for la in col1:
            la_link = la.get("link", "").replace("\\", "/")
            if not la_link.startswith("./") and not la_link.startswith("../") and not la_link.startswith("/"):
                la_link = "../" + la_link
            la_date = (la.get("date", "") or "").replace("-", ".")
            latest_html += f'      <h4><a href="{la_link}" title="{la["title"]}">{la["title"]}</a><em>{la_date}</em></h4>\n'
        latest_html += '    </li>\n'
        
        if col2:
            latest_html += '    <li class="last">\n'
            for la in col2:
                la_link = la.get("link", "").replace("\\", "/")
                if not la_link.startswith("./") and not la_link.startswith("../") and not la_link.startswith("/"):
                    la_link = "../" + la_link
                la_date = (la.get("date", "") or "").replace("-", ".")
                latest_html += f'      <h4><a href="{la_link}" title="{la["title"]}">{la["title"]}</a><em>{la_date}</em></h4>\n'
            latest_html += '    </li>\n'
            
        latest_html += '  </ul>\n</div>'
        html = re.sub(latest_pattern, latest_html, html)
    else:
        # If no online articles, remove latest block completely
        html = re.sub(latest_pattern, '', html)

    # 1. Canonical & Multi-language (Hreflang)
    can_href_tags = generate_canonical_and_hreflang_tags(article.get("link", ""))
    html = inject_meta_block_into_head(html, can_href_tags, block_id="seo-canonical-hreflang")

    # 2. Open Graph & Twitter Cards for social/AI bot crawling
    art_desc = article.get("desc") or re.sub(r'<[^>]+>', '', article.get("content", ""))[:150]
    og_tags = generate_open_graph_tags(
        title=art_title,
        description=art_desc,
        image_url=article.get("image", ""),
        page_rel=article.get("link", ""),
        og_type="article"
    )
    html = inject_meta_block_into_head(html, og_tags, block_id="seo-opengraph")

    # 3. Schema.org Article + BreadcrumbList JSON-LD
    domain_url = "https://www.mellgen.com"
    art_full_url = f"{domain_url}/{article.get('link', '').lstrip('/')}"
    art_img_url = f"{domain_url}/{article.get('image', '').lstrip('/')}" if article.get('image') else f"{domain_url}/images/ban_txt.png"
    
    ld_json_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": article["title"],
                "description": art_desc,
                "url": art_full_url,
                "image": art_img_url,
                "datePublished": article.get("date", ""),
                "author": {
                    "@type": "Organization",
                    "name": settings.get("company_name", "美尔健生物")
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "美尔健（深圳）生物科技有限公司",
                    "url": domain_url
                },
                "mainEntityOfPage": art_full_url
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首页",
                        "item": f"{domain_url}/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": article.get("category", "新闻资讯"),
                        "item": f"{domain_url}/{cat_filename}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": article["title"],
                        "item": art_full_url
                    }
                ]
            }
        ]
    }
    ld_script = f'<script type="application/ld+json">\n{json.dumps(ld_json_data, ensure_ascii=False, indent=2)}\n</script>'
    html = inject_meta_block_into_head(html, ld_script, block_id="schema-jsonld")
    
    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, article['link'])
    
    dest_path = os.path.join(WORKSPACE_DIR, article['link'].replace('/', os.sep))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if not html or len(html) < 1000:
        print(f"[-] Warning: generated html for article {article.get('id')} is too short ({len(html) if html else 0} chars), skipping write to {dest_path}.")
        return False
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def update_product_listing_page(file_path, category, products, settings, nav_links):
    if not os.path.exists(file_path):
        return
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    rel_path = os.path.relpath(file_path, WORKSPACE_DIR).replace("\\", "/")
    if len(html) < 1000:
        try:
            res = subprocess.run(["git", "show", f"HEAD:{rel_path}"], cwd=WORKSPACE_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and len(res.stdout) >= 1000:
                html = res.stdout.decode("utf-8", errors="ignore")
        except Exception:
            pass
    if len(html) < 1000:
        print(f"[-] Warning: base HTML for product listing {file_path} is too short ({len(html)} chars), skipping.")
        return
        
    subcats = get_product_subcategories(category)
    if subcats is None:
        cat_products = list(products)
    else:
        cat_products = [p for p in products if p.get('category') in subcats]
        
    cat_products.sort(key=lambda x: (x.get("sort", 99999) if isinstance(x.get("sort"), (int, float)) else 99999, x.get("id", "")))
    
    list_html = "\n"
    for i, p in enumerate(cat_products):
        detail_link = "./" + p["link"]
        image_path = "./" + p["image"]
        desc_clean = p.get("desc", "").strip(". ").strip()
        p_desc = f"\n      <p> {p['desc'][:80]}...<a href=\"{detail_link}\" target=\"_blank\" title=\"{p['title']}\">详情&gt;</a> </p>" if desc_clean else ""
        list_html += f"""    <dl> 
     <dt> 
      <a href="{detail_link}" target="_blank" title="{p['title']}"><img alt="{p['title']}" src="{image_path}"></a> 
      <div class="product-item-sample-caption" style="background: #f8fafc; text-align: center; font-size: 12px; color: #475569; padding: 5px 0; border-top: 1px solid #e2e8f0; line-height: 1.5; display: flex; align-items: center; justify-content: center; gap: 6px;">
        <span style="background: #e0f2fe; color: #0284c7; font-weight: 600; font-size: 11px; padding: 1px 6px; border-radius: 3px; border: 1px solid #bae6fd;">寄样图</span>
        <span>实物打样装规格</span>
      </div>
     </dt> 
     <dd> 
      <h4><a href="{detail_link}" target="_blank" title="{p['title']}">{p['title']}</a></h4> {p_desc}
     </dd> 
    </dl> 
"""
        if (i + 1) % 4 == 0 and (i + 1) < len(cat_products):
            list_html += "    <div class=\"clear\"></div>\n"
            
    list_html += "    "
    
    html = replace_group(r'(<div class="hyt-product-list-6">)(.*?)(<div class="clear"></div>\s*</div>)', list_html, html)
    
    # Clean pagination block so that it does not link to outdated static pages
    html = replace_group(r'(<div class="p102-pagination-1-main">)(.*?)(</div>)', '<a class="page_curr">1</a>', html)
        
    # Inject SEO tags into product listing page
    rel_path = os.path.relpath(file_path, WORKSPACE_DIR).replace("\\", "/")
    can_href_tags = generate_canonical_and_hreflang_tags(rel_path)
    html = inject_meta_block_into_head(html, can_href_tags, block_id="seo-canonical-hreflang")
    
    cat_title = f"{category}-美尔健生物"
    cat_desc = f"美尔健（深圳）生物科技有限公司官方{category}专区，提供高纯度研发及生产级原料供应与备案支持。"
    og_tags = generate_open_graph_tags(cat_title, cat_desc, "images/ban_txt.png", rel_path, og_type="website")
    html = inject_meta_block_into_head(html, og_tags, block_id="seo-opengraph")

    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, rel_path)
    
    # Clean trailing corrupted data if multiple </html> exist
    m_ends = list(re.finditer(r'</html>', html, re.I))
    if len(m_ends) > 1:
        html = html[:m_ends[0].end()]

    if len(html) < 1000:
        print(f"[-] Warning: generated HTML for product listing {file_path} is too short, refusing to write.")
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_article_listing_page(file_path, category, articles, settings, nav_links):
    if not os.path.exists(file_path):
        return
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    rel_path = os.path.relpath(file_path, WORKSPACE_DIR).replace("\\", "/")
    if len(html) < 1000:
        try:
            res = subprocess.run(["git", "show", f"HEAD:{rel_path}"], cwd=WORKSPACE_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and len(res.stdout) >= 1000:
                html = res.stdout.decode("utf-8", errors="ignore")
        except Exception:
            pass
    if len(html) < 1000:
        print(f"[-] Warning: base HTML for article listing {file_path} is too short ({len(html)} chars), skipping.")
        return
        
    subcats = get_article_subcategories(category)
    cat_articles = [a for a in articles if (a.get('category') in subcats or a.get('sub_category') in subcats or a.get('cat_name') in subcats) and a.get('show', True)]
    cat_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    if '<div class="hyt-product-list-5">' in html:
        # Case listing pages (article_hzal.html and its 8 industry subpages)
        list_html = "\n"
        display_arts = cat_articles[:30]
        for i, a in enumerate(display_arts):
            detail_link = "./" + a["link"].replace("\\", "/")
            image_path = "./" + a["image"].replace("\\", "/")
            desc = (a.get("desc") or "")[:120].strip()
            list_html += f"""   <dl> 
    <dt> 
     <a href="{detail_link}" target="_blank" title="{a['title']}"><img alt="{a['title']}" src="{image_path}"></a> 
    </dt> 
    <dd> 
     <h4><a href="{detail_link}" target="_blank" title="{a['title']}">{a['title']}</a></h4> 
     <p>{desc}...</p> 
     <a class="details" href="{detail_link}" target="_blank" title="{a['title']}"></a> 
    </dd> 
   </dl> 
"""
            if (i + 1) % 3 == 0 and (i + 1) < len(display_arts):
                list_html += '   <div class="clear"></div> \n'
        list_html += "  "
        pattern = r'(<div class="hyt-product-list-5">)(.*?)(</div>\s*<div class="clear"></div>\s*</div>)'
        html = replace_group(pattern, list_html, html)
    else:
        # News / Knowledge listing pages (article_xwzx.html, article_cjwt.html, etc.)
        list_html = "\n"
        for a in cat_articles:
            detail_link = "./" + a["link"].replace("\\", "/")
            image_path = "./" + a["image"].replace("\\", "/")
            desc = (a.get("desc") or "")[:100].strip()
            list_html += f"""   <dl> 
    <dt> 
     <a href="{detail_link}" target="_blank" title="{a['title']}"><img alt="{a['title']}" src="{image_path}" title="{a['title']}"></a> 
    </dt> 
    <dd> 
     <h4><a href="{detail_link}" target="_blank" title="{a['title']}">{a['title']}</a></h4> 
     <div class="p102-info-list-desc">
       {desc}... 
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


    # Update case subcategory navigation tabs (4 subcategories)
    if any(k in file_path for k in ["hzal", "syssj", "sysyanjiu", "khhz", "yycj", "ymxy", "yyxy", "hzp", "hfpgc", "gnlsp", "xhyp", "nxhlcp"]) or category in ["合作案例", "三方权威报告", "实验室研究数据", "客户合作", "应用场景", "实验室数据研究"]:
        nav_pattern = r'(<div class="p101a-fdh-02-nav"[^>]*>\s*<ul[^>]*>)([\s\S]*?)(</ul>\s*</div>)'
        
        cur_syssj = ' class="cur"' if category in ["三方权威报告", "实验室数据研究"] or "syssj" in file_path else ""
        cur_sysyanjiu = ' class="cur"' if category == "实验室研究数据" or "sysyanjiu" in file_path else ""
        cur_khhz = ' class="cur"' if category == "客户合作" or "khhz" in file_path else ""
        cur_yycj = ' class="cur"' if category == "应用场景" or "yycj" in file_path else ""
        
        case_tabs_html = f'''
     <li{cur_syssj}><a href="./article_syssj.html" title="三方权威报告">三方权威报告</a></li> 
     <li{cur_sysyanjiu}><a href="./article_sysyanjiu.html" title="实验室研究数据">实验室研究数据</a></li> 
     <li{cur_khhz}><a href="./article_khhz.html" title="客户合作">客户合作</a></li> 
     <li{cur_yycj}><a href="./article_yycj.html" title="应用场景">应用场景</a></li> 
    '''
        html = re.sub(nav_pattern, r'\1' + case_tabs_html + r'\3', html)
        
        # Update crumbs
        crumb_pattern = r'(<div class="p102-curmbs-1"[^>]*>[\s\S]*?<b>您当前的位置：</b>[\s\S]*?<a href="[^"]*index\.html"[^>]*>\s*首页\s*</a>\s*<span>\s*&gt;\s*</span>\s*)([\s\S]*?)(</div>)'
        if category == "合作案例":
            new_crumb = '<i> <a href="./article_hzal.html" title="合作案例"> 合作案例 </a> </i> '
        else:
            new_crumb = f'<i> <a href="./article_hzal.html" title="合作案例"> 合作案例 </a> </i> <span> &gt; </span> <i> {category} </i> '
        html = re.sub(crumb_pattern, r'\1' + new_crumb + r'\3', html)

        # Update H3
        h3_pattern = r'(<div class="p101a-fdh-02">[\s\S]*?<h3>)([\s\S]*?)(</h3>)'
        if category == "合作案例":
            html = re.sub(h3_pattern, r'\1合作案例\3', html)
        else:
            html = re.sub(h3_pattern, r'\1' + f'合作案例 · {category}' + r'\3', html)

    # Update news subcategory navigation tabs (全部, 企业新闻, 科普研究, 常见问答)
    if any(k in file_path for k in ["xwzx", "qydt", "cpbk", "cjwt"]) or category in ["新闻资讯", "企业新闻", "科普研究", "技术知识", "常见问答"]:
        nav_pattern = r'(<div class="p101a-fdh-02-nav"[^>]*>\s*<ul[^>]*>)([\s\S]*?)(</ul>\s*</div>)'
        
        cur_all = ' class="cur sidenavcur"' if "xwzx" in file_path and "000" not in file_path else ""
        cur_qydt = ' class="cur sidenavcur"' if "qydt" in file_path or category == "企业新闻" else ""
        cur_cpbk = ' class="cur sidenavcur"' if "cpbk" in file_path or category in ["科普研究", "技术知识"] else ""
        cur_cjwt = ' class="cur sidenavcur"' if "cjwt" in file_path or category == "常见问答" else ""
        if not (cur_all or cur_qydt or cur_cpbk or cur_cjwt):
            cur_all = ' class="cur sidenavcur"'
            
        news_tabs_html = f'''
     <li{cur_all}><a href="./article_xwzx.html" title="全部资讯">全部</a></li>
     <li{cur_qydt}><a href="./article_qydt.html" title="企业新闻">企业新闻</a></li>
     <li{cur_cpbk}><a href="./article_cpbk.html" title="科普研究">科普研究</a></li>
     <li{cur_cjwt}><a href="./article_cjwt.html" title="常见问答">常见问答</a></li>
    '''
        html = re.sub(nav_pattern, r'\1' + news_tabs_html + r'\3', html)
        
        # If cpbk, update title, H3, Baidu JSON-LD, and breadcrumb
        if "cpbk" in file_path or category in ["科普研究", "技术知识"]:
            html = re.sub(r'<title>.*?</title>', '<title>科普研究-美尔健生物</title>', html)
            html = re.sub(r'(<div class="p101a-fdh-02">[\s\S]*?<h3>)([\s\S]*?)(</h3>)', r'\1科普研究\3', html)
            crumb_pattern = r'(<div class="p102-curmbs-1"[^>]*>[\s\S]*?<b>您当前的位置：</b>[\s\S]*?<a href="[^"]*index\.html"[^>]*>\s*首页\s*</a>\s*<span>\s*&gt;\s*</span>\s*)([\s\S]*?)(</div>)'
            new_crumb = '<i> <a href="./article_xwzx.html" title="新闻中心"> 新闻中心 </a> <span> &gt; </span> </i> <i class=""> <a href="./article_cpbk.html" title="科普研究"> 科普研究 </a> </i> '
            html = re.sub(crumb_pattern, r'\1' + new_crumb + r'\3', html)
            html = html.replace('"title":"技术知识-美尔健生物"', '"title":"科普研究-美尔健生物"')

    # Inject SEO tags into article listing page
    rel_path = os.path.relpath(file_path, WORKSPACE_DIR).replace("\\", "/")
    can_href_tags = generate_canonical_and_hreflang_tags(rel_path)
    html = inject_meta_block_into_head(html, can_href_tags, block_id="seo-canonical-hreflang")
    
    cat_title = f"{category}-美尔健生物资讯中心"
    cat_desc = f"美尔健官方{category}专区，分享前沿生物科普研究、行业动态与问答。"
    og_tags = generate_open_graph_tags(cat_title, cat_desc, "images/ban_txt.png", rel_path, og_type="website")
    html = inject_meta_block_into_head(html, og_tags, block_id="seo-opengraph")

    # If FAQ page (cjwt), inject FAQPage schema
    if "cjwt" in file_path or category == "常见问答":
        faq_entities = []
        for a in cat_articles[:20]:
            ans_text = a.get("desc") or re.sub(r'<[^>]+>', '', a.get("content", ""))[:250]
            faq_entities.append({
                "@type": "Question",
                "name": a["title"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": ans_text.strip()
                }
            })
        if faq_entities:
            faq_ld = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_entities
            }
            html = inject_meta_block_into_head(
                html,
                f'<script type="application/ld+json">\n{json.dumps(faq_ld, ensure_ascii=False, indent=2)}\n</script>',
                block_id="schema-faqpage"
            )
        
    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, rel_path)
    
    if len(html) < 1000:
        print(f"[-] Warning: generated HTML for article listing {file_path} is too short ({len(html)} chars), refusing to write.")
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_single_homepage(file_path, products, articles, settings, friendlinks, nav_links, page_name="index.html"):
    if not os.path.exists(file_path):
        return
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    rel_path = os.path.relpath(file_path, WORKSPACE_DIR).replace("\\", "/")
    if len(html) < 1000:
        try:
            res = subprocess.run(["git", "show", f"HEAD:{rel_path}"], cwd=WORKSPACE_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and len(res.stdout) >= 1000:
                html = res.stdout.decode("utf-8", errors="ignore")
        except Exception:
            pass
    if len(html) < 1000:
        print(f"[-] Warning: base HTML for homepage {file_path} is too short ({len(html)} chars), skipping.")
        return
        
    # 1. Update Banners
    banner_html = "\n"
    for b in settings.get("banners", []):
        if b.get("type") == "video":
            banner_html += f"""    <div class="swiper-slide"> 
     <div class="ban_txt"> 
      <img src="./images/ban_txt.png"> 
     </div> 
     <video autoplay="" controls="" id="sVideo" loop="" muted="" playsinline="" webkit-playsinline="" x5-playsinline="" style="width: 100%; aspect-ratio: 1920 / 800; object-fit: cover; object-position: center;"> 
      <source src="{b.get('video', '')}" type="video/mp4"> 
     </video> 
    </div> 
"""
        else:
            banner_html += f"""     <div class="swiper-slide" data-swiper-autoplay="3000"> 
      <a href="./{b.get('link', '')}" title="{b.get('title', '')}"><img alt="{b.get('title', '')}" src="./{b.get('image', '')}" title="{b.get('title', '')}"></a> 
     </div> 
"""
    banner_html += "   "
    
    html = replace_group(r'(<div class="swiper-wrapper">)(.*?)(</div>\s*<div class="swiper-pagination">)', banner_html, html)
        
    # 2. Update Product Showcase (g_fa tabs)
    sorted_prods = sorted(products, key=lambda x: (x.get("sort", 99999) if isinstance(x.get("sort"), (int, float)) else 99999, x.get("id", "")))
    hzp = [p for p in sorted_prods if p.get('category') in get_product_subcategories("化妆品原料")][:5]
    yyy = [p for p in sorted_prods if p.get('category') in get_product_subcategories("医用原料")][:3]
    spy = [p for p in sorted_prods if p.get('category') in get_product_subcategories("食品营养原料")][:7]
    
    hzp_links = "\n         " + "\n          ".join([f'<a href="./{p["link"]}" title="{p["title"]}">{p["title"]} </a>' for p in hzp]) + "\n          "
    yyy_links = "\n         " + "\n          ".join([f'<a href="./{p["link"]}" title="{p["title"]}">{p["title"]} </a>' for p in yyy]) + "\n          "
    spy_links = "\n         " + "\n          ".join([f'<a href="./{p["link"]}" title="{p["title"]}">{p["title"]} </a>' for p in spy]) + "\n          "
    
    g_fa_pattern = r'(<div class="g_fa">.*?<div class="fa_links f_cb">)(.*?)(</div>.*?<div class="fa_links f_cb">)(.*?)(</div>.*?<div class="fa_links f_cb">)(.*?)(</div>.*?</div>\s*<div class="fa_b f_fw">)'
    m_fa = re.search(g_fa_pattern, html, re.DOTALL)
    if m_fa:
        html = (
            html[:m_fa.start(2)] + hzp_links +
            html[m_fa.end(2):m_fa.start(4)] + yyy_links +
            html[m_fa.end(4):m_fa.start(6)] + spy_links +
            html[m_fa.end(6):]
        )
        
    # 3. Update Product Carousel (idx-pro)
    pro_list_html = "\n"
    for i, p in enumerate(sorted_prods[:12]):
        pro_list_html += f"""     <div class="swiper-slide"> 
      <a href="./{p['link']}" title="{p['title']}"><img alt="{p['title']}" src="./{p['image']}"> 
       <div class="product-item-sample-caption" style="background: #f8fafc; text-align: center; font-size: 12px; color: #475569; padding: 5px 0; border-top: 1px solid #e2e8f0; line-height: 1.5; display: flex; align-items: center; justify-content: center; gap: 6px;">
        <span style="background: #e0f2fe; color: #0284c7; font-weight: 600; font-size: 11px; padding: 1px 6px; border-radius: 3px; border: 1px solid #bae6fd;">寄样图</span>
        <span>实物打样装规格</span>
       </div>
       <div class="txt"> 
        <h3>{p['title']}</h3> 
        <p>{p.get('desc', '')[:80]}...</p> 
        <span><b>MORE</b><i>&gt;&gt;</i></span> 
       </div> </a> 
     </div> 
"""
    pro_list_html += "    "
    html = replace_group(r'(<div class="idx-pro f_cb">.*?<div class="swiper-wrapper">)(.*?)(</div>\s*<div class="swiper-pagination">)', pro_list_html, html)
        
    # 4. Update Case Showcase (idx-anli)
    show_case = settings.get("show_case_section", True) is not False
    if not show_case:
        html = re.sub(r'<div class="idx-anli f_fw">[\s\S]*?<div class="idx-hezuo f_fw">', '<div class="idx-hezuo f_fw">', html)
    else:
        sorted_active_articles = sorted(
            [a for a in articles if a.get('show', True)],
            key=lambda x: x.get('date', ''),
            reverse=True
        )
        cases = [a for a in sorted_active_articles if a.get('category') in get_article_subcategories("合作案例")][:10]
        case_html = "\n"
        for a in cases:
            case_html += f"""     <div class="swiper-slide"> 
      <a href="./{a['link']}" title="{a['title']}"><img alt="{a['title']}" src="./{a['image']}"> 
       <div class="txt"> 
        <h3>{a['title']}</h3> 
        <p>{a.get('desc', '')[:100]}...</p> 
        <span><b>MORE</b><i>&gt;&gt;</i></span> 
       </div> </a> 
     </div> 
"""
        case_html += "    "
        html = replace_group(r'(<div class="idx-anli f_fw">.*?<div class="swiper-wrapper">)(.*?)(</div>\s*<div class="swiper-pagination">)', case_html, html)
        
    # 5. Update News Section
    sorted_active_articles = sorted(
        [a for a in articles if a.get('show', True)],
        key=lambda x: x.get('date', ''),
        reverse=True
    )
    qydt_news = [a for a in sorted_active_articles if a.get('category') in get_article_subcategories("企业新闻")][:4]
    cpbk_news = [a for a in sorted_active_articles if a.get('category') in get_article_subcategories("科普研究")][:4]
    cjwt_news = [a for a in sorted_active_articles if a.get('category') in get_article_subcategories("常见问答")][:4]
    
    def render_news_block(news_list, more_link="./article_xwzx.html"):
        if not news_list:
            return ""
        first = news_list[0]
        res = f"""\n      <div class="conl f_cb"> 
       <a href="./{first['link']}" title="{first['title']}"><img alt="{first['title']}" src="./{first['image']}"> 
        <div class="txt"> 
         <p>{first.get('date', '')}</p> 
         <h3>{first['title']}</h3> 
         <div>
           {first.get('desc', '')[:100]}... 
         </div> 
        </div> </a> 
      </div> 
      <div class="conr f_cb"> 
       <ul> \n"""
        for a in news_list[1:]:
            d_parts = a.get('date', '2025-01-01').split('-')
            d_str = d_parts[-1] if len(d_parts) > 0 else '01'
            m_str = f"{d_parts[0]}.{d_parts[1]}" if len(d_parts) > 1 else '2025.01'
            res += f"""        <li> <a href="./{a['link']}" title="{a['title']}"> 
          <div class="date"> 
           <h3>{d_str}</h3> 
           <p>{m_str}</p> 
          </div> 
          <div class="txt"> 
           <h4>{a['title']}</h4> 
           <p>{a.get('desc', '')[:80]}...</p> 
          </div> </a> </li> \n"""
        res += f"""       </ul> 
       <a class="more" href="{more_link}" title="查看更多">MORE &gt;&gt;</a> 
      </div> \n"""
        return res
        
    qydt_html = render_news_block(qydt_news, "./article_qydt.html")
    cpbk_html = render_news_block(cpbk_news, "./article_cpbk.html")
    cjwt_html = render_news_block(cjwt_news, "./article_cjwt.html")
    
    news_pattern = r'(<div class="tabsnew f_cb">.*?<div class="js-swiper-tab">.*?<div class="swiper-wrapper">.*?<div class="swiper-slide">\s*<div class="newcon">)(.*?)(</div>\s*</div>\s*<div class="swiper-slide">\s*<div class="newcon">)(.*?)(</div>\s*</div>\s*<div class="swiper-slide">\s*<div class="newcon">)(.*?)(</div>\s*</div>)'
    match = re.search(news_pattern, html, re.DOTALL)
    if match:
        html = (
            html[:match.start(2)] + qydt_html +
            html[match.end(2):match.start(4)] + cpbk_html +
            html[match.end(4):match.start(6)] + cjwt_html +
            html[match.end(6):]
        )
    html = re.sub(r'(<a[^>]*href="\./article_cpbk\.html"[^>]*>[\s\S]*?<em[^>]*>).*?(</em></a>)', r'\1科普研究\2', html)
    html = html.replace('alt="技术知识"', 'alt="科普研究"').replace('title="技术知识"', 'title="科普研究"')
        
    # 6. Update Friendship Links
    html = update_friendlinks(html, friendlinks)
    
    # 7. Apply contact updates
    html = update_global_contact_info(html, settings)
    
    # 8. Update navigation menu
    html = update_navigation(html, nav_links, page_name)
    
    if len(html) < 1000:
        print(f"[-] Warning: generated HTML for homepage {file_path} is too short ({len(html)} chars), refusing to write.")
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_homepage(products, articles, settings, friendlinks, nav_links):
    index_path = os.path.join(WORKSPACE_DIR, "index.html")
    if os.path.exists(index_path):
        try:
            update_single_homepage(index_path, products, articles, settings, friendlinks, nav_links, "index.html")
        except Exception as e_idx:
            print(f"[-] Error updating index.html homepage: {e_idx}")
            
    other_home = os.path.join(WORKSPACE_DIR, "mellgen_home.html")
    if os.path.exists(other_home):
        try:
            update_single_homepage(other_home, products, articles, settings, friendlinks, nav_links, "mellgen_home.html")
        except Exception as e_other:
            print(f"[-] Error updating mellgen_home.html homepage: {e_other}")

def update_all_footers_headers_and_nav(settings, nav_links):
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        dirs[:] = [d for d in dirs if d not in ['.git', 'en', 'cms_system', '.gemini', 'node_modules', '__pycache__'] and not d.startswith('backup')]
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    if len(content.strip()) < 500:
                        continue
                    
                    new_content = update_global_contact_info(content, settings)
                    
                    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
                    depth = len(rel_path.replace("\\", "/").split("/")) - 1
                    prefix = "../" * depth if depth > 0 else "./"

                    # Update footer case links (4 subcategories)
                    show_case = settings.get("show_case_section", True) is not False
                    footer_case_pattern = r'(<dl>\s*<dt>\s*<a href="[^"]*article_hzal\.html">[^<]*</a>\s*</dt>\s*<dd class="f_cb">)[\s\S]*?(</dd>\s*</dl>)'
                    if re.search(footer_case_pattern, new_content):
                        if show_case:
                            new_case_footer = f'''
         <a href="{prefix}article_syssj.html" title="三方权威报告">三方权威报告 </a> 
         <a href="{prefix}article_sysyanjiu.html" title="实验室研究数据">实验室研究数据 </a> 
         <a href="{prefix}article_khhz.html" title="客户合作">客户合作 </a> 
         <a href="{prefix}article_yycj.html" title="应用场景">应用场景 </a> 
       '''
                            new_content = re.sub(footer_case_pattern, r'\1' + new_case_footer + r'\2', new_content)
                        else:
                            new_content = re.sub(r'<dl>\s*<dt>\s*<a href="[^"]*article_hzal\.html">[^<]*</a>\s*</dt>\s*<dd class="f_cb">[\s\S]*?</dd>\s*</dl>', '', new_content)

                    # Update case tabs in case pages
                    if '<div class="p101a-fdh-02">' in new_content and any(k in file for k in ["hzal", "syssj", "sysyanjiu", "khhz", "yycj", "ymxy", "yyxy", "hzp", "hfpgc", "gnlsp", "xhyp", "nxhlcp"]):
                        tab_pat = r'(<div class="p101a-fdh-02-nav"[^>]*>\s*<ul[^>]*>)([\s\S]*?)(</ul>\s*</div>)'
                        cur_syssj = ' class="cur"' if "syssj" in file else ""
                        cur_sysyanjiu = ' class="cur"' if "sysyanjiu" in file else ""
                        cur_khhz = ' class="cur"' if "khhz" in file else ""
                        cur_yycj = ' class="cur"' if "yycj" in file else ""
                        new_tabs = f'''
     <li{cur_syssj}><a href="{prefix}article_syssj.html" title="三方权威报告">三方权威报告</a></li> 
     <li{cur_sysyanjiu}><a href="{prefix}article_sysyanjiu.html" title="实验室研究数据">实验室研究数据</a></li> 
     <li{cur_khhz}><a href="{prefix}article_khhz.html" title="客户合作">客户合作</a></li> 
     <li{cur_yycj}><a href="{prefix}article_yycj.html" title="应用场景">应用场景</a></li> 
    '''
                        new_content = re.sub(tab_pat, r'\1' + new_tabs + r'\3', new_content)

                    new_content = update_navigation(new_content, nav_links, rel_path)
                    
                    if new_content != content and len(new_content.strip()) >= 500:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"[-] Error updating header/footer in {file}: {e}")

def apply_page_seo(file_path, seo_title=None, seo_keywords=None, seo_description=None, settings=None):
    if not os.path.exists(file_path):
        return
    try:
        if settings is None:
            _, _, settings, _, _ = load_db()

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        if seo_title:
            html = re.sub(r'<title>[^<]*</title>', f'<title>{seo_title}</title>', html, flags=re.I)
        if seo_keywords:
            if re.search(r'<meta[^>]+name=["\']keywords["\']', html, re.I):
                html = re.sub(r'(<meta[^>]+name=["\']keywords["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{seo_keywords}{m.group(3)}', html, flags=re.I)
            else:
                html = re.sub(r'(<title>[^<]*</title>)', lambda m: f'{m.group(1)}\n  <meta name="keywords" content="{seo_keywords}">', html, flags=re.I)
        if seo_description:
            if re.search(r'<meta[^>]+name=["\']description["\']', html, re.I):
                html = re.sub(r'(<meta[^>]+name=["\']description["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{seo_description}{m.group(3)}', html, flags=re.I)
            else:
                html = re.sub(r'(<title>[^<]*</title>)', lambda m: f'{m.group(1)}\n  <meta name="description" content="{seo_description}">', html, flags=re.I)

        rel_path = os.path.relpath(file_path, WORKSPACE_DIR).replace("\\", "/")

        # 1. Canonical & Hreflang
        can_href_tags = generate_canonical_and_hreflang_tags(rel_path)
        html = inject_meta_block_into_head(html, can_href_tags, block_id="seo-canonical-hreflang")

        # 2. Open Graph & Twitter Cards
        curr_title = seo_title
        if not curr_title:
            tm = re.search(r'<title>([^<]+)</title>', html, re.I)
            curr_title = tm.group(1) if tm else settings.get("company_name", "美尔健生物")
            
        curr_desc = seo_description
        if not curr_desc:
            dm = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
            curr_desc = dm.group(1) if dm else settings.get("seo_description", "")
            
        og_tags = generate_open_graph_tags(curr_title, curr_desc, "images/ban_txt.png", rel_path, og_type="website")
        html = inject_meta_block_into_head(html, og_tags, block_id="seo-opengraph")

        # 3. Webmaster verification for root homepage
        if rel_path in ["index.html", "en/index.html", "mellgen_home.html"]:
            v_meta = generate_verification_meta(settings)
            if v_meta:
                html = inject_meta_block_into_head(html, v_meta, block_id="seo-webmaster-verification")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"[-] Error applying SEO to {file_path}: {e}")

def update_sitemaps(products, articles):
    sitemap_xml_path = os.path.join(WORKSPACE_DIR, "sitemap.xml")
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
    return xml

def generate_sitemap():
    products, articles, _, _, _ = load_db()
    return update_sitemaps(products, articles)

def publish_site():
    if not _publish_lock.acquire(blocking=False):
        print("[*] Site publishing is already in progress, skipping duplicate concurrent run.")
        return
    try:
        _do_publish_site()
    finally:
        _publish_lock.release()

def _do_publish_site():
    print("[*] Starting site regeneration and publishing...")
    products, articles, settings, friendlinks, nav_links = load_db()
    
    # 0. Immediate Homepage update (takes < 0.05s so changes reflect immediately on front-end)
    try:
        update_homepage(products, articles, settings, friendlinks, nav_links)
    except Exception as e_home0:
        print(f"[-] Error in Step 0 homepage update: {e_home0}")
        
    # Apply channel & innerpage SEO
    for ch in settings.get("channel_seo", []):
        ch_file = os.path.join(WORKSPACE_DIR, ch.get("url", ""))
        apply_page_seo(ch_file, ch.get("title"), ch.get("keywords"), ch.get("description"), settings)

    for ip in settings.get("inner_pages_seo", []):
        ip_file = os.path.join(WORKSPACE_DIR, ip.get("url", ""))
        apply_page_seo(ip_file, ip.get("title"), ip.get("keywords"), ip.get("description"), settings)

    # Apply default home SEO to index.html if not specified in channel_seo
    if settings.get("seo_title"):
        apply_page_seo(os.path.join(WORKSPACE_DIR, "index.html"), settings.get("seo_title"), settings.get("seo_keywords"), settings.get("seo_description"), settings)
    else:
        apply_page_seo(os.path.join(WORKSPACE_DIR, "index.html"), settings=settings)
    
    # 1. Update listing pages
    product_listing_configs = [
        ("product_index.html", "原料产品中心"),
        ("product_hzpyl.html", "化妆品原料"),
        ("product_tpxzzd.html", "高渗透型重组蛋白/多肽"),
        ("product_zwyhxw.html", "植物源活性物"),
        ("product_zzfsdb.html", "重组仿生蛋白"),
        ("product_hyyhxw.html", "海洋源活性物"),
        ("product_yejfjy.html", "婴儿菌发酵源活性物"),
        ("product_dwyhxw.html", "动物源活性物"),
        ("product_zzdb.html", "重组仿生蛋白"),
        ("product_fhyys.html", "细胞营养素"),
        ("product_lzdt.html", "植物源活性物"),
    ]
    for page_rel, cat_name in product_listing_configs:
        page_path = os.path.join(WORKSPACE_DIR, page_rel)
        if os.path.exists(page_path):
            update_product_listing_page(page_path, cat_name, products, settings, nav_links)

    # Clean legacy pagination files & legacy medical/food files so they redirect to canonical listing pages
    pagination_redirects = [
        ("product_yyyl.html", "./product_hzpyl.html"),
        ("product_spyyyl.html", "./product_hzpyl.html"),
        ("product_yyyl_0002.html", "./product_hzpyl.html"),
        ("product_spyyyl_0002.html", "./product_hzpyl.html"),
        ("en/product_yyyl.html", "./product_hzpyl.html"),
        ("en/product_spyyyl.html", "./product_hzpyl.html"),
        ("en/product_yyyl_0002.html", "./product_hzpyl.html"),
        ("en/product_spyyyl_0002.html", "./product_hzpyl.html"),
        ("product_index_0002.html", "./product_index.html"),
        ("product_index_0003.html", "./product_index.html"),
        ("product_hzpyl_0002.html", "./product_hzpyl.html"),
        ("product_hzpyl_0003.html", "./product_hzpyl.html"),
        ("product_tpxzzd_0002.html", "./product_tpxzzd.html"),
        ("en/product_index_0002.html", "./product_index.html"),
        ("en/product_index_0003.html", "./product_index.html"),
        ("en/product_hzpyl_0002.html", "./product_hzpyl.html"),
        ("en/product_hzpyl_0003.html", "./product_hzpyl.html"),
        ("en/product_tpxzzd_0002.html", "./product_tpxzzd.html"),
    ]
    for rel_f, target_url in pagination_redirects:
        p_path = os.path.join(WORKSPACE_DIR, rel_f)
        if os.path.exists(p_path):
            with open(p_path, "w", encoding="utf-8") as pf:
                pf.write(f'<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target_url}"><link rel="canonical" href="{target_url}"><script>location.replace("{target_url}");</script></head><body></body></html>')
    
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_xwzx.html"), "新闻资讯", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_hzal.html"), "合作案例", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_cjwt.html"), "常见问答", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_qydt.html"), "企业新闻", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_cpbk.html"), "科普研究", articles, settings, nav_links)
    
    # 合作案例 4大板块动态静态化
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_syssj.html"), "三方权威报告", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_sysyanjiu.html"), "实验室研究数据", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_khhz.html"), "客户合作", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_yycj.html"), "应用场景", articles, settings, nav_links)
    
    # 历史细分行业页面更新保持兼容
    for legacy_page, leg_cat in [
        ("article_ymxy.html", "客户合作"),
        ("article_yyxy.html", "客户合作"),
        ("article_hzp.html", "应用场景"),
        ("article_hfpgc.html", "客户合作"),
        ("article_gnlsp.html", "应用场景"),
        ("article_xhyp.html", "应用场景"),
        ("article_nxhlcp.html", "应用场景")
    ]:
        lp_path = os.path.join(WORKSPACE_DIR, legacy_page)
        if os.path.exists(lp_path):
            update_article_listing_page(lp_path, leg_cat, articles, settings, nav_links)
    
    # 2. Re-generate all product details
    all_articles_for_rec = []
    if os.path.exists(os.path.join(DATA_DIR, "articles.json")):
        with open(os.path.join(DATA_DIR, "articles.json"), "r", encoding="utf-8") as f:
            all_articles_for_rec = [a for a in json.load(f) if a.get("status") != "deleted" and not a.get("is_deleted")]

    template_product_path = os.path.join(WORKSPACE_DIR, "cms_system", "templates", "product_detail_template.html")
    if not os.path.exists(template_product_path) or os.path.getsize(template_product_path) < 1000:
        template_product_path = os.path.join(WORKSPACE_DIR, "products", "tphtct.html")
    if os.path.exists(template_product_path):
        with open(template_product_path, "r", encoding="utf-8") as tf:
            base_product_html = tf.read()
        if len(base_product_html) >= 1000:
            for p in products:
                try:
                    generate_product_detail_page(p, base_product_html, settings, nav_links, all_articles=all_articles_for_rec)
                except Exception as e:
                    print(f"[-] Error generating page for product {p['id']}: {e}")

        # Handle offline product pages: redirect them to product_index.html
        all_products_path = os.path.join(DATA_DIR, "products.json")
        if os.path.exists(all_products_path):
            try:
                with open(all_products_path, "r", encoding="utf-8") as f:
                    full_prods = json.load(f)
                for p in full_prods:
                    if p.get("show", True) is False or p.get("status") == "offline":
                        pid = p.get("id")
                        dest_path = os.path.join(WORKSPACE_DIR, "products", f"{pid}.html")
                        redirect_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=../product_index.html">
<link rel="canonical" href="https://www.mellgen.com/product_index.html">
<title>产品已下架 - 美尔健生物</title>
<script>location.replace("../product_index.html");</script>
</head>
<body>
<p>该产品已下架，正在跳转至<a href="../product_index.html">原料产品中心</a>...</p>
</body>
</html>'''
                        with open(dest_path, "w", encoding="utf-8") as pf:
                            pf.write(redirect_html)
            except Exception as e_off:
                print(f"[-] Notice handling offline products redirect: {e_off}")
                
    # 3. Re-generate all article details using dedicated template
    template_article_path = os.path.join(WORKSPACE_DIR, "cms_system", "templates", "article_detail_template.html")
    if not os.path.exists(template_article_path) or os.path.getsize(template_article_path) < 1000:
        template_article_path = os.path.join(WORKSPACE_DIR, "articles", "jsjjtp.html")
    if os.path.exists(template_article_path):
        with open(template_article_path, "r", encoding="utf-8") as tf:
            base_article_html = tf.read()
        if len(base_article_html) >= 1000:
            for a in articles:
                try:
                    generate_article_detail_page(a, base_article_html, settings, nav_links, all_online_articles=articles)
                except Exception as e:
                    print(f"[-] Error generating page for article {a['id']}: {e}")
        else:
            print(f"[-] Critical: base_article_html too short ({len(base_article_html)} chars), aborting article generation.")

        # Handle offline article pages: redirect them to article_xwzx.html so offline content is never displayed
        all_articles_path = os.path.join(DATA_DIR, "articles.json")
        if os.path.exists(all_articles_path):
            try:
                with open(all_articles_path, "r", encoding="utf-8") as f:
                    all_arts = json.load(f)
                offline_arts = [a for a in all_arts if not is_online_article(a, settings)]
                for oa in offline_arts:
                    oa_link = oa.get("link")
                    if oa_link:
                        oa_file = os.path.join(WORKSPACE_DIR, oa_link.replace("/", os.sep))
                        redirect_html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=../article_xwzx.html">
<link rel="canonical" href="https://www.mellgen.com/article_xwzx.html">
<title>文章已下架 - 美尔健生物</title>
<script>location.replace("../article_xwzx.html");</script>
</head>
<body>
<p>该文章已下架，正在跳转至<a href="../article_xwzx.html">新闻中心</a>...</p>
</body>
</html>'''
                        if os.path.exists(oa_file):
                            with open(oa_file, "w", encoding="utf-8") as oaf:
                                oaf.write(redirect_html)
                        en_oa_file = os.path.join(WORKSPACE_DIR, "en", oa_link.replace("/", os.sep))
                        if os.path.exists(en_oa_file):
                            with open(en_oa_file, "w", encoding="utf-8") as eoaf:
                                eoaf.write(redirect_html)
            except Exception as e_art_off:
                print(f"[-] Notice handling offline articles redirect: {e_art_off}")
                
    # 4. Update homepage structures (updates both index.html and mellgen_home.html)
    update_homepage(products, articles, settings, friendlinks, nav_links)
            
    # 4.5. Synchronize published videos to front-end pages
    try:
        import video_manager
        video_manager.sync_videos_to_html()
    except Exception as e:
        print(f"[-] Notice on video sync: {e}")

    # 5. Global footer/header/nav propagates
    update_all_footers_headers_and_nav(settings, nav_links)
    
    # 6. Sitemaps
    update_sitemaps(products, articles)
    
    # 7. Auto-sync English site & Language switchers
    try:
        import sys
        scripts_dir = os.path.join(WORKSPACE_DIR, "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import build_full_en_site
        build_full_en_site.main()
        import generate_en_product_pages
        generate_en_product_pages.main()
        import deep_translate_en
        deep_translate_en.main()
        import clean_100_percent_en
        clean_100_percent_en.main()
    except Exception as e:
        print(f"[-] Notice on English site sync: {e}")
        
    # 8. Universal Canonical, Hreflang & Verification sweep on ALL generated HTML files
    print("[*] Performing universal Canonical, Hreflang & Verification sweep...")
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        dirs[:] = [d for d in dirs if d not in ['.git', 'cms_system', '.gemini', 'node_modules', '__pycache__'] and not d.startswith('backup')]
        for file in files:
            if file.endswith('.html'):
                fpath = os.path.join(root, file)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        f_html = f.read()
                    r_path = os.path.relpath(fpath, WORKSPACE_DIR).replace("\\", "/")
                    new_f_html = inject_meta_block_into_head(f_html, generate_canonical_and_hreflang_tags(r_path), block_id="seo-canonical-hreflang")
                    if r_path in ["index.html", "en/index.html", "mellgen_home.html"]:
                        v_tags = generate_verification_meta(settings)
                        if v_tags:
                            new_f_html = inject_meta_block_into_head(new_f_html, v_tags, block_id="seo-webmaster-verification")
                    if new_f_html != f_html:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(new_f_html)
                except Exception as e:
                    print(f"[-] Notice on sweep for {file}: {e}")

    print("[OK] Site publishing complete!")

# Alias build_all to publish_site for backward compatibility
build_all = publish_site

if __name__ == "__main__":
    publish_site()


