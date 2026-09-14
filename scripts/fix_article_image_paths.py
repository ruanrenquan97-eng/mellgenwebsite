# -*- coding: utf-8 -*-
"""
Ensure all relative asset paths in subdirectories (en/articles, en/products, en/helps, en/Tools)
have the correct relative path prefixes (../../).
"""

import os
import re

def fix_paths():
    subdirs = ["en/articles", "en/products", "en/helps", "en/Tools"]
    total_fixed_images = 0
    total_files_changed = 0

    for sdir in subdirs:
        if not os.path.exists(sdir):
            continue
        for fname in os.listdir(sdir):
            if not fname.endswith(".html"):
                continue
            fpath = os.path.join(sdir, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            original = content

            # Fix 1: src="resource/images/..." -> src="../../resource/images/..."
            content = re.sub(r'src=["\']resource/images/', 'src="../../resource/images/', content)

            # Fix 2: src="../resource/images/..." -> src="../../resource/images/..."
            # (only in these 2-deep subdirectories!)
            content = re.sub(r'src=["\']\.\./resource/images/', 'src="../../resource/images/', content)

            # Fix 3: src="../images/..." -> src="../../images/..." (except where already ../../)
            content = re.sub(r'src=["\']\.\./images/', 'src="../../images/', content)

            # Fix 4: url("resource/images/...") -> url("../../resource/images/...")
            content = re.sub(r'url\(["\']?resource/images/', 'url("../../resource/images/', content)

            # Fix 5: url("../resource/images/...") -> url("../../resource/images/...")
            content = re.sub(r'url\(["\']?\.\./resource/images/', 'url("../../resource/images/', content)

            if content != original:
                total_files_changed += 1
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)

    print(f"Fixed image paths in {total_files_changed} HTML files across subdirectories.")

if __name__ == "__main__":
    fix_paths()
