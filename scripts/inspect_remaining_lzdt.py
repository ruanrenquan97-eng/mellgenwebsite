import re

files_with_lzdt = [
    'article_cjwt.html', 'article_cpbk.html', 'article_hzal_0002.html',
    'articles/lab_placenta_efficacy.html', 'articles/mejswc.html', 'articles/mejswy4690.html',
    'articles/wx_c5dff9d3.html', 'articles/wx_fa691f73.html', 'help_dydsp.html',
    'helps/tdhy4.html', 'helps/zgkjcx2546.html', 'helps/zgkjcx8889.html', 'helps/zh1.html',
    'product_zzfsdb.html'
]

for f in files_with_lzdt:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        lines = fp.readlines()
    for i, l in enumerate(lines):
        if 'lzdt' in l:
            print(f"{f}:{i+1} -> {l.strip()[:100]}")
