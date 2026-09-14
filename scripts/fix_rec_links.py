import glob, re
pat = re.compile(r'(<a\s+href=[^>]*zzjydb\.html[^>]*>\s*<img[^>]*src=[^>]*?)9b89259b4fb24ad2bcc390737279f8ff_30\.jpg', re.I)
c = 0
for g in ['products/*.html', 'en/products/*.html', 'articles/*.html', '*.html']:
    for f in glob.glob(g):
        with open(f, 'r', encoding='utf-8') as fp:
            txt = fp.read()
        if pat.search(txt):
            txt = pat.sub(r'\g<1>bottle_zzjydb.jpg', txt)
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(txt)
            c += 1
print('Fixed files:', c)
