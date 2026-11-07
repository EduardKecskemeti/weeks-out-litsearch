"""Build the search-queries PDF for the literature-search assignment."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', F + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', F + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVI', F + 'DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DVM', F + 'DejaVuSansMono.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('DV', normal='DV', bold='DVB', italic='DVI', boldItalic='DVB')

INK = colors.HexColor('#1d2433'); MUTED = colors.HexColor('#5b6475')
ACC = colors.HexColor('#2f5d8a'); LINE = colors.HexColor('#cfd6e0')
KEEP = colors.HexColor('#e8f1ea'); DROP = colors.HexColor('#f6ecea'); HEAD = colors.HexColor('#eef2f7')

title = ParagraphStyle('t', fontName='DVB', fontSize=17, leading=21, textColor=INK, spaceAfter=2)
sub = ParagraphStyle('s', fontName='DV', fontSize=9.5, leading=13, textColor=MUTED, spaceAfter=10)
h1 = ParagraphStyle('h1', fontName='DVB', fontSize=12, leading=15, textColor=ACC, spaceBefore=10, spaceAfter=5)
body = ParagraphStyle('b', fontName='DV', fontSize=9, leading=12.5, textColor=INK, spaceAfter=4)
cell = ParagraphStyle('c', fontName='DV', fontSize=7.8, leading=10.2, textColor=INK)
cellb = ParagraphStyle('cb', parent=cell, fontName='DVB')
mono = ParagraphStyle('m', fontName='DVM', fontSize=7.2, leading=9.6, textColor=INK)
note = ParagraphStyle('n', fontName='DVI', fontSize=7.8, leading=10.5, textColor=MUTED, spaceBefore=3)

def P(t, s=cell): return Paragraph(t, s)
def q(t): return Paragraph(t.replace('"', '&quot;'), mono)

def table(rows, widths, shade=None):
    t = Table(rows, colWidths=widths, repeatRows=1)
    st = [('BACKGROUND', (0, 0), (-1, 0), HEAD), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
          ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('BOX', (0, 0), (-1, -1), 0.6, LINE),
          ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
          ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4)]
    if shade:
        st.append(('BACKGROUND', (0, 1), (-1, -1), shade))
    t.setStyle(TableStyle(st))
    return t

C1 = '("body fat" OR "body composition" OR adiposity OR "body shape" OR physique OR "body mass index" OR anthropometry OR anthropometric)'
C2 = '(photograph OR photo OR "2D image" OR "single image" OR "RGB image" OR smartphone OR "computer vision" OR "image-based" OR silhouette OR "digital anthropometry")'
ML = '("deep learning" OR "machine learning" OR "neural network" OR convolutional)'
ML3 = '("deep learning" OR "machine learning" OR "neural network" OR convolutional OR "artificial intelligence" OR "computer vision" OR automated OR "2D image" OR "two-dimensional")'
B2 = ('(bodybuilder OR bodybuilding OR "physique athlete" OR "physique competitor" OR "physique competition" OR '
      '"contest preparation" OR "competition preparation") AND ("body composition" OR "body fat" OR "fat loss" OR '
      '"weight loss" OR "energy restriction" OR "lean mass" OR "fat mass")')
R1 = '("ordinal regression" OR "learning to rank" OR "pairwise ranking" OR "siamese network" OR "siamese neural network" OR "temporal order" OR "image ordering")'
R2 = '(longitudinal OR progression OR "age estimation" OR "temporal change" OR "disease severity")'
IMG = '(image OR images OR photograph OR imaging)'
B3OLD = ('("ordinal regression" OR "learning to rank" OR "pairwise ranking" OR "relative attribute" OR "temporal order" OR '
         '"image ordering" OR siamese) AND (longitudinal OR progression OR "disease stage" OR "temporal change" OR '
         '"age estimation") AND (image OR images OR photograph OR "deep learning")')
B4 = ('(bodybuilding OR bodybuilder OR "physique athlete" OR "physique competitor") AND ("computer vision" OR '
      '"deep learning" OR "machine learning" OR "artificial intelligence" OR "pose estimation")')

story = []
story += [Paragraph('Literature search: queries', title),
          Paragraph('Methodology of Research, assignment 2 · Eduard Kecskemeti · topic: estimating “apparent weeks out” '
                    'from physique photos (Classic Physique) with pairwise ranking · OpenAlex 17–19 Oct 2026, '
                    'Scopus and Web of Science 7 Nov 2026', sub)]

story.append(Paragraph('1. Search set-up', h1))
story.append(table([
    [P('Item', cellb), P('Setting', cellb)],
    [P('Research question'), P('How has progress toward contest leanness, or body composition in general, been estimated from ordinary photographs?')],
    [P('Sub-questions'), P('Q1 body composition / shape from 2D images · Q2 body-composition tracking during contest preparation · '
                           'Q3 learning an order or progression from images without absolute labels')],
    [P('Term refinement'), P('Google Scholar Labs: each sub-question asked in natural language; results used only to collect vocabulary and seed papers')],
    [P('Databases'), P('<b>OpenAlex</b> (api.openalex.org), field <font face="DVM">title_and_abstract.search</font>; '
                       '<b>Scopus</b>, field <font face="DVM">TITLE-ABS</font>; <b>Web of Science Core Collection</b>, fields '
                       '<font face="DVM">TI</font> or <font face="DVM">AB</font>. Scopus and WoS through the university library proxy. '
                       'Google Scholar has no type/language filters or export.')],
    [P('Filters'), P('OpenAlex: <font face="DVM">publication_year:2016-2025, language:en, type:article|review|conference-paper|book-chapter</font><br/>'
                     'Scopus: <font face="DVM">PUBYEAR &gt; 2015 AND PUBYEAR &lt; 2026 AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch))</font><br/>'
                     'WoS: <font face="DVM">PY=(2016-2025) AND LA=(English) AND DT=(Article OR Review OR "Proceedings Paper" OR "Book Chapter")</font>')],
    [P('Criteria'), P('Articles (incl. reviews), conference papers, book chapters; English; 2016–2025, current year (2026) excluded')],
], [38 * mm, 136 * mm]))

story.append(Paragraph('2. Final queries (used for the dataset)', h1))
story.append(Paragraph('The same search string is used in all three databases; only the field syntax differs (section 5).', body))
story.append(table([
    [P('Block', cellb), P('Q', cellb), P('Query', cellb), P('OpenAlex', cellb), P('Scopus', cellb), P('WoS', cellb)],
    [P('<b>b1v3</b>'), P('Q1'), q(f'{C1} AND {C2} AND {ML3}'), P('804'), P('534'), P('345')],
    [P('<b>b2</b>'), P('Q2'), q(B2), P('294'), P('176'), P('137')],
    [P('<b>b3v4</b>'), P('Q3'), q(f'{R1} AND {R2} AND {IMG}'), P('138'), P('90'), P('75')],
    [P('<b>b4</b>'), P('Q1–Q2'), q(B4), P('18'), P('10'), P('9')],
    [P(''), P(''), P('<b>Unique records per database</b>'), P('<b>1,251</b>'), P('<b>810</b>'), P('<b>566</b>')],
], [13 * mm, 11 * mm, 99 * mm, 19 * mm, 17 * mm, 15 * mm], shade=KEEP))
story.append(Paragraph('Block b1 (the original Q1 query, 436 hits, see section 3) is a subset of b1v3 and adds no records; '
                       'it is kept as a label on the records it matches.', note))

story.append(Paragraph('3. Scrapped queries and why they were changed', h1))
rows = [[P('Version', cellb), P('Query', cellb), P('Hits', cellb), P('Problem → change', cellb)],
        [P('<b>Run 1</b> (all blocks)'), P('Queries b1, b2 and b3 (original), with types <font face="DVM">article|review|book-chapter</font> only'),
         P('881 union'), P('Conference papers are a separate OpenAlex type and were excluded; most ML work for Q1/Q3 is published at conferences → added <font face="DVM">conference-paper</font>.')],
        [P('<b>b1</b>'), q(f'{C1} AND {C2} AND {ML}'), P('436<br/>(302 in run 1)'),
         P('Missed seed papers that describe the method without ML words (Majmudar 2022, Ferreira 2025) → third concept widened (b1v3).')],
        [P('<b>b1 without 3rd concept</b>'), q(f'{C1} AND {C2}'), P('3,991'),
         P('Recall fine but far over the 1,500 limit and mostly clinical / apparel noise → rejected.')],
        [P('<b>b3</b> (original)'), q(B3OLD), P('292'),
         P('Bare <i>siamese</i> matched Thai/“Siam” studies; <i>progression</i> without an image term matched oncology → rewritten.')],
        [P('<b>b3v2</b>*'), P('b3 with the third concept replaced by a required neural-network term '
                             '(“deep learning” / “neural network” family)'), P('46'),
         P('Too narrow: lost known Q3 papers → rejected.')],
        [P('<b>b3v3</b>*'), q(f'{R1} AND {R2}'), P('703'),
         P('Specific network phrases fixed the Siam noise, but with no image term most hits were non-imaging → image concept added (b3v4).')],
        [P('<b>Scopus / WoS with keywords</b>'), P('The four final queries in <font face="DVM">TITLE-ABS-KEY</font> (Scopus) and '
                                                   '<font face="DVM">TS=</font> (WoS, title + abstract + keywords)'),
         P('Scopus 974 / 219 / 216 / 13 (1,422 unique); WoS 453 / 199 / 105 / 9 (766 unique)'),
         P('Merged with OpenAlex: about 1,970 works, over the 1,500 limit → '
           'restricted to title and abstract, the same field OpenAlex searches.')],
        ]
story.append(table(rows, [24 * mm, 82 * mm, 17 * mm, 51 * mm], shade=DROP))
story.append(Paragraph('* The exact wording of b3v2 was not preserved; it is described here from the search log. '
                       'b3v3 is b3v4 without its image concept, as recorded in the log. '
                       'The OpenAlex rows are run on 17–19 Oct; the Scopus/WoS keyword run on 7 Nov 2026.', note))

story.append(Paragraph('4. From hits to datasets (PRISMA-style flow)', h1))
story.append(table([
    [P('Step', cellb), P('Records', cellb), P('Notes', cellb)],
    [P('Identified'), P('2,631'), P('OpenAlex 1,251 · Scopus 810 · Web of Science 566 · snowballing 4')],
    [P('After de-duplication'), P('1,338'), P('Records grouped by DOI, then by normalised title; 488 works are in all three databases')],
    [P('Cleaning, OpenAlex-only works'), P('− 63'), P('Rules R1–R7: spam adverts, retraction notices, front matter, no DOI and no venue, '
                                                       'repository copies and preprints, non-English titles, duplicate titles')],
    [P('Cleaning, Scopus / WoS'), P('− 6'), P('D1 year 2026 (WoS early access) 1 · D2 retracted 3 · D3 same work as a removed '
                                               'OpenAlex record 1 · D4 encyclopedia entry 1')],
    [P('<b>Dataset 1 (broad)</b>'), P('<b>1,269</b>'), P('931 articles, 20 reviews, 283 conference papers, 35 book chapters; under the 1,500 limit. '
                                                         'Found by: OpenAlex + Scopus + WoS 488 · OpenAlex + Scopus 239 · OpenAlex only 406 · '
                                                         'OpenAlex + WoS 31 · Scopus + WoS 21 · Scopus only 60 · WoS only 20 · snowballing 4')],
    [P('<b>Dataset 2 (relevant)</b>'), P('<b>50</b>'), P('Screened from dataset 1; 42 found by OpenAlex, 4 only by Scopus/WoS, 4 from snowballing. '
                                                        'Themes: photo-based body composition 15, shape/weight from images 8, '
                                                        'contest prep 11, ranking/ordering 13, AI in bodybuilding 3')],
], [38 * mm, 18 * mm, 118 * mm]))

story.append(KeepTogether([
    Paragraph('5. Database syntax (block b2 as the example)', h1),
    Paragraph('<b>OpenAlex</b> (<font face="DVM">title_and_abstract.search</font>, filters as a separate parameter):', body),
    q(B2), Spacer(1, 4),
    Paragraph('<b>Scopus</b> advanced search:', body),
    q('TITLE-ABS(' + B2 + ') AND PUBYEAR &gt; 2015 AND PUBYEAR &lt; 2026 AND LANGUAGE(english) '
      'AND (DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch))'), Spacer(1, 4),
    Paragraph('<b>Web of Science</b> advanced search (each concept group searched in title or abstract):', body),
    q('(TI=(' + B2.split(' AND ')[0][1:-1] + ') OR AB=(' + B2.split(' AND ')[0][1:-1] + ')) AND (TI=(' + B2.split(' AND ')[1][1:-1]
      + ') OR AB=(' + B2.split(' AND ')[1][1:-1] + ')) AND PY=(2016-2025) AND LA=(English) '
      'AND DT=(Article OR Review OR "Proceedings Paper" OR "Book Chapter")'),
    Paragraph('All twelve exact strings are in search/queries.json in the GitHub repository.', note)]))

def footer(c, d):
    c.saveState(); c.setFont('DV', 7.5); c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, 'Literature search queries · E. Kecskemeti · Nov 2026')
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, f'{d.page}')
    c.restoreState()

doc = SimpleDocTemplate('search/search_queries.pdf', pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=16 * mm, title='Literature search: queries',
                        author='Eduard Kecskemeti')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('ok')
