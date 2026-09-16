import os
import re

files_to_trim = [
    'index.html', 'en/index.html',
    'product_index.html', 'en/product_index.html',
    'product_hzpyl.html', 'en/product_hzpyl.html',
    'article_xwzx.html', 'en/article_xwzx.html',
    'en/articles/wx_b46e6ef9.html'
]

for f in files_to_trim:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        m_ends = list(re.finditer(r'</html>', content, re.I))
        if len(m_ends) > 1 or (len(m_ends) == 1 and len(content[m_ends[0].end():].strip()) > 0):
            trimmed = content[:m_ends[0].end()] + "\n"
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(trimmed)
            print(f"Trimmed {f}: original size {len(content)} -> new size {len(trimmed)}")

# Clean lzdt from sitemap.html and en/sitemap.html
sitemaps = ['sitemap.html', 'en/sitemap.html']
for sm in sitemaps:
    if os.path.exists(sm):
        with open(sm, 'r', encoding='utf-8', errors='ignore') as fp:
            c = fp.read()
        # Remove <li> <h4><a href="...products/lzdt.html"...>...</a></h4></li>
        new_c = re.sub(r'<li>\s*<h4>\s*<a href="[^"]*products/lzdt\.html"[^>]*>.*?</a>\s*</h4>\s*</li>\s*', '', c, flags=re.DOTALL)
        if new_c != c:
            with open(sm, 'w', encoding='utf-8') as fp:
                fp.write(new_c)
            print(f"Removed offline product lzdt from {sm}")

print("Clean broken tails complete!")
