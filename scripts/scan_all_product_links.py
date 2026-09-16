import os
import re
from collections import defaultdict

def scan_product_links():
    cn_links = defaultdict(list)
    en_links = defaultdict(list)
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', '.gemini', 'node_modules', '__pycache__'] and not d.startswith('backup')]
        for f in files:
            if f.endswith('.html'):
                fp = os.path.join(root, f).replace('\\', '/')
                with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                    text = file.read()
                matches = set(re.findall(r'products/([a-zA-Z0-9_\-]+)\.html', text))
                if matches:
                    if fp.startswith('./en/'):
                        for m in matches:
                            en_links[m].append(fp)
                    else:
                        for m in matches:
                            cn_links[m].append(fp)
                            
    print("=== CN product links summary ===")
    for pid in sorted(cn_links.keys()):
        print(f"  {pid:15} linked in {len(cn_links[pid])} files (e.g. {cn_links[pid][:3]})")
        
    print("\n=== EN product links summary ===")
    for pid in sorted(en_links.keys()):
        print(f"  {pid:15} linked in {len(en_links[pid])} files (e.g. {en_links[pid][:3]})")

scan_product_links()
