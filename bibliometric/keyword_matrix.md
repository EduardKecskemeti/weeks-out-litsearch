# Keyword matrices and controlled vocabulary

Each column is joined with OR, and the columns with AND. The vocabularies are
the U.S. National Library of Medicine **MeSH** (https://meshb.nlm.nih.gov) and the
**ACM Computing Classification System 2012** (https://www.acm.org/about/class/2012).
Descriptors were looked up on 8 Nov 2026.

## b1v4: body composition, weight and shape from images

b1v4 = b1v3 (matrix below) AND NOT (retina\* OR fundus OR cattle OR cow OR pig OR fish OR
livestock OR animal\* OR "computed tomography" OR gait OR "action recognition"), adopted
9 Nov 2026: the NOT-block removes 74 records, none of them relevant (precision 0.28 → 0.33).

| | Column 1: body measure | Column 2: image source | Column 3: method |
|---|---|---|---|
| **MeSH / ACM CCS** | Body Composition (D001823) → narrower Body Fat Distribution (D050218; entry: body fat patterning) → Adiposity (D050154). Anthropometry (D000886) → narrower Body Mass Index (D015992; entry: Quetelet index), Body Weights and Measures. Somatotypes (D013008; entries: body shape, body type, body build, somatotype) | Photography (D010781) → narrower Photogrammetry, Image Enhancement. Image Processing, Computer-Assisted (D007091; entries: digital image processing, computer-assisted image analysis). Mobile Applications (D063731; entry: smartphone apps). CCS: Computing methodologies → Artificial intelligence → Computer vision → Image and video acquisition; Computer vision representations → Image representations | Machine Learning (D000069550; entry: transfer learning) → narrower Deep Learning (D000077321; entry: hierarchical learning). Neural Networks, Computer (D016571; entries: perceptrons, connectionist models; narrower: convolutional neural networks). CCS: Computing methodologies → Machine learning → Machine learning approaches → Neural networks; Learning paradigms → Supervised learning → Supervised learning by regression |
| **Used in query** | body fat, body composition, adiposity, body shape, physique, body mass index, anthropometry, anthropometric | photograph, photo, 2D image, single image, RGB image, smartphone, computer vision, image-based, silhouette, digital anthropometry | deep learning, machine learning, neural network, convolutional, artificial intelligence, computer vision, automated, 2D image, two-dimensional |
| **Candidates (tested 9 Nov 2026: rejected, see vocabulary_tests.tsv)** | body build, body type, somatotype, body fat distribution | image analysis, image processing, digital image, mobile application, photogrammetry | transfer learning |

## b2: body composition in physique-sport preparation

| | Column 1: population | Column 2: outcome |
|---|---|---|
| **MeSH** | Weight Lifting (D014891; entry: **Bodybuilding**); broader: Sports. There is no separate descriptor for bodybuilding. | Body Composition (D001823); Caloric Restriction (D031204; entries: low-calorie diet, calorie-restricted diet) |
| **Used in query** | bodybuilder, bodybuilding, physique athlete, physique competitor, physique competition, contest preparation, competition preparation | body composition, body fat, fat loss, weight loss, energy restriction, lean mass, fat mass |
| **Candidates (tested 9 Nov 2026: rejected, see vocabulary_tests.tsv)** | weight lifting (broader: also powerlifting and Olympic weightlifting) | caloric restriction, calorie restriction, low-calorie diet |

## b3v5: order, rank and progression learned from images

| | Column 1: method | Column 2: target | Column 3: data |
|---|---|---|---|
| **MeSH / ACM CCS** | CCS: Information systems → Information retrieval → Retrieval models and ranking → Learning to rank; Computing methodologies → Machine learning → Learning paradigms → Supervised learning → Ranking, Learning to rank, Supervised learning by regression. "Siamese network" is in neither vocabulary. | MeSH Disease Progression (D018450; entries: clinical course, clinical progression) | MeSH Photography (D010781); CCS Computer vision |
| **Used in query** | ordinal regression, learning to rank, pairwise ranking, siamese network, siamese neural network, temporal order, image ordering | longitudinal, progression, age estimation, temporal change, disease severity | image, images, photograph, imaging |
| **Candidates (tested 9 Nov 2026, see vocabulary_tests.tsv)** | ranking (broader): rejected; specific phrases order learning, ranking loss, ranking-based, ranking network, pair-wise ranking, triplet ranking, label ranking, ranking-CNN, learning to compare: **adopted (b3v5)** | clinical course: no effect | |

## b5: validation of photographic body-composition estimates (added 9 Nov 2026)

b1v4 requires an ML/automation term, so validation studies of commercial smartphone and
2D-photo apps (which rarely name the method) were missed, including one paper of dataset 2.
b5 is a separate, narrow sub-query; its records not already in b1v3 were exported.

| | Column 1: outcome | Column 2: image source | Column 3: study type |
|---|---|---|---|
| **MeSH** | Body Composition (D001823), Adiposity (D050154) | Photography (D010781), Mobile Applications (D063731); "digital anthropometry" has no descriptor | Reproducibility of Results, Validation Study (publication type) |
| **Used in query** | body fat, body composition, adiposity, fat mass, lean mass, fat-free mass | smartphone, digital anthropometry, 2D image, two-dimensional image, digital image, photograph, 3D optical, three-dimensional optical, optical scan, optical imaging | validity, validation, agreement, reliability, accuracy |

Screening: dedicated 3D optical scanners are excluded (E11, 2D photos only; applied to b1v4 too on 10 Nov 2026); smartphone-camera
captures count as photographic even when they build a 3D avatar.

## b4: AI applied to bodybuilding

Column 1 of b2 (bodybuilding, bodybuilder, physique athlete, physique competitor)
AND column 3 of b1v3 reduced to computer vision, deep learning, machine learning,
artificial intelligence, plus pose estimation. Candidates: neural network,
convolutional, image processing.

## Check against the index terms Scopus assigns

MeSH/Emtree index terms attached to the **included** Scopus records (number of
records), which confirm the mapping above:

- b1v4 (132 included, 2D-only scope): Anthropometry 47, Deep Learning 35, Body Mass Index 19, Body Composition 18, Body Weight 15, Machine Learning 12, Smartphone 7, Artificial Intelligence 7, Photography 6, Mobile Applications 5
- b2 (95 included): Body Composition 68, Weight Lifting 35, Resistance Training 34, Athletes 31, Body Weight 21, Body Image 15, Anthropometry 15, Weight Loss 10, Caloric Restriction 9
- b3v4 (50 included): Deep Learning 31, Diagnostic Imaging 11, Disease Progression 6
