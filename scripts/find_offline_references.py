import os
import re
import json

with open('cms_system/cms_data/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

offline_pids = set(p['id'] for p in products if p.get('status') == 'offline' or p.get('show', True) is False)
active_pids = set(p['id'] for p in products if p['id'] not in offline_pids)

print(f"Active PIDs ({len(active_pids)}): {active_pids}")
print(f"Offline PIDs ({len(offline_pids)}): {offline_pids}")

cn_files_with_offline = {}
en_files_with_offline = {}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', '.gemini', 'node_modules', '__pycache__'] and not d.startswith('backup')]
    for f in files:
        if f.endswith('.html'):
            fp = os.path.join(root, f).replace('\\', '/')
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fp_in:
                content = fp_in.read()
            
            # Find any link to offline products: products/xxx.html
            found = set()
            for pid in offline_pids:
                if f"products/{pid}.html" in content:
                    found.add(pid)
                    
            if found:
                if fp.startswith('./en/'):
                    en_files_with_offline[fp] = found
                else:
                    cn_files_with_offline[fp] = found

print("\n=== CN Files containing links to offline products ===")
for fp, pids in sorted(cn_files_with_offline.items()):
    print(f"  {fp}: {len(pids)} offline products -> {pids}")

print("\n=== EN Files containing links to offline products ===")
for fp, pids in sorted(en_files_with_offline.items()):
    print(f"  {fp}: {len(pids)} offline products -> {pids}")
