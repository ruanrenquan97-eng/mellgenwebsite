import glob
import os
import re

files = sorted(glob.glob('en/articles/wx_*.html'))
print(f"Total WeChat articles: {len(files)}")
for p in files:
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        c = f.read()
    m_title = re.search(r'<title>(.*?)</title>', c)
    t = m_title.group(1).strip() if m_title else 'NO TITLE'
    m_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', c, re.DOTALL)
    h1 = re.sub(r'<[^>]+>', '', m_h1.group(1)).strip() if m_h1 else 'NO H1'
    print(f"{os.path.basename(p)}: title=[{t[:60]}] | h1=[{h1[:60]}]")
