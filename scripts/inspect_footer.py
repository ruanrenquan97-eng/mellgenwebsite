import re

with open('article_xwzx.html', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'(<dl>\s*<dt>\s*<a href="[^"]*product[^"]*">[\s\S]*?</dl>)', c)
if m:
    print(m.group(1))
