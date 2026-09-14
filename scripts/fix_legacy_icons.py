# -*- coding: utf-8 -*-
"""
Fix the last 3 legacy files (logo, tel, menu) and clean up commented consult-tel-icon.
"""

import os
import re

def fix_last_items():
    legacy_files = [
        "en/help_ryzs_0002.html",
        "en/product_tpxzzd_0002.html",
        "en/product_hzpyl_0003.html"
    ]

    for p in legacy_files:
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Fix logo
        content = content.replace(
            'src="../images/logo.jpg"',
            'src="../resource/images/967bbb92f01e4b14a89691e300570a47_4.png"'
        )

        # Fix tel.jpg -> text / emoji
        content = re.sub(
            r'<h5><a href="tel:186-9197-8530"><img alt="" src="\.\./images/tel\.jpg"></a></h5>',
            '<h5><a href="tel:186-9197-8530" style="font-size:14px;color:#1e3a8a;font-weight:bold;text-decoration:none;">📞 186-9197-8530</a></h5>',
            content
        )

        # Fix menu.png -> unicode hamburger
        content = re.sub(
            r'<span class="menu_btn iconfont"><a class="downmenu"><img src="\.\./images/menu\.png"></a></span>',
            '<span class="menu_btn iconfont"><a class="downmenu" style="font-size:24px;cursor:pointer;color:#1e3a8a;">☰</a></span>',
            content
        )

        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated legacy file: {p}")

    # Remove commented consult-tel-icon.png from en/index.html and en/mellgen_home.html
    for p in ["en/index.html", "en/mellgen_home.html"]:
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        content = content.replace('<img src="../images/consult-tel-icon.png" alt="Phone">', 'Phone')
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned commented icon in: {p}")

if __name__ == "__main__":
    fix_last_items()
