# -*- coding: utf-8 -*-
"""
Full-scale generator for all 37 Mellgen B2B raw material products:
- Chinese pages: products/{id}.html
- English pages: en/products/{id}.html
- Chinese & English product catalog index and category pages
"""

import os
import re
import json
from bs4 import BeautifulSoup

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_DIR, "cms_system", "cms_data")
ZH_JSON_PATH = os.path.join(DATA_DIR, "products.json")
EN_JSON_PATH = os.path.join(DATA_DIR, "products_en.json")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
NAV_PATH = os.path.join(DATA_DIR, "nav.json")

def load_data():
    with open(ZH_JSON_PATH, "r", encoding="utf-8") as f:
        zh_products = json.load(f)
    with open(EN_JSON_PATH, "r", encoding="utf-8") as f:
        en_products = json.load(f)
    settings = {}
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    nav_links = []
    if os.path.exists(NAV_PATH):
        with open(NAV_PATH, "r", encoding="utf-8") as f:
            nav_links = json.load(f)
    return zh_products, en_products, settings, nav_links

def render_b2b_dossier_zh(p):
    rd = p.get("rd_info") or {}
    proc = p.get("procurement_info") or {}
    mkt = p.get("marketing_info") or {}
    disclaimer = p.get("disclaimer") or ""

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

    # 1. 生物科技机理与实验佐证（源自2026官方画册）
    diagram_img = p.get("diagram_image")
    diagram_cap = p.get("diagram_caption", "")
    if diagram_img:
        out.append('  <!-- 1. 生物科技机理与实验佐证 -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">📊</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">生物科技机理与实验佐证 (Biotechnology Mechanism &amp; Evidence)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #dbeafe; font-size: 12px;">官方权威画册图谱 · 结构解析 · 促透与功效机理</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px; text-align: center; background: #f8fafc;">')
        out.append('      <div style="display: inline-block; max-width: 100%; background: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">')
        out.append(f'        <img src="../{diagram_img}" alt="{diagram_cap}" style="max-width: 100%; max-height: 480px; object-fit: contain; border-radius: 6px; display: block; margin: 0 auto; box-shadow: 0 1px 4px rgba(0,0,0,0.08);">')
        out.append(f'        <p style="margin: 14px 0 4px 0; font-size: 13.5px; color: #334155; font-weight: 600; line-height: 1.6; text-align: center;">')
        out.append(f'          <span style="display: inline-block; background: #eff6ff; color: #1d4ed8; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 8px; border: 1px solid #bfdbfe;">机理与实验图谱</span>{diagram_cap}')
        out.append('        </p>')
        out.append('      </div>')
        out.append('    </div>')
        out.append('  </div>')

    # 2. 研发配方工程师专区
    if has_rd:
        out.append('  <!-- 研发配方工程师专区 -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #174778 0%, #1d5b99 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">🔬</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">配方研发工程师指南 (R&amp;D Technical Dossier)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #93c5fd; font-size: 12px;">配方应用 · 理化参数 · 稳定性与配伍</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px;">')
        out.append('      <table style="width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155;">')

        rd_items = [
            ("INCI名称（中文）", rd.get("inci_cn"), "INCI名称（英文）", rd.get("inci_en")),
            ("CAS号", rd.get("cas"), "建议添加量", rd.get("dosage")),
            ("最佳pH范围", rd.get("ph_range"), "耐热性与工艺", rd.get("heat_tolerance")),
            ("外观与气味", rd.get("appearance"), "溶解性与配制", rd.get("solubility")),
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
            out.append(f'        <strong>💡 配伍禁忌与工艺指导：</strong>{rd.get("compatibility")}')
            out.append('      </div>')

        out.append('    </div>')
        out.append('  </div>')

    # 3. 采购与供应链专区
    if has_proc:
        out.append('  <!-- 采购与供应链专区 -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">📦</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">采购与供应链准入档案 (Procurement &amp; Compliance)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #ccfbf1; font-size: 12px;">国家药监局报送码 · MOQ · 打样支持 · 质检资质</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px;">')
        out.append('      <table style="width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155;">')

        code_val = proc.get("nmpa_code") or proc.get("submission_code")
        proc_items = [
            ("国家药监局报送码", code_val, "包装规格", proc.get("packaging")),
            ("起订量 (MOQ)", proc.get("moq"), "供货周期", proc.get("lead_time")),
            ("储存条件", proc.get("storage"), "保质期", proc.get("shelf_life")),
            ("打样支持", proc.get("sample_policy"), "资质文件", proc.get("qualifications")),
        ]

        for label1, val1, label2, val2 in proc_items:
            if val1 or val2:
                val1_display = f'<span style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; color: #047857; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-family: monospace; border: 1px solid #a7f3d0;">✓ {val1}</span>' if label1 == "国家药监局报送码" and val1 else (val1 or "—")
                out.append('        <tr style="border-bottom: 1px solid #f1f5f9;">')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 15%; font-weight: 600; color: #475569; white-space: nowrap;">{label1}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 35%; color: #1e293b;">{val1_display}</td>')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 15%; font-weight: 600; color: #475569; white-space: nowrap;">{label2}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 35%; color: #1e293b;">{val2 or "—"}</td>')
                out.append('        </tr>')

        out.append('      </table>')
        out.append('    </div>')
        out.append('  </div>')

    # 4. 产品策划专区
    if has_mkt:
        out.append('  <!-- 产品策划专区 -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #b45309 0%, #d97706 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">💡</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">产品策划与核心卖点 (Product Planning &amp; Marketing Highlights)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #fef3c7; font-size: 12px;">核心机理 · 卖点宣称 · 推荐剂型 · 专利文献佐证</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px; display: flex; flex-direction: column; gap: 16px;">')

        if mkt.get("mechanism"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">🧬 核心生物技术壁垒与作用机制：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; line-height: 1.7; color: #475569; background: #fffbeb; padding: 12px 16px; border-radius: 6px; border: 1px solid #fef3c7;">{mkt.get("mechanism")}</p>')
            out.append('      </div>')

        if mkt.get("claims"):
            claims_tags = [f'<span style="background: #f1f5f9; color: #1e293b; padding: 4px 12px; border-radius: 100px; font-size: 12.5px; font-weight: 600; border: 1px solid #cbd5e1;">🏷️ {c.strip()}</span>' for c in mkt.get("claims").split(',') if c.strip()]
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 700; color: #1e293b;">✨ 核心卖点关键词：</h5>')
            out.append(f'        <div style="display: flex; flex-wrap: wrap; gap: 8px;">{"".join(claims_tags)}</div>')
            out.append('      </div>')

        if mkt.get("applications"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">🧴 推荐开发剂型与产品线：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{mkt.get("applications")}</p>')
            out.append('      </div>')

        if mkt.get("patents"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">📜 专利技术与文献佐证：</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{mkt.get("patents")}</p>')
            out.append('      </div>')

        out.append('    </div>')
        out.append('  </div>')

    # 5. 监管合规与声明
    out.append('  <!-- 监管合规与声明 -->')
    out.append('  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #174778; border-radius: 6px; padding: 20px 24px; margin-top: 25px;">')
    out.append('    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">')
    out.append('      <span style="font-size: 16px;">⚖️</span>')
    out.append('      <h4 style="margin: 0; font-size: 14.5px; font-weight: 700; color: #1e293b; letter-spacing: 0.3px;">监管合规与同行技术探讨免责声明</h4>')
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

def generate_zh_product_detail(product):
    pid = product["id"]
    dest_path = os.path.join(WORKSPACE_DIR, "products", f"{pid}.html")
    template_path = os.path.join(WORKSPACE_DIR, "products", "tphtct.html")

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Clean existing B2B section from template
    html = re.sub(r'<!-- ==================== B2B PROFESSIONAL DOSSIER & DISCLAIMER ==================== -->[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->', '', html)
    html = re.sub(r'<div class="mellgen-b2b-section"[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->', '', html)

    # 1. SEO Title & Meta
    seo_title = f"{product['title']} - 医用原料/化妆品原料供应商 - 美尔健（深圳）生物科技有限公司"
    html = re.sub(r'<title>[^<]+</title>', f"<title>{seo_title}</title>", html)
    if product.get("desc"):
        html = re.sub(r'(<meta[^>]+name=["\']description["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{product["desc"]}{m.group(3)}', html, flags=re.I)
    html = re.sub(r'(<meta[^>]+name=["\']keywords["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{product["title"]},{product["category"]},生物原料,美尔健生物{m.group(3)}', html, flags=re.I)

    # Canonical & Hreflang
    canonical_block = f'''<!-- [seo-canonical-hreflang] -->
  <link rel="canonical" href="https://www.mellgen.com/products/{pid}.html">
  <link rel="alternate" hreflang="zh-CN" href="https://www.mellgen.com/products/{pid}.html">
  <link rel="alternate" hreflang="en" href="https://www.mellgen.com/en/products/{pid}.html">
  <link rel="alternate" hreflang="x-default" href="https://www.mellgen.com/products/{pid}.html">
  <!-- [/seo-canonical-hreflang] -->'''
    html = re.sub(r'<!-- \[seo-canonical-hreflang\] -->[\s\S]*?<!-- \[/seo-canonical-hreflang\] -->', canonical_block, html)

    # OpenGraph & Twitter
    og_image = f"https://www.mellgen.com/{product['image'].lstrip('/')}"
    og_block = f'''<!-- [seo-opengraph] -->
  <meta property="og:type" content="product">
  <meta property="og:title" content="{product['title']} - 医用原料/化妆品原料供应商 - 美尔健（深圳）生物科技有限公司">
  <meta property="og:description" content="{product.get('desc', '')[:150]}">
  <meta property="og:url" content="https://www.mellgen.com/products/{pid}.html">
  <meta property="og:site_name" content="美尔健生物 | Mellgen Bio">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{product['title']} - 医用原料/化妆品原料供应商 - 美尔健（深圳）生物科技有限公司">
  <meta name="twitter:description" content="{product.get('desc', '')[:150]}">
  <meta name="twitter:image" content="{og_image}">
  <!-- [/seo-opengraph] -->'''
    html = re.sub(r'<!-- \[seo-opengraph\] -->[\s\S]*?<!-- \[/seo-opengraph\] -->', og_block, html)

    # Schema JSON-LD
    schema_block = f'''<!-- [schema-jsonld] -->
  <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Product",
      "name": "{product['title']}",
      "description": "{product.get('desc', '')}",
      "category": "{product['category']}",
      "url": "https://www.mellgen.com/products/{pid}.html",
      "image": "{og_image}",
      "brand": {{
        "@type": "Brand",
        "name": "美尔健（深圳）生物科技有限公司"
      }},
      "manufacturer": {{
        "@type": "Organization",
        "name": "美尔健（深圳）生物科技有限公司",
        "url": "https://www.mellgen.com"
      }},
      "offers": {{
        "@type": "Offer",
        "availability": "https://schema.org/InStock",
        "priceCurrency": "CNY",
        "price": "0",
        "url": "https://www.mellgen.com/products/{pid}.html"
      }}
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "首页",
          "item": "https://www.mellgen.com/"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "{product['category']}",
          "item": "https://www.mellgen.com/product_hzpyl.html"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": "{product['title']}",
          "item": "https://www.mellgen.com/products/{pid}.html"
        }}
      ]
    }}
  ]
}}
  </script>
  <!-- [/schema-jsonld] -->'''
    html = re.sub(r'<!-- \[schema-jsonld\] -->[\s\S]*?<!-- \[/schema-jsonld\] -->', schema_block, html)

    # 2. Breadcrumbs
    cat_filename = "product_hzpyl.html"
    cat = product["category"]
    if cat in ["医用原料", "重组蛋白"]:
        cat_filename = "product_yyyl.html"
    elif cat in ["食品营养原料", "复合营养素"]:
        cat_filename = "product_spyyyl.html"

    crumbs_html = f'''<div class="p102-curmbs-1" navcrumbs=""> 
    <b>您当前的位置：</b> 
    <a href="../index.html" title="首页"> 首页 </a> 
    <span> &gt; </span> 
    <i class=""> <a href="../product_index.html" title="产品频道"> 产品频道 </a> <span> &gt; </span> </i> 
    <i class="p12-curblock"> <a href="../{cat_filename}" title="{product['category']}">{product['category']}</a> <span> &gt; </span> </i> 
    <i class=""> <a href="../products/{pid}.html" title="{product['title']}"> {product['title']} </a> </i> 
  </div>'''
    html = re.sub(r'<div class="p102-curmbs-1"[^>]*>.*?</div>', crumbs_html, html, flags=re.DOTALL)

    # 3. Product Title & Subtitle
    html = re.sub(r'<div class="p102-proShow-1-text">\s*<h1[^>]*>.*?</h1>\s*<p>.*?</p>', f'<div class="p102-proShow-1-text">\n      <h1 title="{product["title"]}" class="p102-proShow-1-title">\n        {product["title"]} \n      </h1> \n      <p>{product["category"]}</p>', html, flags=re.DOTALL)

    # Left Column (Image & Sample Box)
    clean_left_block_zh = f'''<div class="p102-proShow-1-left">
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
   </div>'''
    left_pattern = r'<div class="p102-proShow-1-left"[^>]*>[\s\S]*?(?=\s*<div class="p102-proShow-1-right">)'
    if re.search(left_pattern, html):
        html = re.sub(left_pattern, clean_left_block_zh, html)

    # 4. Top Specs Box
    rd = product.get("rd_info", {})
    specs_p_html = []
    if product.get("desc"):
        specs_p_html.append(f'<p style="line-height: 1.6; margin-bottom: 8px; color: #475569; font-size: 13.5px;">{product["desc"]}</p>')
    inci = rd.get("inci_cn") or product.get("specs", {}).get("INCI中文")
    if inci:
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>INCI名称：</strong>{inci}</p>')
    app_val = rd.get("appearance") or product.get("specs", {}).get("外观性状")
    sol_val = rd.get("solubility") or product.get("specs", {}).get("溶解性")
    if app_val or sol_val:
        app_sol = f"{app_val or ''}，{sol_val or ''}".strip('， ')
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>性状及溶解性：</strong>{app_sol}</p>')
    dosage = rd.get("dosage") or product.get("specs", {}).get("建议添加量")
    if dosage:
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>建议添加量：</strong>{dosage}</p>')

    top_specs_content = "\n" + "\n".join(specs_p_html) + "\n "
    desc_box_pattern = r'(<div class="p102-proShow-1-desc">)(.*?)(</div>\s*<div class="p102-proShow-1-tel">)'
    if re.search(desc_box_pattern, html, re.DOTALL):
        html = re.sub(desc_box_pattern, r'\1' + top_specs_content.replace('\\', '\\\\') + r'\3', html, flags=re.DOTALL)

    # 5. Render B2B Dossier
    b2b_html_zh = render_b2b_dossier_zh(product)
    intro_p = product.get("content", f"<p>{product.get('desc')}</p>")

    # Add intro illustration image card (animal/plant source, mechanism, or data chart)
    intro_img = product.get("intro_image")
    intro_tag = product.get("intro_image_tag", "技术图谱")
    intro_cap = product.get("intro_image_caption", "")
    intro_img_html = ""
    if intro_img:
        intro_img_html = f'''
      <div class="product-intro-image-card" style="margin: 28px auto 25px auto; text-align: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 22px; box-shadow: 0 2px 12px rgba(0,0,0,0.03); max-width: 820px; box-sizing: border-box;">
        <div style="overflow: hidden; border-radius: 6px; display: inline-block; max-width: 100%; box-shadow: 0 1px 4px rgba(0,0,0,0.06); background: #ffffff;">
          <img src="../{intro_img}" alt="{intro_cap}" style="max-width: 100%; max-height: 400px; object-fit: contain; display: block; margin: 0 auto;">
        </div>
        <p style="margin: 14px 0 0 0; font-size: 13.5px; color: #475569; font-weight: 600; line-height: 1.6; display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;">
          <span style="background: #e0f2fe; color: #0369a1; padding: 2px 10px; border-radius: 4px; font-size: 12px; font-weight: 700; border: 1px solid #bae6fd;">{intro_tag}</span>
          <span>{intro_cap}</span>
        </p>
      </div>'''

    full_content_zh = f"{intro_p}\n{intro_img_html}\n{b2b_html_zh}"

    # Replace content container
    content_pattern = r'(<div class="p102-pro-content-desc endit-content">)([\s\S]*?)((?:\s*</div>){3,5}\s*<div class="k12-cx-xgcp-4pl-fx1-1-01)'
    match = re.search(content_pattern, html)
    if match:
        html = html[:match.start(2)] + f"\n     {full_content_zh}\n    " + html[match.end(2):]
    else:
        content_pattern_fallback = r'(<div class="p102-pro-content-desc endit-content">)([\s\S]*?)((?:\s*</div>){3,5})'
        match_fb = re.search(content_pattern_fallback, html)
        if match_fb:
            html = html[:match_fb.start(2)] + f"\n     {full_content_zh}\n    " + html[match_fb.end(2):]

    # 6. Language switcher for ZH
    switcher_html = f'''<div class="lang-switch">
  <span class="lang-icon">🌐</span>
  <a href="./{pid}.html" class="active" title="中文">CN</a>
  <span class="lang-sep">|</span>
  <a href="../en/products/{pid}.html" title="English">EN</a>
</div>'''
    html = re.sub(r'<div class="lang-switch">.*?</div>\s*', '', html, flags=re.DOTALL)
    if '<div class="tel rter">' in html:
        html = html.replace('<div class="tel rter">', switcher_html + '\n  <div class="tel rter">', 1)
    elif '<div class="m_top">' in html:
        html = html.replace('<div class="m_top">', '<div class="m_top">\n  ' + switcher_html, 1)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_zh_product_listing_pages(products):
    listing_files = [
        ("product_hzpyl.html", "化妆品原料"),
        ("product_yyyl.html", "医用原料"),
        ("product_spyyyl.html", "食品营养原料"),
        ("product_index.html", "全部原料"),
    ]

    for rel_path, cat in listing_files:
        fp = os.path.join(WORKSPACE_DIR, rel_path)
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8") as f:
            html = f.read()

        # Filter products
        if cat == "全部原料":
            cat_products = products
        elif cat == "化妆品原料":
            cat_products = [p for p in products if p.get("category") in ["化妆品原料", "透皮型重组蛋白/多肽", "仿生生物原料", "植物提取物", "生物发酵原料", "特色定制原料"]]
        elif cat == "医用原料":
            cat_products = [p for p in products if p.get("category") in ["医用原料", "重组蛋白", "动物活性原料", "活性抑菌材料"]]
        elif cat == "食品营养原料":
            cat_products = [p for p in products if p.get("category") in ["食品营养原料", "复合营养素", "细胞营养素"]]
        else:
            cat_products = products

        cards_html = []
        for p in cat_products:
            p_code = p.get("procurement_info", {}).get("submission_code") or p.get("procurement_info", {}).get("nmpa_code")
            code_badge = f'<span style="display:inline-block;padding:2px 6px;background:#ecfdf5;color:#047857;border:1px solid #a7f3d0;border-radius:3px;font-size:11px;font-family:monospace;margin-top:4px;">报送码: {p_code}</span>' if p_code else ''
            card = f'''    <dl> 
     <dt> 
      <a href="products/{p['id']}.html" target="_blank" title="{p['title']}"> <img alt="{p['title']}" src="{p['image']}" title="{p['title']}"> </a> 
     </dt> 
     <dd> 
      <h4><a href="products/{p['id']}.html" target="_blank" title="{p['title']}">{p['title']}</a></h4> 
      <div class="k12-cx-xgcp-4pl-fx1-1-01-desc" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;height:40px;line-height:20px;font-size:12px;color:#64748b;">
        {p.get('desc', '')}
      </div> 
      {code_badge}
      <div class="p15-product-2-date"> 
       <a href="products/{p['id']}.html" target="_blank" title="{p['title']}">查看详情 &gt;</a> 
      </div> 
     </dd> 
    </dl>'''
            cards_html.append(card)

        # Replace product cards inside list container
        list_pattern = r'(<div class="k12-cx-xgcp-4pl-fx1-1-01-list"[^>]*>)([\s\S]*?)(</div>\s*<div class="clear"></div>)'
        if re.search(list_pattern, html):
            new_list_content = "\n" + "\n".join(cards_html) + "\n "
            html = re.sub(list_pattern, r'\1' + new_list_content.replace('\\', '\\\\') + r'\3', html)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Updated Chinese listing page {rel_path} with {len(cat_products)} products.")

def main():
    zh_products, en_products, settings, nav_links = load_data()

    print(f"Generating {len(zh_products)} Chinese product detail pages...")
    for p in zh_products:
        generate_zh_product_detail(p)
    print("All Chinese product detail pages generated successfully!")

    update_zh_product_listing_pages(zh_products)

    # Now run generate_en_product_pages for EN products
    import generate_en_product_pages
    print(f"Generating {len(en_products)} English product detail pages...")
    for p in en_products:
        generate_en_product_pages.generate_en_product_detail(p)
    generate_en_product_pages.update_en_product_listing_pages(en_products)
    print("All English product detail pages and listings generated successfully!")

if __name__ == "__main__":
    main()
