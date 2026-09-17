import re

with open('products/tphtct.html', 'r', encoding='utf-8') as f:
    cn_html = f.read()

with open('en/products/tphtct.html', 'r', encoding='utf-8') as f:
    en_html = f.read()

rec_pattern = r'((?:</div>\s*){3})\s*(?:<div class=["\']k12-cx-xgcp-4pl-fx1-1-01[\s\S]*?)(?=\s*<div class=["\']g_ft f_fw["\'])'
print("Match in CN html:", bool(re.search(rec_pattern, cn_html)))
print("Match in EN html:", bool(re.search(rec_pattern, en_html)))

# 打印 en_html 中 k12-cx-xgcp-4pl-fx1-1-01 附近内容
pos = en_html.find('k12-cx-xgcp-4pl-fx1-1-01')
if pos != -1:
    print("Found k12 in en_html at pos", pos)
    print(repr(en_html[pos-100:pos+300]))
