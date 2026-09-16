import os
import json

backups = [
    'cms_system/cms_data_backup_toupi_20260916_105231',
    'cms_system/cms_data_backup_compliance_20260916_111237',
    'cms_system/cms_data_backup_hzpyl_only_20260916_113525'
]

for b in backups:
    p_path = os.path.join(b, 'products.json')
    if os.path.exists(p_path):
        with open(p_path, 'r', encoding='utf-8') as f:
            prods = json.load(f)
        pub = [p['id'] for p in prods if p.get('status') != 'offline' and p.get('show', True) is not False]
        print(f"{b}: total {len(prods)}, published/active {len(pub)}: {pub}")
