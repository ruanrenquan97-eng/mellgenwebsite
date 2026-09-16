import re

with open('product_hzpyl.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'(<div class="hyt-product-list-6">)(.*?)(<div class="clear"></div>\s*</div>)'
m = re.search(pattern, html, re.DOTALL)
if m:
    print('Match found!')
    print('Group 1:', m.group(1))
    print('Group 2 length:', len(m.group(2)))
    print('Group 3:', m.group(3))
    pids = re.findall(r'products/([a-zA-Z0-9_\-]+)\.html', m.group(2))
    print('PIDs in group 2:', len(set(pids)), set(pids))
    outside = html[:m.start(2)] + html[m.end(2):]
    pids_out = re.findall(r'products/([a-zA-Z0-9_\-]+)\.html', outside)
    print('PIDs outside group 2:', len(set(pids_out)), set(pids_out))
else:
    print('NO MATCH!')
