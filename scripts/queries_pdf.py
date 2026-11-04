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
                    'from physique photos (Classic Physique) with pairwise ranking · searches run 17–19 Oct 2026', sub)]

story.append(Paragraph('1. Search set-up', h1))
story.append(table([
    [P('Item', cellb), P('Setting', cellb)],
    [P('Research question'), P('How has progress toward contest leanness, or body composition in general, been estimated from ordinary photographs?')],
    [P('Sub-questions'), P('Q1 body composition / shape from 2D images · Q2 body-composition tracking during contest preparation · '
                           'Q3 learning an order or progression from images without absolute labels')],
    [P('Term refinement'), P('Google Scholar Labs: each sub-question asked in natural language; results used only to collect vocabulary and seed papers')],
    [P('Database'), P('OpenAlex (api.openalex.org), field <b>title_and_abstract.search</b>. Web of Science: login failed. '
                      'Scopus: institutional account pending, so only Scopus Preview. Scholar has no type/language filters or export.')],
    [P('Filters (all queries)'), q('publication_year:2016-2025, language:en, type:article|review|conference-paper|book-chapter')],
    [P('Criteria'), P('Articles (incl. reviews), conference papers, book chapters; English; 2016–2025, current year (2026) excluded')],
], [38 * mm, 136 * mm]))

story.append(Paragraph('2. Final queries (used for the dataset)', h1))
story.append(table([
    [P('Block', cellb), P('Q', cellb), P('Query', cellb), P('Hits', cellb)],
    [P('<b>b1v3</b>'), P('Q1'), q(f'{C1} AND {C2} AND {ML3}'), P('804')],
    [P('<b>b2</b>'), P('Q2'), q(B2), P('294')],
    [P('<b>b3v4</b>'), P('Q3'), q(f'{R1} AND {R2} AND {IMG}'), P('138')],
    [P('<b>b4</b>'), P('Q1–Q2'), q(B4), P('18')],
    [P(''), P(''), P('<b>Union of the four queries (unique records)</b>'), P('<b>1,251</b>')],
], [14 * mm, 13 * mm, 133 * mm, 14 * mm], shade=KEEP))
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
        ]
story.append(table(rows, [24 * mm, 82 * mm, 17 * mm, 51 * mm], shade=DROP))
story.append(Paragraph('* The exact wording of b3v2 was not preserved; it is described here from the search log. '
                       'b3v3 is b3v4 without its image concept, as recorded in the log.', note))

story.append(Paragraph('4. From hits to datasets', h1))
story.append(table([
    [P('Step', cellb), P('Records', cellb), P('Notes', cellb)],
    [P('Union of final queries'), P('1,251'), P('')],
    [P('Cleaning'), P('− 84'), P('Spam ads 11 · retractions 5 · front matter / abstract books 21 · no DOI and no source 2 · '
                                'repository copies and preprints 31 · non-English titles 5 · duplicate titles 9')],
    [P('Snowballing'), P('+ 4'), P('Scholar Labs seeds not matched by any query: Liu 2018 (CVPR), Minetto 2023 (Sci. Rep.), '
                                  'Kasper 2021 (Nutrients), Toulany 2023 (Nat. Methods)')],
    [P('<b>Dataset 1 (broad)</b>'), P('<b>1,171</b>'), P('879 articles, 17 reviews, 242 conference papers, 33 book chapters; under the 1,500 limit')],
    [P('<b>Dataset 2 (relevant)</b>'), P('<b>50</b>'), P('Screened from dataset 1; 46 from the search, 4 from snowballing; '
                                                        'themes: photo-based body composition 15, shape/weight from images 9, '
                                                        'contest prep 13, ranking/ordering 11, AI in bodybuilding 2')],
], [38 * mm, 18 * mm, 118 * mm]))

story.append(KeepTogether([
    Paragraph('5. Planned re-run in Scopus / Web of Science', h1),
    Paragraph('When access is approved the four final queries will be run with the same concepts and filters, merged with '
              'the OpenAlex set by DOI, and dataset 2 re-screened. Scopus form (b2 shown; the others follow the same pattern):', body),
    q('TITLE-ABS-KEY(' + B2 + ') AND PUBYEAR &gt; 2015 AND PUBYEAR &lt; 2026 AND LANGUAGE(english) '
      'AND DOCTYPE(ar OR re OR cp OR ch)'),
    Spacer(1, 4),
    Paragraph('Web of Science: the same string in the <b>TS=</b> field, years 2016–2025, document types Article, Review, '
              'Proceedings Paper, Book Chapter, language English.', body)]))

def footer(c, d):
    c.saveState(); c.setFont('DV', 7.5); c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, 'Literature search queries · E. Kecskemeti · Oct 2026')
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, f'{d.page}')
    c.restoreState()

doc = SimpleDocTemplate('search/search_queries.pdf', pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=16 * mm, title='Literature search: queries',
                        author='Eduard Kecskemeti')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('ok')
