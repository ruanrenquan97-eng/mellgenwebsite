import re

homepages = ['index.html', 'mellgen_home.html', 'en/index.html', 'en/mellgen_home.html']
for hp in homepages:
    with open(hp, 'r', encoding='utf-8') as f:
        content = f.read()
    pids = re.findall(r'products/([a-zA-Z0-9_\-]+)\.html', content)
    print(f"{hp}: {len(pids)} product links -> {set(pids)}")
