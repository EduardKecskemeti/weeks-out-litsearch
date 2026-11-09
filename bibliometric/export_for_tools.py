"""Write the screened Scopus set in Scopus' own CSV layout for VOSviewer and Biblioshiny.

Output stays in the git-ignored licensed/analysis/ folder (it contains the licensed
abstracts and reference lists): scopus_included.csv (303 records, all 45 columns,
Scopus header order) and scopus_retrieved_all.csv (810 records, for comparison).
Also writes a first VOSviewer thesaurus for keyword variants (public).
"""
import csv, os
csv.field_size_limit(10**9)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dec = {l.split('\t')[0]: l.split('\t')[3] for l in open('results/screening_scopus.tsv', encoding='utf-8').read().strip().split('\n')[1:]}
seen, rows, header = set(), [], None
for b in ['b1v3', 'b2', 'b3v5', 'b4']:
    rd = csv.DictReader(open(f'licensed/scopus_ta/scopus_{b}.csv', encoding='utf-8-sig'))
    header = header or rd.fieldnames
    for r in rd:
        if r['EID'] not in seen:
            seen.add(r['EID']); rows.append(r)
os.makedirs('licensed/analysis', exist_ok=True)
for name, sel in (('scopus_included.csv', [r for r in rows if dec[r['EID']] == 'include']), ('scopus_retrieved_all.csv', rows)):
    with open(f'licensed/analysis/{name}', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=header, quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(sel)
    print(name, len(sel))
# VOSviewer thesaurus: label -> replace by (tab-separated, header required by VOSviewer)
pairs = [('bodybuilders', 'bodybuilding'), ('bodybuilder', 'bodybuilding'), ('body building', 'bodybuilding'),
         ('cnn', 'convolutional neural network'), ('cnns', 'convolutional neural network'),
         ('convolutional neural networks', 'convolutional neural network'), ('convolutional neural network (cnn)', 'convolutional neural network'),
         ('deep neural networks', 'deep neural network'), ('neural networks', 'neural network'),
         ('siamese networks', 'siamese network'), ('siamese neural network', 'siamese network'), ('siamese neural networks', 'siamese network'),
         ('bmi', 'body mass index'), ('body mass index (bmi)', 'body mass index'),
         ('physique athletes', 'physique athlete'), ('athlete', 'athletes'),
         ('anthropometric measurements', 'anthropometric measurement'), ('anthropometrics', 'anthropometry'),
         ('3d reconstruction', '3d human reconstruction'), ('smpl', 'smpl model'),
         ('dxa', 'dual-energy x-ray absorptiometry'), ('dexa', 'dual-energy x-ray absorptiometry'),
         ('learning-to-rank', 'learning to rank'), ('ordinal classification', 'ordinal regression'),
         ('energy deficit', 'energy restriction'), ('caloric restriction', 'energy restriction'), ('calorie restriction', 'energy restriction')]
os.makedirs('bibliometric/vosviewer', exist_ok=True)
with open('bibliometric/vosviewer/thesaurus_keywords.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write('label\treplace by\n')
    for a, b in pairs:
        f.write(f'{a}\t{b}\n')
