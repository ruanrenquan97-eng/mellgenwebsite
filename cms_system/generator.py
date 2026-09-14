import os
import re
import json
import shutil
from urllib.parse import urlparse

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    
    address_val = settings.get("address", "")
    if address_val:
        html_content = re.sub(r'广东省深圳市大鹏新区葵涌街道生命科学产业园(?:B1栋)*', address_val, html_content)
    
    html_content = html_content.replace("61791579@qq.com", settings.get("email", ""))
    html_content = html_content.replace("邮箱：61791579@qq.com", "邮箱：" + settings.get("email", ""))
    
    html_content = html_content.replace("61791579", settings.get("qq", ""))
    
    return html_content

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
            nav_html += f'     <li class="is-sub-item" style="display:none;"> <a href="{child_url}" title="{child["name"]}"> &nbsp;&nbsp;├ {child["name"]} </a> </li> \n'

    for item in nav_links:
        process_item(item)
        
    nav_html += "   "
    
    pattern = r'(<div class="[^"]*menu[^"]*">.*?<ul>)(.*?)(</ul>)'
    if re.search(pattern, html_content, re.DOTALL):
        html_content = replace_group(pattern, nav_html, html_content, group_index=2)
    return html_content

DEFAULT_DISCLAIMER = """【法规合规与专业同行免责声明】
1. 本网页展示的所有原料产品技术参数、活性机理、科研实验数据（包括细胞实验、生化模型等体外数据）及相关文献资料，仅供化妆品品牌方研发工程师、配方师、产品策划及高校科研机构进行同行专业技术探讨与配方研发参考，并非针对终端消费者的产品功效宣称、商业承诺或医疗建议。
2. 根据《化妆品监督管理条例》、《化妆品功效宣称评价规范》等相关法律法规，使用本原料的化妆品成品企业应独立对其终产品的安全性、稳定性和功效宣称负责，并依法完成终产品的功效宣称评价与国家药监局备案/注册申报，不得直接将本技术资料中有关原料的体外/细胞实验结论直接作为终端化妆品功效依据。
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
        out.append('      <span style="color: #ccfbf1; font-size: 12px;">药监报送码 · 现货起订 · 索样支持 · 资质随货</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px;">')
        out.append('      <table style="width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155;">')
        
        proc_items = [
            ("药监局原料报送码", proc.get("nmpa_code"), "供货包装规格", proc.get("packaging")),
            ("最小起订量 (MOQ)", proc.get("moq"), "供货交期", proc.get("lead_time")),
            ("储存条件", proc.get("storage"), "保质期 (Shelf Life)", proc.get("shelf_life")),
            ("研发索样支持", proc.get("sample_policy"), "随货资质报告", proc.get("qualifications")),
        ]
        
        for label1, val1, label2, val2 in proc_items:
            if val1 or val2:
                val1_display = f'<span style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; color: #047857; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-family: monospace; border: 1px solid #a7f3d0;">✓ {val1}</span>' if label1 == "药监局原料报送码" and val1 else (val1 or "—")
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
            claims_tags = [f'<span style="background: #f1f5f9; color: #1e293b; padding: 4px 12px; border-radius: 100px; font-size: 12.5px; font-weight: 600; border: 1px solid #cbd5e1;">🏷️ {c.strip()}</span>' for c in mkt.get("claims").replace('，', ',').replace('、', ',').split(',') if c.strip()]
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 700; color: #1e293b;">✨ 核心功效宣称关键词：</h5>')
            out.append(f'        <div style="display: flex; flex-wrap: wrap; gap: 8px;">{"".join(claims_tags)}</div>')
            out.append('      </div>')
            
        if mkt.get("applications"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">🧴 推荐适用产品品类与剂型：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{mkt.get("applications")}</p>')
            out.append('      </div>')
            
        if mkt.get("patents"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">📜 专利技术背书与科研合作：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{mkt.get("patents")}</p>')
            out.append('      </div>')
            
        out.append('    </div>')
        out.append('  </div>')

    # 4. 法规合规与免责声明
    out.append('  <!-- 法规合规与免责声明 -->')
    out.append('  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #174778; border-radius: 6px; padding: 20px 24px; margin-top: 25px;">')
    out.append('    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">')
    out.append('      <span style="font-size: 16px;">⚖️</span>')
    out.append('      <h4 style="margin: 0; font-size: 14.5px; font-weight: 700; color: #1e293b; letter-spacing: 0.3px;">国家法规合规与专业同行免责声明</h4>')
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

def generate_product_detail_page(product, base_template_html, settings, nav_links):
    dest_path = os.path.join(WORKSPACE_DIR, product['link'].replace('/', os.sep))
    if os.path.exists(dest_path):
        with open(dest_path, "r", encoding="utf-8") as f:
            html = f.read()
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

    cat = product['category']
    cat_filename = "product_hzpyl.html"
    if cat in ["医用原料", "重组蛋白", "动物源活性物", "活性抗菌材料"]:
        cat_filename = "product_yyyl.html"
    elif cat in ["食品营养原料", "桃胶多糖", "水母胶原", "灵芝黄酮", "灵芝多糖", "人参多肽", "复合营养素", "婴儿源益生菌"]:
        cat_filename = "product_spyyyl.html"

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
    
    # Update Image
    img_pattern = r'(<div class="p102-proShow-1-pic">.*?<img alt=")(.*?)(" src=")(.*?)(")'
    match = re.search(img_pattern, html, re.DOTALL)
    if match:
        html = (
            html[:match.start(2)] + product["title"] +
            html[match.end(2):match.start(4)] + f"../{product['image']}" +
            html[match.end(4):]
        )
    
    # Render B2B sections (R&D, Procurement, Marketing, Disclaimer)
    b2b_html = render_product_b2b_sections(product)
    
    # Clean any and all previous B2B sections first
    b2b_clean_pattern = r'<!-- ==================== B2B PROFESSIONAL DOSSIER & DISCLAIMER ==================== -->[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->'
    html = re.sub(b2b_clean_pattern, '', html)

    full_content = f"{product['content']}\n{b2b_html}" if product.get("content") else b2b_html
    content_pattern1 = r'(<div class="p102-pro-content-desc endit-content">)(.*?)(</div>\s*</div>\s*</div>\s*<div class="k12-cx-xgcp-4pl-fx1-1-01)'
    content_pattern2 = r'(<div class="p102-pro-content-desc endit-content">)(.*?)(</div>\s*<!--)'
    if re.search(content_pattern1, html, re.DOTALL):
        html = replace_group(content_pattern1, f"\n     {full_content}\n    ", html)
    elif re.search(content_pattern2, html, re.DOTALL):
        html = replace_group(content_pattern2, f"\n     {full_content}\n    ", html)
    else:
        end_pattern = r'(</div>\s*</div>\s*</div>\s*<div class="k12-cx-xgcp-4pl-fx1-1-01)'
        if re.search(end_pattern, html):
            html = re.sub(end_pattern, lambda m: f"\n{full_content}\n    " + m.group(1), html, count=1)

    html = update_global_contact_info(html, settings)
    
    # Update navigation menu
    html = update_navigation(html, nav_links, product['link'])
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)

def generate_article_detail_page(article, base_template_html, settings, nav_links):
    html = base_template_html
    
    art_title = f"{article['title']}-新闻资讯-{settings.get('company_name', '美尔健生物')}"
    html = re.sub(r'<title>[^<]+</title>', f"<title>{art_title}</title>", html)
    
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
    
    content_pattern = r'(<div class="p102-info-content endit-content">)(.*?)(</div>\s*<div class="clear"></div>)'
    
    # Normalize relative image paths based on target page depth
    art_content = article.get("content", "")
    rel_depth = article.get("link", "").count("/")
    root_prefix = "../" * rel_depth if rel_depth > 0 else "./"
    art_content = re.sub(r'src=["\'](?:\.\./)*resource/images/', f'src="{root_prefix}resource/images/', art_content)
    art_content = re.sub(r'src=["\'](?:\.\./)*images/', f'src="{root_prefix}images/', art_content)
    
    if re.search(content_pattern, html, re.DOTALL):
        html = replace_group(content_pattern, f"\n     {art_content}\n    ", html)
    else:
        alt_pattern = r'(<div class="p102-info-content[^"]*">)(.*?)(</div>\s*<div class="clear"></div>)'
        if re.search(alt_pattern, html, re.DOTALL):
            html = replace_group(alt_pattern, f"\n     {art_content}\n    ", html)

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
        desc_clean = p.get("desc", "").strip(". ").strip()
        p_desc = f"\n      <p> {p['desc'][:80]}...<a href=\"{detail_link}\" target=\"_blank\" title=\"{p['title']}\">详情&gt;</a> </p>" if desc_clean else ""
        list_html += f"""    <dl> 
     <dt> 
      <a href="{detail_link}" target="_blank" title="{p['title']}"><img alt="{p['title']}" src="{image_path}"></a> 
     </dt> 
     <dd> 
      <h4><a href="{detail_link}" target="_blank" title="{p['title']}">{p['title']}</a></h4> {p_desc}
     </dd> 
    </dl> 
"""
        if (i + 1) % 3 == 0 and (i + 1) < len(cat_products):
            list_html += "    <div class=\"clear\"></div>\n"
            
    list_html += "    "
    
    html = replace_group(r'(<div class="hyt-product-list-6">)(.*?)(<div class="clear"></div>\s*</div>)', list_html, html)
        
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
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_article_listing_page(file_path, category, articles, settings, nav_links):
    if not os.path.exists(file_path):
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    subcats = get_article_subcategories(category)
    cat_articles = [a for a in articles if a.get('category') in subcats and a.get('show', True)]
    cat_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    if '<div class="hyt-product-list-5">' in html:
        # Case listing pages (article_hzal.html and its 7 industry subpages)
        list_html = "\n"
        display_arts = cat_articles[:12]
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

    # Inject SEO tags into article listing page
    rel_path = os.path.relpath(file_path, WORKSPACE_DIR).replace("\\", "/")
    can_href_tags = generate_canonical_and_hreflang_tags(rel_path)
    html = inject_meta_block_into_head(html, can_href_tags, block_id="seo-canonical-hreflang")
    
    cat_title = f"{category}-美尔健生物资讯中心"
    cat_desc = f"美尔健官方{category}专区，分享前沿生物技术知识、行业动态与问答。"
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
        dirs[:] = [d for d in dirs if d not in ['.git', 'en', 'cms_system', '.gemini', 'node_modules', '__pycache__'] and not d.startswith('backup')]
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

def apply_page_seo(file_path, seo_title=None, seo_keywords=None, seo_description=None, settings=None):
    if not os.path.exists(file_path):
        return
    try:
        if settings is None:
            _, _, settings, _, _ = load_db()

        with open(file_path, "r", encoding="utf-8") as f:
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
    print("[*] Starting site regeneration and publishing...")
    products, articles, settings, friendlinks, nav_links = load_db()
    
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
    update_product_listing_page(os.path.join(WORKSPACE_DIR, "product_hzpyl.html"), "化妆品原料", products, settings, nav_links)
    update_product_listing_page(os.path.join(WORKSPACE_DIR, "product_yyyl.html"), "医用原料", products, settings, nav_links)
    update_product_listing_page(os.path.join(WORKSPACE_DIR, "product_spyyyl.html"), "食品营养原料", products, settings, nav_links)
    
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_xwzx.html"), "新闻资讯", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_hzal.html"), "合作案例", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_cjwt.html"), "常见问答", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_qydt.html"), "企业新闻", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_cpbk.html"), "技术知识", articles, settings, nav_links)
    
    # 合作案例 7大细分行业页面动态静态化
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_ymxy.html"), "医美行业", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_yyxy.html"), "医药行业", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_hzp.html"), "化妆品", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_hfpgc.html"), "护肤品工厂", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_gnlsp.html"), "功能类食品", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_xhyp.html"), "洗护用品", articles, settings, nav_links)
    update_article_listing_page(os.path.join(WORKSPACE_DIR, "article_nxhlcp.html"), "女性护理产品", articles, settings, nav_links)
    
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


