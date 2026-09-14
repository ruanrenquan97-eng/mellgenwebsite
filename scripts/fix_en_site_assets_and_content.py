import os
import re
import glob

def fix_mojibake(text):
    # Fix Latin-1 mojibake where UTF-8 bytes were read as latin-1
    # Often occurs in paragraphs or spans
    def repl(m):
        raw = m.group(0)
        try:
            fixed = raw.encode('latin1').decode('utf-8')
            return fixed
        except Exception:
            return raw

    # Match sequences of latin-1 encoded utf-8 bytes (2 or 3 bytes per char)
    # Typical start bytes for Chinese: \xc0-\xdf (2-byte), \xe0-\xef (3-byte)
    pattern = re.compile(r'[\xc0-\xef][\x80-\xbf]{1,2}(?:[\xc0-\xef][\x80-\xbf]{1,2})*')
    return pattern.sub(repl, text)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    en_dir = os.path.join(root_dir, "en")

    print("[1] Fixing relative image paths in en/articles/...", flush=True)
    article_files = glob.glob(os.path.join(en_dir, "articles", "*.html"))
    fixed_img_articles = 0
    fixed_mojibake_articles = 0

    for fp in article_files:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        orig = content
        # Fix resource/images path
        content = re.sub(r'src=["\']resource/images/', 'src="../../resource/images/', content)
        content = re.sub(r'src=["\']\./resource/images/', 'src="../../resource/images/', content)
        content = re.sub(r'src=["\']\.\./resource/images/', 'src="../../resource/images/', content)

        # Fix wechat section negative margins causing container overflow
        content = re.sub(r'margin-right:\s*-17px;\s*margin-left:\s*-17px;', 'margin-right: 0; margin-left: 0; max-width: 100%;', content)
        content = re.sub(r'margin-right:\s*-20px;\s*margin-left:\s*-20px;', 'margin-right: 0; margin-left: 0; max-width: 100%;', content)

        # Fix mojibake
        if any(c in content for c in ['æ', 'ç', 'é', 'è', 'å', 'ã']):
            content = fix_mojibake(content)
            fixed_mojibake_articles += 1

        if content != orig:
            fixed_img_articles += 1
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)

    print(f"    Updated {fixed_img_articles} article files (mojibake fixed in {fixed_mojibake_articles}).", flush=True)

    print("[2] Fixing root en/*.html asset links...", flush=True)
    root_html = glob.glob(os.path.join(en_dir, "*.html"))
    for fp in root_html:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        orig = content
        # Ensure single ./resource/ or resource/ becomes ../resource/
        content = re.sub(r'src=["\']\./resource/', 'src="../resource/', content)
        content = re.sub(r'src=["\']resource/', 'src="../resource/', content)

        if content != orig:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)

    print("[3] Fixing specific legacy pages (help_ryzs_0002, product_hzpyl_0003, product_tpxzzd_0002)...", flush=True)
    legacy_pages = [
        "help_ryzs_0002.html",
        "product_hzpyl_0003.html",
        "product_tpxzzd_0002.html"
    ]
    for lp in legacy_pages:
        lp_path = os.path.join(en_dir, lp)
        if os.path.exists(lp_path):
            with open(lp_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Fix non-existent css/js
            content = re.sub(r'href=["\']\.\./css/reset750\.css["\']', 'href="../css/reset.css"', content)
            content = re.sub(r'href=["\']\.\./css/67b71d3[a-z0-9]+\.css["\']', 'href="../css/mobile.css"', content)
            content = re.sub(r'<script src=["\']\./js/jquery-1\.10\.1\.min\.js["\']></script>', '<script src="../js/nsw.pc.min.js"></script>', content)
            content = re.sub(r'<script src=["\']\./index\.html67b71d3[a-z0-9]+\.js["\'][^>]*></script>', '', content)
            content = re.sub(r'<script src=["\']\./js/ab77b6ea7f3fbf79\.js["\'][^>]*></script>', '', content)

            # Fix image paths
            content = re.sub(r'src=["\']\./resource/images/', 'src="../resource/images/', content)
            content = re.sub(r'src=["\']\.\./images/logo\.jpg["\']', 'src="../resource/images/967bbb92f01e4b14a89691e300570a47_4.png"', content)
            content = re.sub(r'src=["\']\.\./images/tel\.jpg["\']', 'src="../images/flogo.png"', content)
            content = re.sub(r'src=["\']\.\./images/menu\.png["\']', 'src="../images/flogo.png"', content)

            with open(lp_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"    Fixed assets in {lp}")

    print("[4] Fixing empty title in wx_b46e6ef9.html...", flush=True)
    b46_path = os.path.join(en_dir, "articles", "wx_b46e6ef9.html")
    if os.path.exists(b46_path):
        with open(b46_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        content = re.sub(r'<title>\s*-News & Insights', '<title>Photo Highlights & Milestones - News & Insights', content)
        with open(b46_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("    Updated title in wx_b46e6ef9.html")

    print("[OK] Assets and content cleanup complete!", flush=True)

if __name__ == "__main__":
    main()
