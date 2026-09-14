# -*- coding: utf-8 -*-
"""
Universal Asset Path Normalizer for English Pages (en/)
Ensures 100% correct relative paths for all assets across:
- en/*.html (depth 1 -> prefix: ../)
- en/*/*.html (depth 2 -> prefix: ../../)
"""

import os
import re

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
EN_DIR = os.path.join(ROOT_DIR, "en")

def normalize_file(filepath):
    rel_from_en = os.path.relpath(filepath, EN_DIR).replace("\\", "/")
    parts = rel_from_en.split("/")
    depth = len(parts) # 1 for en/*.html, 2 for en/articles/*.html, etc.

    correct_prefix = "../" if depth == 1 else "../../"

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original = content

    # 1. Normalize resource/images paths in src, href, data-src, url(...)
    # Matches any variations like:
    #   src="resource/images/..."
    #   src="../resource/images/..."
    #   src="../../resource/images/..."
    #   src="../../../resource/images/..."
    def fix_resource_images(m):
        attr = m.group(1) # e.g. 'src="' or 'url("'
        tail = m.group(2) # e.g. 'wechat/abc.jpg"'
        return f'{attr}{correct_prefix}resource/images/{tail}'

    content = re.sub(
        r'(\b(?:src|href|data-src)=["\'])(?:\.\./)*resource/images/([^"\']+["\'])',
        fix_resource_images,
        content,
        flags=re.IGNORECASE
    )
    content = re.sub(
        r'(url\(["\']?)(?:\.\./)*resource/images/([^"\'\)]+["\']?\))',
        fix_resource_images,
        content,
        flags=re.IGNORECASE
    )

    # 2. Normalize images/ paths (root images folder)
    def fix_root_images(m):
        attr = m.group(1)
        tail = m.group(2)
        # Avoid matching resource/images
        if tail.startswith("images/"):
            tail = tail[7:]
        return f'{attr}{correct_prefix}images/{tail}'

    content = re.sub(
        r'(\b(?:src|href|data-src)=["\'])(?:\.\./)*images/([^"\']+["\'])',
        fix_root_images,
        content,
        flags=re.IGNORECASE
    )
    content = re.sub(
        r'(url\(["\']?)(?:\.\./)*images/([^"\'\)]+["\']?\))',
        fix_root_images,
        content,
        flags=re.IGNORECASE
    )

    # 3. Fix specific broken legacy assets
    if "help_ryzs_0002.html" in filepath:
        content = content.replace('../resource/images/afd7203e032747ddb72c31d760ceea03_32.jpg', '../resource/images/en_banner_about.jpg')
    if "product_hzpyl_0003.html" in filepath or "product_tpxzzd_0002.html" in filepath:
        content = content.replace('../resource/images/afd7203e032747ddb72c31d760ceea03_26.jpg', '../resource/images/en_banner_products.jpg')

    # Replace broken logo.jpg with standard logo
    logo_path = f"{correct_prefix}resource/images/967bbb92f01e4b14a89691e300570a47_4.png"
    content = re.sub(r'src=["\'](?:\.\./)*images/logo\.jpg["\']', f'src="{logo_path}"', content)

    # Replace broken tel.jpg and menu.png
    content = re.sub(r'<h5><a href="tel:186-9197-8530"><img alt="" src="[^"]*tel\.jpg"></a></h5>', '<h5><a href="tel:186-9197-8530" style="font-size:14px;color:#1e3a8a;font-weight:bold;text-decoration:none;">📞 186-9197-8530</a></h5>', content)
    content = re.sub(r'<span class="menu_btn iconfont"><a class="downmenu"><img src="[^"]*menu\.png"></a></span>', '<span class="menu_btn iconfont"><a class="downmenu" style="font-size:24px;cursor:pointer;color:#1e3a8a;">☰</a></span>', content)

    # Remove broken ftico img tags
    content = re.sub(r'<em>\s*<img\s+src="[^"]*ftico\d+\.png">\s*</em>', '', content)

    # Fix wx_b46e6ef9.html title if needed
    if "wx_b46e6ef9.html" in filepath:
        content = re.sub(r'<title>.*?</title>', '<title>Photo Highlights & Milestones - News & Insights - Mellgen Biotechnology</title>', content, flags=re.DOTALL)
        if '<h1' not in content or '<h1 class="p102-info-blk-title"></h1>' in content:
            content = re.sub(r'<h1[^>]*class="p102-info-blk-title"[^>]*>.*?</h1>', '<h1 class="p102-info-blk-title" title="Photo Highlights & Milestones">Photo Highlights & Milestones</h1>', content, flags=re.DOTALL)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def main():
    total_files = 0
    updated_files = 0

    for root, dirs, files in os.walk(EN_DIR):
        if "backup_" in root:
            continue
        for f in files:
            if f.endswith(".html"):
                total_files += 1
                fp = os.path.join(root, f)
                if normalize_file(fp):
                    updated_files += 1

    print(f"Scanned {total_files} English HTML files, updated asset paths in {updated_files} files.")

if __name__ == "__main__":
    main()
