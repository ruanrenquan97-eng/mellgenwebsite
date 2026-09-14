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

    print(f"Total active English HTML files: {len(html_files)}", flush=True)

    missing_assets = []
    non_en_lang = []
    css_files_used = set()
    templates = {}
    overflow_risk_tags = []
    table_overflows = []

    link_re = re.compile(r'<link[^>]+rel=["\']?stylesheet["\']?[^>]*>', re.I)
    href_re = re.compile(r'href=["\']([^"\']+)["\']', re.I)
    script_re = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.I)
    style_width_re = re.compile(r'style=["\'][^"\']*width\s*:\s*(\d+)px[^"\']*["\']', re.I)
    nowrap_re = re.compile(r'style=["\'][^"\']*white-space\s*:\s*nowrap[^"\']*["\']', re.I)
    table_re = re.compile(r'<table[^>]*>', re.I)

    for file_path in html_files:
        rel_path = os.path.relpath(file_path, root_dir).replace("\\", "/")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()

        # Check html lang
        m_lang = re.search(r'<html[^>]*lang=["\']?([a-zA-Z\-]+)["\']?', content, re.I)
        if not m_lang or m_lang.group(1).lower() != "en":
            non_en_lang.append((rel_path, m_lang.group(1) if m_lang else "None"))

        # Check CSS links
        for m in link_re.finditer(content):
            tag_str = m.group(0)
            hm = href_re.search(tag_str)
            if hm:
                href = hm.group(1)
                clean_href = href.split("?")[0]
                resolved = os.path.normpath(os.path.join(os.path.dirname(file_path), clean_href))
                css_files_used.add(clean_href)
                if not clean_href.startswith("http") and not clean_href.startswith("//"):
                    if not os.path.exists(resolved):
                        missing_assets.append((rel_path, "CSS", href, resolved))

        # Check JS
        for m in script_re.finditer(content):
            src = m.group(1)
            if not src.startswith("http") and not src.startswith("//"):
                clean_src = src.split("?")[0]
                resolved = os.path.normpath(os.path.join(os.path.dirname(file_path), clean_src))
                if not os.path.exists(resolved):
                    missing_assets.append((rel_path, "JS", src, resolved))

        # Check tables with explicit large width > 800px or 1000px
        for tm in table_re.finditer(content):
            t_str = tm.group(0)
            m_w = re.search(r'width=["\']?(\d+)', t_str, re.I)
            if m_w and int(m_w.group(1)) > 800:
                table_overflows.append((rel_path, m_w.group(1)))

        # Group by folder
        parts = rel_path.split("/")
        if len(parts) == 2:
            prefix = parts[1].split("_")[0] if "_" in parts[1] else parts[1].split(".")[0]
            templates.setdefault("root_" + prefix, []).append(rel_path)
        else:
            templates.setdefault(parts[1], []).append(rel_path)

    print("\n--- Summary by Section ---", flush=True)
    for t, files in sorted(templates.items()):
        print(f"  {t}: {len(files)} files", flush=True)

    print("\n--- Missing Assets ---", flush=True)
    if missing_assets:
        print(f"Found {len(missing_assets)} missing asset links:", flush=True)
        for m in missing_assets:
            print(f"  {m[0]} -> {m[1]}: {m[2]} (resolved: {m[3]})", flush=True)
    else:
        print("  None! All CSS and JS files exist on disk.", flush=True)

    print("\n--- HTML lang attribute ---", flush=True)
    if non_en_lang:
        print(f"Found {len(non_en_lang)} files without lang='en':", flush=True)
        for f in non_en_lang[:10]:
            print(f"  {f[0]}: {f[1]}", flush=True)
    else:
        print("  All files have lang='en'!", flush=True)

    print("\n--- CSS files linked across English site ---", flush=True)
    for c in sorted(css_files_used):
        print(f"  {c}", flush=True)

    print("\n--- Tables with fixed width > 800px ---", flush=True)
    print(f"Count: {len(table_overflows)}", flush=True)
    for t in table_overflows[:5]:
        print(f"  {t[0]}: width={t[1]}", flush=True)

if __name__ == "__main__":
    main()
