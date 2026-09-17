#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Injects professional B2B legal and regulatory disclaimers into all articles
across Chinese (articles/*.html) and English (en/articles/*.html) directories,
updates cms_data/articles.json, cms_system/generator.py, and cms_system/wechat_crawler.py.
"""

import os
import glob
import re
import json

ZH_DISCLAIMER_HTML = """    <div class="article-disclaimer-box" style="margin-top:20px;padding:15px 18px;background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #7fb435;border-radius:6px;font-size:12.5px;color:#64748b;line-height:1.8;">
        <div style="font-weight:700;color:#1e293b;font-size:13px;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
            <span style="color:#7fb435;">⚖️</span> 版权与合规免责声明
        </div>
        <p style="margin:0 0 6px 0;">1. <strong>专业研发与学术参考：</strong>本站刊载之技术科普、学术文献、配方机理及实验数据探讨，仅供化妆品研发工程师、配方师及科研专业人士交流参考，不作为针对终端消费者的直接功效承诺或医疗/诊断建议。</p>
        <p style="margin:0 0 6px 0;">2. <strong>成品合规与宣称责任：</strong>化妆品品牌商及成品制造方应依据国家法律法规（如《化妆品监督管理条例》、《化妆品功效宣称评价规范》等），独立对其终产品的安全性、稳定性及功效宣称负责，并依法完成备案申报与功效评价。</p>
        <p style="margin:0;">3. <strong>知识产权与内容说明：</strong>本站部分内容或图片摘引自公开学术文献或专业资讯，版权归原作者所有，仅作学术分享与技术探讨。若涉及版权争议请联系核实；对于因客户不当使用或超范围宣称所引发的后果，本司不承担法律责任。</p>
    </div>"""

EN_DISCLAIMER_HTML = """    <div class="article-disclaimer-box" style="margin-top:20px;padding:15px 18px;background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #7fb435;border-radius:6px;font-size:12px;color:#64748b;line-height:1.75;">
        <div style="font-weight:700;color:#1e293b;font-size:12.5px;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
            <span style="color:#7fb435;">⚖️</span> Regulatory &amp; Technical Disclaimer
        </div>
        <p style="margin:0 0 6px 0;">1. <strong>Professional R&amp;D Reference Only:</strong> Technical research, mechanism analyses, literature citations, and experimental evaluations published on this website are intended solely for professional exchange among cosmetic formulation chemists, researchers, and scientific institutions. They do not constitute efficacy guarantees, marketing claims for end-consumers, or medical advice.</p>
        <p style="margin:0 0 6px 0;">2. <strong>Finished Formulation Compliance:</strong> Finished cosmetic brand owners and manufacturers are independently responsible for verifying the safety, stability, regulatory filings, and efficacy evaluations of their finished cosmetic products in accordance with applicable cosmetic regulations.</p>
        <p style="margin:0;">3. <strong>Intellectual Property &amp; Liability:</strong> Select content, figures, or literature references are cited from published academic journals or scientific databases for educational purposes. Mellgen Biotech assumes no liability for unauthorized dissemination, improper applications, or off-label claims by third parties.</p>
    </div>"""

ZH_FOOTER_NOTE_HTML = """    <div class="article-footer-note" style="margin-top:28px;padding:14px 18px;background:#fafafa;border:1px dashed #dcdcdc;border-radius:6px;font-size:13px;color:#777;">
        <p style="margin:0;line-height:1.6;"><strong>声明与技术支持：</strong>美尔健（深圳）生物科技有限公司致力于生物透皮技术与功效原料研发，如需获取原料详细规格书（TDS）、安全评估资料或定制配方打样，欢迎致电全国服务热线：0755-82926499 / 136-9197-8530。</p>
    </div>"""

EN_FOOTER_NOTE_HTML = """    <div class="article-footer-note" style="margin-top:28px;padding:14px 18px;background:#fafafa;border:1px dashed #dcdcdc;border-radius:6px;font-size:13px;color:#777;">
        <p style="margin:0;line-height:1.6;"><strong>Technical Inquiries &amp; Support:</strong> Mellgen (Shenzhen) Biotechnology Co., Ltd. specializes in biological transdermal delivery technologies and bioactive skincare ingredients. To request technical data sheets (TDS), safety assessment dossiers, or custom formulation samples, please contact our team at: +86-755-82926499 / +86-136-9197-8530.</p>
    </div>"""


def process_zh_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # Remove existing disclaimer box if previously added to allow clean update
    html = re.sub(r'\s*<div class="article-disclaimer-box"[^>]*>.*?</div>\s*</div>', '</div>', html, flags=re.DOTALL)
    html = re.sub(r'\s*<div class="article-disclaimer-box"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    # Check if article has article-footer-note
    footer_note_pattern = r'<div class="article-footer-note"[^>]*>.*?</div>'
    has_fn = bool(re.search(footer_note_pattern, html, flags=re.DOTALL))

    if has_fn:
        # Replace existing footer note with updated footer note + disclaimer box
        combined_footer = f"{ZH_FOOTER_NOTE_HTML}\n{ZH_DISCLAIMER_HTML}"
        html = re.sub(footer_note_pattern, combined_footer, html, flags=re.DOTALL)
    else:
        # If no footer note (e.g. lab reports), look for the lab card or end of p102-info-content
        lab_card_pattern = r'(<div style="margin-top:30px;padding:16px 20px;background:#f8fafc;border:1px dashed #cbd5e1;.*?</div>\s*</div>)'
        if re.search(lab_card_pattern, html, flags=re.DOTALL):
            html = re.sub(lab_card_pattern, rf'\1\n{ZH_DISCLAIMER_HTML}', html, flags=re.DOTALL)
        else:
            # Fallback: insert before end of p102-info-content
            end_p102_pattern = r'(</div>\s*<div class="clear"></div>\s*<div class="p102-info-related">)'
            if re.search(end_p102_pattern, html):
                html = re.sub(end_p102_pattern, f"{ZH_DISCLAIMER_HTML}\n\\1", html, count=1)
            else:
                end_p102_simple = r'(</div>\s*<div class="clear"></div>)'
                html = re.sub(end_p102_simple, f"{ZH_DISCLAIMER_HTML}\n\\1", html, count=1)

    # Also clean up any accidental G55 typo in the file
    html = html.replace("G55-82926499", "0755-82926499")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return True


def process_en_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    html = re.sub(r'\s*<div class="article-disclaimer-box"[^>]*>.*?</div>\s*</div>', '</div>', html, flags=re.DOTALL)
    html = re.sub(r'\s*<div class="article-disclaimer-box"[^>]*>.*?</div>', '', html, flags=re.DOTALL)

    footer_note_pattern = r'<div class="article-footer-note"[^>]*>.*?</div>'
    has_fn = bool(re.search(footer_note_pattern, html, flags=re.DOTALL))

    if has_fn:
        combined_footer = f"{EN_FOOTER_NOTE_HTML}\n{EN_DISCLAIMER_HTML}"
        html = re.sub(footer_note_pattern, combined_footer, html, flags=re.DOTALL)
    else:
        lab_card_pattern = r'(<div style="margin-top:30px;padding:16px 20px;background:#f8fafc;border:1px dashed #cbd5e1;.*?</div>\s*</div>)'
        if re.search(lab_card_pattern, html, flags=re.DOTALL):
            html = re.sub(lab_card_pattern, rf'\1\n{EN_DISCLAIMER_HTML}', html, flags=re.DOTALL)
        else:
            end_p102_pattern = r'(</div>\s*<div class="clear"></div>\s*<div class="p102-info-related">)'
            if re.search(end_p102_pattern, html):
                html = re.sub(end_p102_pattern, f"{EN_DISCLAIMER_HTML}\n\\1", html, count=1)
            else:
                end_p102_simple = r'(</div>\s*<div class="clear"></div>)'
                html = re.sub(end_p102_simple, f"{EN_DISCLAIMER_HTML}\n\\1", html, count=1)

    html = html.replace("G55-82926499", "+86-755-82926499")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return True


def update_articles_json():
    json_path = "cms_system/cms_data/articles.json"
    if not os.path.exists(json_path):
        print(f"[-] {json_path} not found")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    updated_count = 0
    footer_note_pattern = r'<div class="article-footer-note"[^>]*>.*?</div>'

    for a in articles:
        content = a.get("content", "")
        # Remove any previous disclaimer box
        content = re.sub(r'\s*<div class="article-disclaimer-box"[^>]*>.*?</div>\s*</div>', '</div>', content, flags=re.DOTALL)
        content = re.sub(r'\s*<div class="article-disclaimer-box"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

        if re.search(footer_note_pattern, content, flags=re.DOTALL):
            combined_footer = f"{ZH_FOOTER_NOTE_HTML}\n{ZH_DISCLAIMER_HTML}"
            content = re.sub(footer_note_pattern, combined_footer, content, flags=re.DOTALL)
        elif 'lab_' in a.get('link', ''):
            lab_card_pattern = r'(<div style="margin-top:30px;padding:16px 20px;background:#f8fafc;border:1px dashed #cbd5e1;.*?</div>\s*</div>)'
            if re.search(lab_card_pattern, content, flags=re.DOTALL):
                content = re.sub(lab_card_pattern, rf'\1\n{ZH_DISCLAIMER_HTML}', content, flags=re.DOTALL)
            else:
                content += f"\n{ZH_DISCLAIMER_HTML}"
        else:
            content += f"\n{ZH_DISCLAIMER_HTML}"

        content = content.replace("G55-82926499", "0755-82926499")
        a["content"] = content
        updated_count += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"[OK] Updated {updated_count} articles in {json_path}")
    return True


def main():
    zh_files = sorted(glob.glob("articles/*.html"))
    print(f"Processing {len(zh_files)} ZH articles...")
    zh_ok = 0
    for f in zh_files:
        try:
            process_zh_file(f)
            zh_ok += 1
        except Exception as e:
            print(f"[-] Error on {f}: {e}")
    print(f"[OK] {zh_ok}/{len(zh_files)} ZH articles updated.")

    en_files = sorted(glob.glob("en/articles/*.html"))
    print(f"Processing {len(en_files)} EN articles...")
    en_ok = 0
    for f in en_files:
        try:
            process_en_file(f)
            en_ok += 1
        except Exception as e:
            print(f"[-] Error on {f}: {e}")
    print(f"[OK] {en_ok}/{len(en_files)} EN articles updated.")

    update_articles_json()


if __name__ == "__main__":
    main()
