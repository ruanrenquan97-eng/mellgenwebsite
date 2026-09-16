# -*- coding: utf-8 -*-
"""
Generate 100% Pure Professional English Product Detail Pages and Product Listing Pages.
"""

import os
import re
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_DIR = os.path.join(WORKSPACE, "en")
PRODUCTS_EN_PATH = os.path.join(WORKSPACE, "cms_system", "cms_data", "products_en.json")
SETTINGS_PATH = os.path.join(WORKSPACE, "cms_system", "cms_data", "settings.json")
NAV_PATH = os.path.join(WORKSPACE, "cms_system", "cms_data", "nav.json")

def load_data():
    with open(PRODUCTS_EN_PATH, "r", encoding="utf-8") as f:
        all_products = json.load(f)
    all_products.sort(key=lambda x: (x.get("sort", 99999) if isinstance(x.get("sort"), (int, float)) else 99999, x.get("id", "")))
    products = [p for p in all_products if p.get("show", True) is not False and p.get("status") != "offline"]
    offline_products = [p for p in all_products if p.get("show", True) is False or p.get("status") == "offline"]
    settings = {}
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    nav_links = []
    if os.path.exists(NAV_PATH):
        with open(NAV_PATH, "r", encoding="utf-8") as f:
            nav_links = json.load(f)
    return products, offline_products, settings, nav_links

def render_b2b_dossier_en(p):
    rd = p.get("rd_info") or {}
    proc = p.get("procurement_info") or {}
    mkt = p.get("marketing_info") or {}
    disclaimer = p.get("disclaimer") or ""

    has_rd = any(bool(v) for v in rd.values()) if isinstance(rd, dict) else False
    has_proc = any(bool(v) for v in proc.values()) if isinstance(proc, dict) else False
    has_mkt = any(bool(v) for v in mkt.values()) if isinstance(mkt, dict) else False

    out = []
    out.append('\n<!-- ==================== B2B PROFESSIONAL DOSSIER & DISCLAIMER ==================== -->')
    out.append('<div class="mellgen-b2b-section" style="width:1200px; margin: 45px auto 25px auto; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif; box-sizing: border-box;">')

    if has_rd or has_proc or has_mkt:
        out.append('  <div style="text-align: center; margin-bottom: 35px;">')
        out.append('    <h3 style="font-size: 26px; color: #174778; font-weight: 700; margin: 0 0 8px 0; letter-spacing: 0.5px;">RAW MATERIAL TECHNICAL &amp; REGULATORY DOSSIER</h3>')
        out.append('    <p style="font-size: 14px; color: #64748b; margin: 0;">Comprehensive Technical, Quality Specification, and Regulatory Dossier for R&amp;D Formulators, Procurement, and Product Managers</p>')
        out.append('  </div>')

    # 1. Biotechnology Mechanism & Evidence (Authoritative 2026 Brochure)
    diagram_img = p.get("diagram_image")
    diagram_cap = p.get("diagram_caption", "")
    if diagram_img:
        out.append('  <!-- 1. Biotechnology Mechanism & Evidence -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">📊</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">Biotechnology Mechanism &amp; Scientific Evidence</span>')
        out.append('      </div>')
        out.append('      <span style="color: #dbeafe; font-size: 12px;">Authoritative Brochure Technical Diagram · Molecular Model · Transdermal &amp; Efficacy Mechanism</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px; text-align: center; background: #f8fafc;">')
        out.append('      <div style="display: inline-block; max-width: 100%; background: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">')
        out.append(f'        <img src="../../{diagram_img}" alt="{diagram_cap}" style="max-width: 100%; max-height: 480px; object-fit: contain; border-radius: 6px; display: block; margin: 0 auto; box-shadow: 0 1px 4px rgba(0,0,0,0.08);">')
        out.append(f'        <p style="margin: 14px 0 4px 0; font-size: 13.5px; color: #334155; font-weight: 600; line-height: 1.6; text-align: center;">')
        out.append(f'          <span style="display: inline-block; background: #eff6ff; color: #1d4ed8; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 8px; border: 1px solid #bfdbfe;">Mechanism Diagram</span>{diagram_cap}')
        out.append('        </p>')
        out.append('      </div>')
        out.append('    </div>')
        out.append('  </div>')

    # 2. R&D Formulation Engineers Zone
    if has_rd:
        out.append('  <!-- R&D Formulation Engineers Zone -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #174778 0%, #1d5b99 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">🔬</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">Formulation R&amp;D Engineer Guide (R&amp;D Technical Dossier)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #93c5fd; font-size: 12px;">Formulation Application · Physicochemical Parameters · Stability &amp; Compatibility</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px;">')
        out.append('      <table style="width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155;">')

        rd_items = [
            ("INCI Name (CN)", rd.get("inci_cn"), "INCI Name (EN)", rd.get("inci_en")),
            ("CAS No.", rd.get("cas"), "Recommended Dosage", rd.get("dosage")),
            ("Optimal pH Range", rd.get("ph_range"), "Thermal Processing", rd.get("heat_tolerance")),
            ("Appearance &amp; Odor", rd.get("appearance"), "Solubility &amp; Method", rd.get("solubility")),
        ]

        for label1, val1, label2, val2 in rd_items:
            if val1 or val2:
                out.append('        <tr style="border-bottom: 1px solid #f1f5f9;">')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 16%; font-weight: 600; color: #475569; white-space: nowrap;">{label1}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 34%; color: #1e293b;">{val1 or "—"}</td>')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 16%; font-weight: 600; color: #475569; white-space: nowrap;">{label2}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 34%; color: #1e293b;">{val2 or "—"}</td>')
                out.append('        </tr>')

        out.append('      </table>')

        if rd.get("compatibility"):
            out.append('      <div style="margin-top: 16px; padding: 12px 18px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; font-size: 13px; color: #166534; line-height: 1.6;">')
            out.append(f'        <strong>💡 Compatibility Guidelines &amp; Precautions: </strong>{rd.get("compatibility")}')
            out.append('      </div>')

        out.append('    </div>')
        out.append('  </div>')

    # 3. Procurement & Compliance Dossier
    if has_proc:
        out.append('  <!-- Procurement & Compliance Dossier -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">📦</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">Procurement &amp; Compliance Dossier (Procurement &amp; Compliance)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #ccfbf1; font-size: 12px;">NMPA Code · MOQ · Sampling Support · Certificate of Analysis</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px;">')
        out.append('      <table style="width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155;">')

        proc_items = [
            ("NMPA Submission Code", proc.get("nmpa_code"), "Supply Packaging", proc.get("packaging")),
            ("Minimum Order Quantity (MOQ)", proc.get("moq"), "Delivery Lead Time", proc.get("lead_time")),
            ("Storage Conditions", proc.get("storage"), "Shelf Life (Shelf Life)", proc.get("shelf_life")),
            ("R&amp;D Sample Support", proc.get("sample_policy"), "Quality Documentation", proc.get("qualifications")),
        ]

        for label1, val1, label2, val2 in proc_items:
            if val1 or val2:
                val1_display = f'<span style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; color: #047857; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-family: monospace; border: 1px solid #a7f3d0;">✓ {val1}</span>' if label1 == "NMPA Submission Code" and val1 else (val1 or "—")
                out.append('        <tr style="border-bottom: 1px solid #f1f5f9;">')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 16%; font-weight: 600; color: #475569; white-space: nowrap;">{label1}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 34%; color: #1e293b;">{val1_display}</td>')
                out.append(f'          <td style="padding: 10px 14px; background: #f8fafc; width: 16%; font-weight: 600; color: #475569; white-space: nowrap;">{label2}</td>')
                out.append(f'          <td style="padding: 10px 14px; width: 34%; color: #1e293b;">{val2 or "—"}</td>')
                out.append('        </tr>')

        out.append('      </table>')
        out.append('    </div>')
        out.append('  </div>')

    # 4. Marketing Highlights
    if has_mkt:
        out.append('  <!-- Product Planning & Marketing Highlights -->')
        out.append('  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 25px; overflow: hidden;">')
        out.append('    <div style="background: linear-gradient(135deg, #b45309 0%, #d97706 100%); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between;">')
        out.append('      <div style="display: flex; align-items: center; gap: 10px;">')
        out.append('        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 14px;">💡</span>')
        out.append('        <span style="color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;">Product Planning &amp; Marketing Highlights (Marketing Highlights)</span>')
        out.append('      </div>')
        out.append('      <span style="color: #fef3c7; font-size: 12px;">Core Mechanism · Efficacy Claims · Recommended Formats · Scientific Backing</span>')
        out.append('    </div>')
        out.append('    <div style="padding: 24px; display: flex; flex-direction: column; gap: 16px;">')

        if mkt.get("mechanism"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">🧬 Core Bio-Tech Barrier &amp; Mechanism of Action:</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; line-height: 1.7; color: #475569; background: #fffbeb; padding: 12px 16px; border-radius: 6px; border: 1px solid #fef3c7;">{mkt.get("mechanism")}</p>')
            out.append('      </div>')

        if mkt.get("claims"):
            claims_tags = [f'<span style="background: #f1f5f9; color: #1e293b; padding: 4px 12px; border-radius: 100px; font-size: 12.5px; font-weight: 600; border: 1px solid #cbd5e1;">🏷️ {c.strip()}</span>' for c in mkt.get("claims").split(',') if c.strip()]
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 700; color: #1e293b;">✨ Key Selling Point Keywords:</h5>')
            out.append(f'        <div style="display: flex; flex-wrap: wrap; gap: 8px;">{"".join(claims_tags)}</div>')
            out.append('      </div>')

        if mkt.get("applications"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">🧴 Recommended Product Formats &amp; Categories:</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{mkt.get("applications")}</p>')
            out.append('      </div>')

        if mkt.get("patents"):
            out.append('      <div>')
            out.append('        <h5 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #1e293b;">📜 Patented Technologies &amp; Scientific Backing:</h5>')
            out.append(f'        <p style="margin: 0; font-size: 13.5px; color: #334155;">{mkt.get("patents")}</p>')
            out.append('      </div>')

        out.append('    </div>')
        out.append('  </div>')

    # 5. Regulatory Compliance & Disclaimer
    out.append('  <!-- Regulatory Compliance & Disclaimer -->')
    out.append('  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #174778; border-radius: 6px; padding: 20px 24px; margin-top: 25px;">')
    out.append('    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">')
    out.append('      <span style="font-size: 16px;">⚖️</span>')
    out.append('      <h4 style="margin: 0; font-size: 14.5px; font-weight: 700; color: #1e293b; letter-spacing: 0.3px;">Regulatory Compliance &amp; Peer-to-Peer Disclaimer</h4>')
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

def generate_en_product_detail(product):
    pid = product["id"]
    dest_path = os.path.join(EN_DIR, "products", f"{pid}.html")
    src_cn_path = os.path.join(WORKSPACE, "products", f"{pid}.html")

    if os.path.exists(src_cn_path):
        with open(src_cn_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        with open(os.path.join(WORKSPACE, "products", "tphtct.html"), "r", encoding="utf-8") as f:
            html = f.read()

    # FIRST: Completely remove any existing B2B section (comments or div) from the loaded template
    html = re.sub(r'<!-- ==================== B2B PROFESSIONAL DOSSIER & DISCLAIMER ==================== -->[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->', '', html)
    html = re.sub(r'<div class="mellgen-b2b-section"[\s\S]*?<!-- ==================== END B2B PROFESSIONAL DOSSIER ==================== -->', '', html)

    # 1. SEO Title & Meta
    seo_title = f"{product['title']} - Product Center - Mellgen Biotech"
    html = re.sub(r'<title>[^<]+</title>', f"<title>{seo_title}</title>", html)
    if product.get("desc"):
        html = re.sub(r'(<meta[^>]+name=["\']description["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{product["desc"]}{m.group(3)}', html, flags=re.I)
    html = re.sub(r'(<meta[^>]+name=["\']keywords["\'][^>]+content=["\'])(.*?)(["\'])', lambda m: f'{m.group(1)}{product["title"]}, Mellgen Biotech, cosmetic raw materials, transdermal peptides{m.group(3)}', html, flags=re.I)

    # 2. Breadcrumbs
    cat_filename = "product_hzpyl.html"
    cat = product["category"]
    if cat in ["Medical Raw Materials"]:
        cat_filename = "product_yyyl.html"
    elif cat in ["Food Nutrition Ingredients"]:
        cat_filename = "product_spyyyl.html"

    crumbs_html = f'''<div class="p102-curmbs-1" navcrumbs=""> 
    <b>Current Location: </b> 
    <a href="../index.html" title="Home"> Home </a> 
    <span> &gt; </span> 
    <i class=""> <a href="../product_index.html" title="Products"> Products </a> <span> &gt; </span> </i> 
    <i class="p12-curblock"> <a href="../{cat_filename}" title="{product['category']}">{product['category']}</a> <span> &gt; </span> </i> 
    <i class=""> <a href="../products/{pid}.html" title="{product['title']}"> {product['title']} </a> </i> 
  </div>'''
    html = re.sub(r'<div class="p102-curmbs-1"[^>]*>.*?</div>', crumbs_html, html, flags=re.DOTALL)

    # 3. Product Title & Subtitle
    html = re.sub(r'<h1[^>]*class="p102-proShow-1-title"[^>]*>.*?</h1>', f'<h1 title="{product["title"]}" class="p102-proShow-1-title">\n        {product["title"]} \n      </h1>', html, flags=re.DOTALL)
    html = re.sub(r'<div class="p102-proShow-1-text">\s*<h1[^>]*>.*?</h1>\s*<p>.*?</p>', f'<div class="p102-proShow-1-text">\n      <h1 title="{product["title"]}" class="p102-proShow-1-title">\n        {product["title"]} \n      </h1> \n      <p>{product["category"]}</p>', html, flags=re.DOTALL)

    # Fix left column (Image, Corner Tag, Sample Bar, Size) cleanly and deterministically
    clean_left_block_en = f'''<div class="p102-proShow-1-left">
    <div class="product-sample-corner-tag" style="position: absolute; left: 14px; top: 14px; z-index: 6; background: rgba(15, 23, 42, 0.78); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); color: #ffffff; font-size: 12px; font-weight: 600; padding: 3px 9px; border-radius: 4px; display: inline-flex; align-items: center; gap: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.2); pointer-events: none;"><span style="width: 6px; height: 6px; background: #38bdf8; border-radius: 50%; display: inline-block;"></span>Sample Packaging</div> 
    <div class="p102-proShow-1-prev"></div> 
    <div class="p102-proShow-1-next"></div> 
    <div class="p102-proShow-1-pic"> 
     <ul class="clearafter"> 
       <li><img alt="{product['title']}" src="../../{product['image']}" title="{product['title']}"></li> 
     </ul> 
    </div> 
    <div class="product-detail-sample-bar" style="margin: 10px 14px 12px 14px; padding: 9px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #0284c7; border-radius: 4px; display: flex; align-items: center; justify-content: space-between; box-sizing: border-box;">
      <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
        <span style="display: inline-flex; align-items: center; gap: 4px; background: #0284c7; color: #ffffff; font-size: 12px; font-weight: 600; padding: 2px 7px; border-radius: 3px;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          Sample Pack
        </span>
        <span style="color: #475569; font-size: 12.5px;">Specification: 30g/50g R&amp;D Testing Sample (Global Courier Support)</span>
      </div>
      <a href="../helps/lxwm.html" target="_blank" style="display: inline-flex; align-items: center; gap: 4px; color: #0284c7; font-size: 12px; font-weight: 600; text-decoration: none; white-space: nowrap;">
        Request Sample &gt;
      </a>
    </div>
    <div class="p102-proShow-1-size"></div> 
   </div>\n   '''

    left_pattern = r'<div class="p102-proShow-1-left"[^>]*>[\s\S]*?(?=\s*<div class="p102-proShow-1-right">)'
    if re.search(left_pattern, html):
        html = re.sub(left_pattern, clean_left_block_en, html)

    # 4. Top Specs & Overview
    rd = product.get("rd_info", {})
    specs_p_html = []
    if product.get("desc"):
        specs_p_html.append(f'<p style="line-height: 1.6; margin-bottom: 8px; color: #475569; font-size: 13.5px;">{product["desc"]}</p>')
    inci = rd.get("inci_en") or rd.get("inci_cn") or product.get("specs", {}).get("INCI Name")
    if inci:
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>INCI Name: </strong>{inci}</p>')
    app_val = rd.get("appearance") or product.get("specs", {}).get("Appearance")
    sol_val = rd.get("solubility") or product.get("specs", {}).get("Solubility")
    if app_val or sol_val:
        app_sol = f"{app_val or ''}, {sol_val or ''}".strip(', ')
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>Appearance &amp; Solubility: </strong>{app_sol}</p>')
    dosage = rd.get("dosage") or product.get("specs", {}).get("Recommended Dosage")
    if dosage:
        specs_p_html.append(f'<p style="margin: 4px 0; font-size: 13px; color: #334155;"><strong>Recommended Dosage: </strong>{dosage}</p>')

    top_specs_content = "\n" + "\n".join(specs_p_html) + "\n "
    desc_box_pattern = r'(<div class="p102-proShow-1-desc">)(.*?)(</div>\s*<div class="p102-proShow-1-tel">)'
    if re.search(desc_box_pattern, html, re.DOTALL):
        html = re.sub(desc_box_pattern, r'\1' + top_specs_content.replace('\\', '\\\\') + r'\3', html, flags=re.DOTALL)

    # Online inquiry button & hotline
    html = re.sub(r'<a href="[^"]*lxwm\.html"[^>]*>.*?</a>', '<a href="../helps/lxwm.html" target="_blank" title="Online Inquiry">Online Inquiry</a>', html)
    html = re.sub(r'<p><em>服务热线：</em><span>0755-82926499</span></p>', '<p><em>Hotline: </em><span>0755-82926499</span></p>', html)

    # 5. Render B2B Dossier
    b2b_html_en = render_b2b_dossier_en(product)
    intro_p = product.get("content", f"<p>{product.get('desc')}</p>")

    # Add intro illustration image card (animal/plant source, mechanism, or data chart)
    intro_img = product.get("intro_image")
    intro_tag = product.get("intro_image_tag", "Scientific Illustration")
    intro_cap = product.get("intro_image_caption", "")
    intro_img_html = ""
    if intro_img:
        intro_img_html = f'''
      <div class="product-intro-image-card" style="margin: 28px auto 25px auto; text-align: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 22px; box-shadow: 0 2px 12px rgba(0,0,0,0.03); max-width: 820px; box-sizing: border-box;">
        <div style="overflow: hidden; border-radius: 6px; display: inline-block; max-width: 100%; box-shadow: 0 1px 4px rgba(0,0,0,0.06); background: #ffffff;">
          <img src="../../{intro_img}" alt="{intro_cap}" style="max-width: 100%; max-height: 400px; object-fit: contain; display: block; margin: 0 auto;">
        </div>
        <p style="margin: 14px 0 0 0; font-size: 13.5px; color: #475569; font-weight: 600; line-height: 1.6; display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;">
          <span style="background: #e0f2fe; color: #0369a1; padding: 2px 10px; border-radius: 4px; font-size: 12px; font-weight: 700; border: 1px solid #bae6fd;">{intro_tag}</span>
          <span>{intro_cap}</span>
        </p>
      </div>'''

    full_content_en = f"{intro_p}\n{intro_img_html}\n{b2b_html_en}"

    # Replace content container
    content_pattern = r'(<div class="p102-pro-content-desc endit-content">)([\s\S]*?)((?:\s*</div>){3,5}\s*<div class="k12-cx-xgcp-4pl-fx1-1-01)'
    match = re.search(content_pattern, html)
    if match:
        html = html[:match.start(2)] + f"\n     {full_content_en}\n    " + html[match.end(2):]
    else:
        content_pattern_fallback = r'(<div class="p102-pro-content-desc endit-content">)([\s\S]*?)((?:\s*</div>){3,5})'
        match_fb = re.search(content_pattern_fallback, html)
        if match_fb:
            html = html[:match_fb.start(2)] + f"\n     {full_content_en}\n    " + html[match_fb.end(2):]

    # Clean related products translations
    rel_replacements = [
        ('MELLPRO-RHCTransdermal Recombinant Human Ⅰ型、Ⅲ型', 'MELLPRO-RHC Transdermal Recombinant Human Type I & Type III '),
        ('MELLPRO-RHCTransdermal Recombinant Human Ⅰ型、Ⅲ', 'MELLPRO-RHC Transdermal Recombinant Human Type I & Type III '),
        ('Ⅰ型、Ⅲ型', 'Type I & Type III'),
        ('Ⅰ型、Ⅲ', 'Type I & Type III'),
        ('十肽-4', 'Decapeptide-4'),
        ('水溶性胶原', 'Soluble Collagen'),
        ('水、', 'Aqua, '),
        ('胶原、', 'Collagen, '),
        ('胶原', 'Collagen'),
        ('无色澄澈透明液体', 'Colorless Transparent Liquid'),
        ('水溶', 'Water Soluble'),
    ]
    for k, v in rel_replacements:
        html = html.replace(k, v)

    # Normalize bottom recommendation section: exactly one clean English recommendation block
    standard_rec_block_en = '''<div class="k12-cx-xgcp-4pl-fx1-1-01 blk blk-main" style="width:1200px;margin:30px auto;"> 
 <h4 class="p102-pro-content-title">Recommended Products</h4> 
 <div class="k12-cx-xgcp-4pl-fx1-1-01-list"> 
   <dl> 
    <dt> 
     <a href="../products/tphtct.html" target="_blank" title="Transdermal Peptide cTDP"> <img alt="Transdermal Peptide cTDP" src="../../resource/images/9b89259b4fb24ad2bcc390737279f8ff_44.jpg" title="Transdermal Peptide cTDP"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/tphtct.html" target="_blank" title="Transdermal Peptide cTDP"> Transdermal Peptide cTDP </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       The master key to opening skin absorption channels. Core carrier of biological transdermal technology, enhancing skin absorption of 10000+ Da. macromolecules.
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/tphtct.html" target="_blank" title="Transdermal Peptide cTDP"></a> 
     </div> 
    </dd> 
   </dl> 
   <dl> 
    <dt> 
     <a href="../products/jnhtea.html" target="_blank" title="Polycyclic Peptide EAC"> <img alt="Polycyclic Peptide EAC" src="../../resource/images/9b89259b4fb24ad2bcc390737279f8ff_36.jpg" title="Polycyclic Peptide EAC"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/jnhtea.html" target="_blank" title="Polycyclic Peptide EAC"> Polycyclic Peptide EAC </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       Cellular energy power bank and nutrient ring. Energizes mitochondrial respiration, accelerates cutaneous microcirculation and endogenous collagen synthesis.
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/jnhtea.html" target="_blank" title="Polycyclic Peptide EAC"></a> 
     </div> 
    </dd> 
   </dl> 
   <dl> 
    <dt> 
     <a href="../products/5djydb.html" target="_blank" title="5D Collagen"> <img alt="5D Collagen" src="../../resource/images/9b89259b4fb24ad2bcc390737279f8ff_32.jpg" title="5D Collagen"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/5djydb.html" target="_blank" title="5D Collagen"> 5D Collagen </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       Integrates 3rd-generation biological transdermal technology to replenish collagen directly into deep skin layers, resisting collagen depletion and restoring elasticity.
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/5djydb.html" target="_blank" title="5D Collagen"></a> 
     </div> 
    </dd> 
   </dl> 
   <dl class="p14-product-clear"> 
    <dt> 
     <a href="../products/zzjydb.html" target="_blank" title="Recombinant Collagen Solution"> <img alt="Recombinant Collagen Solution" src="../../resource/images/bottle_zzjydb.jpg" title="Recombinant Collagen Solution"> </a> 
    </dt> 
    <dd> 
     <h4><a href="../products/zzjydb.html" target="_blank" title="Recombinant Collagen Solution"> Recombinant Collagen Solution </a></h4> 
     <div class="k12-cx-xgcp-4pl-fx1-1-01-desc">
       MELLPRO-RHC transdermal recombinant human Type I &amp; Type III collagen solution, repairing the basement membrane zone and smoothing dry lines and sagging.
     </div> 
     <div class="p15-product-2-date"> 
      <a href="../products/zzjydb.html" target="_blank" title="Recombinant Collagen Solution"></a> 
     </div> 
    </dd> 
   </dl> 
 </div> 
 <div class="clear"></div> 
</div>'''
    rec_pattern = r'((?:</div>\s*){3})\s*(?:<div class=["\']k12-cx-xgcp-4pl-fx1-1-01[\s\S]*?)(?=\s*<div class=["\']g_ft f_fw["\'])'
    html = re.sub(rec_pattern, r'\1\n  ' + standard_rec_block_en.replace('\\', '\\\\') + '\n\n  ', html)

    # 6. Fix asset paths for en/products/ (depth = 1)
    html = re.sub(r'src=["\']\.\./images/', 'src="../../images/', html)
    html = re.sub(r'href=["\']\.\./css/', 'href="../../css/', html)
    html = re.sub(r'src=["\']\.\./js/', 'src="../../js/', html)
    html = re.sub(r'src=["\']\.\./resource/', 'src="../../resource/', html)
    html = re.sub(r'url\(\.\./images/', 'url(../../images/', html)
    html = re.sub(r'url\(\.\./resource/', 'url(../../resource/', html)
    html = re.sub(r'href=["\']\.\./67b', 'href="../../css/67b', html)

    # 7. Language Switcher
    switcher_html = f'''<div class="lang-switch">
  <span class="lang-icon">🌐</span>
  <a href="../../products/{pid}.html" title="中文">CN</a>
  <span class="lang-sep">|</span>
  <a href="./{pid}.html" class="active" title="English">EN</a>
</div>'''
    html = re.sub(r'<div class="lang-switch">.*?</div>\s*', '', html, flags=re.DOTALL)
    if '<div class="tel rter">' in html:
        html = html.replace('<div class="tel rter">', switcher_html + '\n  <div class="tel rter">', 1)
    elif '<div class="m_top">' in html:
        html = html.replace('<div class="m_top">', '<div class="m_top">\n  ' + switcher_html, 1)

    # 8. Search bar placeholder
    html = re.sub(r'placeholder="[^"]*"', 'placeholder="Please enter keywords to search..."', html)

    # 9. Translate all surrounding template elements (navigation, sidebar, carousels, footers)
    m_inci = re.search(r'(INCI Name \(CN\)</td>\s*<td[^>]*>)(.*?)(</td>)', html)
    inci_saved = m_inci.group(0) if m_inci else None

    try:
        import build_full_en_site
        html = build_full_en_site.translate_content(html)
    except Exception as e:
        print(f"[-] Notice translating product template: {e}")

    if inci_saved:
        html = re.sub(r'INCI Name \(CN\)</td>\s*<td[^>]*>.*?</td>', inci_saved, html)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_en_product_listing_pages(products):
    listing_files = [
        ("en/product_index.html", "All Products"),
        ("en/product_hzpyl.html", "Cosmetic Raw Materials"),
        ("en/product_tpxzzd.html", "Transdermal Recombinant Protein/Peptides"),
        ("en/product_zwyhxw.html", "Plant-Derived Actives"),
        ("en/product_zzfsdb.html", "Recombinant Biomimetic Protein"),
        ("en/product_hyyhxw.html", "Marine-Derived Actives"),
        ("en/product_yejfjy.html", "Infant Probiotic Fermentation Actives"),
        ("en/product_dwyhxw.html", "Animal-Derived Actives"),
        ("en/product_zzdb.html", "Recombinant Biomimetic Protein"),
        ("en/product_fhyys.html", "Cell Nutrients"),
        ("en/product_lzdt.html", "Plant-Derived Actives"),
    ]

    for rel_path, cat in listing_files:
        fp = os.path.join(WORKSPACE, rel_path)
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        # Clean trailing corrupted data if multiple </html> exist
        m_ends = list(re.finditer(r'</html>', html, re.I))
        if len(m_ends) > 1:
            html = html[:m_ends[0].end()]

        # Build card list
        if cat in ["All Products", "Cosmetic Raw Materials"]:
            cat_products = products
        elif cat == "Transdermal Recombinant Protein/Peptides":
            cat_products = [p for p in products if p.get("id") in ["tphtct", "tpxldb", "mellpr8670"] or p.get("category") in [
                "Transdermal Recombinant Protein/Peptides", "透皮型重组蛋白/多肽", "高渗透型重组蛋白/多肽"
            ]]
        elif cat == "Plant-Derived Actives":
            cat_products = [p for p in products if p.get("id") in ["yskmyz"] or p.get("category") in [
                "Plant-Derived Actives", "植物源活性物", "植物提取物"
            ]]
        else:
            cat_products = []

        cat_products.sort(key=lambda x: (x.get("sort", 99999) if isinstance(x.get("sort"), (int, float)) else 99999, x.get("id", "")))

        list_html = "\n"
        for i, p in enumerate(cat_products):
            detail_link = f"./products/{p['id']}.html"
            image_path = f"../{p['image']}"
            p_desc = f"\n      <p> {p['desc'][:90]}...<a href=\"{detail_link}\" target=\"_blank\" title=\"{p['title']}\">Details &gt;</a> </p>" if p.get("desc") else ""
            list_html += f"""    <dl> 
     <dt> 
      <a href="{detail_link}" target="_blank" title="{p['title']}"><img alt="{p['title']}" src="{image_path}"></a> 
     </dt> 
     <dd> 
      <h4><a href="{detail_link}" target="_blank" title="{p['title']}">{p['title']}</a></h4> {p_desc}
     </dd> 
    </dl> 
"""
            if (i + 1) % 4 == 0 and (i + 1) < len(cat_products):
                list_html += "    <div class=\"clear\"></div>\n"
        list_html += "    "

        html = re.sub(r'(<div class="hyt-product-list-6">)(.*?)(<div class="clear"></div>\s*</div>)', r'\1' + list_html.replace('\\', '\\\\') + r'\3', html, flags=re.DOTALL)
        html = re.sub(r'(<div class="p102-pagination-1-main">)(.*?)(</div>)', r'\1<a class="page_curr">1</a>\3', html, flags=re.DOTALL)

        # Popular searches in header
        pop_html = '''<p> <b>Popular Searches: </b> 
    <a href="./product_hzpyl.html" title="Probiotic Soothing Factor">Probiotic Soothing Factor</a> 
    <a href="./product_hzpyl.html" title="Collagen">Collagen</a> 
    <a href="./product_hzpyl.html" title="Transdermal Fibronectin">Transdermal Fibronectin</a> 
    <a href="./product_hzpyl.html" title="cTDP Cyclic Peptide">cTDP Cyclic Peptide</a> 
   </p>'''
        html = re.sub(r'<p>\s*<b>Popular Searches:.*?</b>.*?</p>', pop_html, html, flags=re.DOTALL)
        html = re.sub(r'placeholder="[^"]*"', 'placeholder="Please enter keywords to search..."', html)

        with open(fp, "w", encoding="utf-8") as f:
            f.write(html)

def main():
    print("Generating pure English product pages & updating listing pages...")
    products, offline_products, settings, nav_links = load_data()
    
    # Clean orphaned English product pages
    known_pids = set(p['id'] for p in products) | set(p['id'] for p in offline_products)
    en_prod_dir = os.path.join(WORKSPACE, "en", "products")
    if os.path.exists(en_prod_dir):
        for f in os.listdir(en_prod_dir):
            if f.endswith('.html') and f[:-5] not in known_pids:
                try:
                    os.remove(os.path.join(en_prod_dir, f))
                    print(f"[*] Cleaned orphaned English product page: {f}")
                except Exception:
                    pass

    # 1. Generate detail pages for published active products
    for p in products:
        generate_en_product_detail(p)

    # 2. Generate standard redirection pages for offline products
    for p in offline_products:
        pid = p["id"]
        dest_path = os.path.join(EN_DIR, "products", f"{pid}.html")
        redirect_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=../product_index.html">
<link rel="canonical" href="https://www.mellgen.com/en/product_index.html">
<title>Product Discontinued / Offline - Mellgen Biotech</title>
<script>location.replace("../product_index.html");</script>
</head>
<body>
<p>This product has been discontinued or taken offline. Redirecting to <a href="../product_index.html">Product Center</a>...</p>
</body>
</html>'''
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(redirect_html)

    # 3. Update all listing pages
    update_en_product_listing_pages(products)
    print(f"[OK] Generated {len(products)} English product detail pages, {len(offline_products)} redirect pages & updated listing pages!")

if __name__ == "__main__":
    main()
