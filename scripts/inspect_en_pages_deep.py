import os
import re

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    en_dir = os.path.join(root_dir, "en")

    html_files = []
    for root, dirs, files in os.walk(en_dir):
        if "backup_" in root:
            continue
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    print(f"Inspecting {len(html_files)} English HTML files...", flush=True)

    missing_images = []
    hardcoded_wide_divs = []
    empty_titles = []
    chinese_text_found = []

    # Regex patterns
    img_re = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)
    title_re = re.compile(r'<title>(.*?)</title>', re.I | re.DOTALL)
    wide_style_re = re.compile(r'style=["\'][^"\']*width\s*:\s*([1-9]\d{3,})px', re.I)
    wide_attr_re = re.compile(r'\bwidth=["\']([1-9]\d{3,})["\']', re.I)

    # Chinese char check
    cn_re = re.compile(r'[\u4e00-\u9fff]')

    for fp in html_files:
        rel = os.path.relpath(fp, root_dir).replace("\\", "/")
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 1. Title check
        tm = title_re.search(content)
        if not tm or not tm.group(1).strip() or tm.group(1).strip().startswith("-"):
            empty_titles.append((rel, tm.group(1).strip() if tm else "NO TITLE TAG"))

        # 2. Hardcoded width > 1200px
        for wm in wide_style_re.finditer(content):
            w = int(wm.group(1))
            if w > 1250:
                hardcoded_wide_divs.append((rel, f"style width:{w}px"))
        for wm in wide_attr_re.finditer(content):
            w = int(wm.group(1))
            if w > 1250:
                hardcoded_wide_divs.append((rel, f"attr width={w}"))

        # Strip comments for text and element checks
        clean_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

        # 3. Image existence check
        for im in img_re.finditer(clean_content):
            src = im.group(1).split("?")[0]
            if not src.startswith("http") and not src.startswith("//") and not src.startswith("data:") and not src.endswith(".php"):
                # resolve
                img_path = os.path.normpath(os.path.join(os.path.dirname(fp), src))
                if not os.path.exists(img_path):
                    missing_images.append((rel, src))

        # 4. Stray Chinese in visible text (excluding comments, script, style)
        # Strip script and style
        no_script = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL | re.I)
        no_style = re.sub(r'<style.*?</style>', '', no_script, flags=re.DOTALL | re.I)
        no_comments = re.sub(r'<!--.*?-->', '', no_style, flags=re.DOTALL)
        # Check title and meta
        meta_cn = cn_re.findall(no_comments)
        if len(meta_cn) > 30: # some pages might have INCI (CN) which is intentional
            chinese_text_found.append((rel, len(meta_cn)))

    print(f"\n1. Empty or malformed titles: {len(empty_titles)}")
    for item in empty_titles[:5]:
        print(f"   {item[0]}: '{item[1]}'")

    print(f"\n2. Hardcoded elements wider than 1250px: {len(hardcoded_wide_divs)}")
    for item in hardcoded_wide_divs[:5]:
        print(f"   {item[0]}: {item[1]}")

    print(f"\n3. Missing local images: {len(missing_images)}")
    missing_by_src = {}
    for rel, src in missing_images:
        missing_by_src[src] = missing_by_src.get(src, 0) + 1
    print("   Top missing image src patterns:")
    for src, count in sorted(missing_by_src.items(), key=lambda x: x[1], reverse=True)[:25]:
        print(f"     [{count} occurrences] {src}")

    print(f"\n4. Pages with substantial Chinese characters (>30): {len(chinese_text_found)}")
    for item in chinese_text_found[:5]:
        print(f"   {item[0]}: {item[1]} chars")

if __name__ == "__main__":
    main()
