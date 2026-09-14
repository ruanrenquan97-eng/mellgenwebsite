# -*- coding: utf-8 -*-
"""
Fix missing legacy asset links in help_ryzs_0002, product_hzpyl_0003, and product_tpxzzd_0002.
"""

import os
import re

def fix_legacy_assets():
    fixes = [
        (
            "en/help_ryzs_0002.html",
            "../css/67b2cbe9e4b03b204ca34c85.css"
        ),
        (
            "en/product_hzpyl_0003.html",
            "../css/67b2cbe5e4b03b204ca34c69.css"
        ),
        (
            "en/product_tpxzzd_0002.html",
            "../css/67b2cbe5e4b03b204ca34c69.css"
        )
    ]

    for p, theme_css in fixes:
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Replace reset750.css with reset.css
        content = content.replace('../css/reset750.css', '../css/reset.css')

        # Replace jquery-1.10.1.min.js with nsw.pc.min.js
        content = content.replace('../js/jquery-1.10.1.min.js', '../js/nsw.pc.min.js')

        # Replace 67b71d3...css with theme_css
        content = re.sub(r'\.\./css/67b71d3[a-z0-9]+\.css', theme_css, content)

        # Remove dead script `./index.html67b71d3...js`
        content = re.sub(r'<script\s+src=["\']\./index\.html[0-9a-z]+\.js["\'][^>]*></script>', '', content)

        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed assets in: {p}")

if __name__ == "__main__":
    fix_legacy_assets()
