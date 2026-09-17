#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for article disclaimers across ZH and EN articles.
"""

import glob
import re
import sys

def verify():
    zh_files = sorted(glob.glob("articles/*.html"))
    en_files = sorted(glob.glob("en/articles/*.html"))

    errors = []

    print(f"=== Verifying {len(zh_files)} Chinese articles ===")
    for f in zh_files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            c = fp.read()
        if "article-disclaimer-box" not in c:
            errors.append(f"ZH missing disclaimer box: {f}")
        if "版权与合规免责声明" not in c:
            errors.append(f"ZH missing disclaimer title: {f}")
        if "G55-82926499" in c:
            errors.append(f"ZH has G55 typo: {f}")

    print(f"=== Verifying {len(en_files)} English articles ===")
    for f in en_files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            c = fp.read()
        if "article-disclaimer-box" not in c:
            errors.append(f"EN missing disclaimer box: {f}")
        if "Regulatory &amp; Technical Disclaimer" not in c and "Regulatory & Technical Disclaimer" not in c:
            errors.append(f"EN missing disclaimer title: {f}")
        if "G55-82926499" in c:
            errors.append(f"EN has G55 typo: {f}")

    print(f"\nVerification Results:")
    if not errors:
        print(f"[ALL PASS] Successfully verified {len(zh_files)} ZH and {len(en_files)} EN articles!")
        print(f"Total articles verified: {len(zh_files) + len(en_files)}")
        return 0
    else:
        print(f"[FAIL] Found {len(errors)} errors:")
        for err in errors[:20]:
            print(f"  - {err}")
        return 1

if __name__ == "__main__":
    sys.exit(verify())
