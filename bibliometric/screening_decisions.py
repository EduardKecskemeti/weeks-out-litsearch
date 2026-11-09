"""Title/abstract screening of the Scopus title+abstract results (first pass).

Decisions are made per block, by position in the Scopus export of that block
(licensed/scopus_ta/scopus_<block>.csv, Scopus default order), and written out
by EID in results/screening_scopus.tsv. A record that appears in several blocks
is included if any block includes it.

Inclusion criteria
  b1v3  estimates human body composition, adiposity, weight/BMI, whole-body
        anthropometric measurements or body shape from optical images
        (photographs, smartphone, video, depth cameras, 3D surface scans)
  b2    physique sport (bodybuilding, physique/figure/bikini/fitness
        competitors): body composition, diet, energy restriction, contest
        preparation and its physiological or psychological effects
  b3v5  ranking, ordinal regression, Siamese/pairwise comparison or temporal
        ordering applied to images to estimate progression, severity, age or order
  b4    AI / machine learning applied to bodybuilding or resistance training

Exclusion codes
  E1 non-human subject (animals, plants, objects)
  E2 other imaging modality (CT, MRI, X-ray, retinal fundus, ultrasound)
  E3 pose, motion, activity, gait or person identification only
  E4 apparel, virtual try-on, rendering or avatars without body measurement
  E5 diet/nutrition apps or interventions without image-based body measurement
  E6 other topic or body-part (facial, hand, foot, head) anthropometry
  E7 drugs, toxicology or clinical case reports (b2)
  E8 other sport or non-physique population (b2, b4)
  E9 clinical/longitudinal imaging without a ranking or ordinal method (b3v5)
  E10 not a research contribution (encyclopedia entry, technical report)
For b1v3 the exclusion code was assigned from the title with keyword rules
(EXCL_RULES below) after the include/exclude decision was made by hand.
"""

INCLUDE = {
    'b1v3': {0, 9, 11, 12, 15, 17, 20, 28, 32, 34, 35, 41, 43, 44, 46, 48, 49, 53, 55, 66, 67, 68, 71, 78,
             80, 92, 94, 96, 104, 113, 114, 115, 120, 122, 123, 125, 126, 127, 130, 131, 135, 138, 147, 149,
             156, 163, 164, 165, 170, 173, 174, 176, 186, 188, 192, 195, 209, 212, 213, 217, 222, 226, 231,
             232, 233, 235, 236, 239, 241, 243, 244, 246, 254, 256, 261, 262, 264, 265, 266, 267,
             270, 273, 277, 281, 283, 287, 288, 293, 295, 297, 306, 307, 316, 318, 319, 320, 323, 324, 327,
             341, 344, 349, 350, 358, 360, 362, 368, 374, 378, 382, 388, 393, 403, 404, 406, 408, 411, 418,
             423, 425, 426, 431, 434, 436, 439, 440, 446, 447, 455, 456, 460, 469, 472, 474, 479, 480, 485,
             486, 487, 490, 494, 503, 504, 510, 512, 522, 524, 525, 527, 528, 532, 533},
    'b2': {0, 1, 2, 6, 7, 8, 11, 12, 16, 17, 18, 21, 22, 25, 27, 28, 29, 31, 35, 36, 39, 42, 44, 45, 46, 50,
           51, 53, 54, 55, 57, 59, 65, 66, 67, 68, 69, 71, 77, 78, 79, 80, 82, 83, 84, 86, 87, 88, 89, 90, 95,
           97, 99, 102, 109, 110, 111, 112, 113, 114, 115, 118, 119, 121, 124, 125, 126, 127, 129, 130, 131,
           135, 139, 140, 144, 145, 146, 147, 148, 149, 150, 151, 152, 154, 157, 159, 164, 165, 167, 168,
           169, 170, 171, 172, 174},
    # b3v5 = the 90 b3v4 records (positions 0-89) + 25 records added by the specific
    # ranking phrases (positions 90-114, file scopus_b3v5_added.csv, exported 9 Nov 2026)
    'b3v5': {0, 3, 4, 5, 6, 7, 10, 11, 13, 16, 17, 23, 25, 26, 27, 29, 30, 32, 33, 34, 35, 36, 38, 40, 41,
             43, 44, 45, 47, 48, 50, 51, 53, 55, 57, 60, 61, 62, 64, 65, 66, 68, 71, 73, 74, 75, 77, 78, 85, 86,
             90, 91, 92, 93, 95, 97, 98, 100, 101, 103, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114},
    'b4': {0, 1, 2, 3, 7, 9},
}

EXCLUDE_CODE = {
    'b2': {**{i: 'E7' for i in (3, 9, 14, 19, 20, 24, 26, 30, 33, 58, 61, 74, 75, 85, 91, 98, 101, 105, 108,
                               116, 117, 122, 123, 128, 136, 143, 153, 156, 161, 175)},
           **{i: 'E1' for i in (10, 38, 41)},
           **{i: 'E8' for i in (4, 32, 49, 62, 63, 70, 93, 137, 158, 160, 162, 173)},
           15: 'E10'},
    'b3v5': {i: 'E6' for i in (1, 12, 28, 39, 42, 52, 54, 56, 70, 79, 80, 94, 96, 99, 102, 104)},
    'b4': {5: 'E8'},
}
DEFAULT_EXCLUDE = {'b2': 'E6', 'b3v5': 'E9', 'b4': 'E6'}

# b1v3: code from the title, first matching rule wins, otherwise E6
EXCL_RULES = [
    ('E1', r'\b(cattle|cow|bovine|pig|pigs|fish|shrimp|salmon|sheep|calves|calf|dairy|livestock|ruminant|snake|beetle|zebrafish|elegans|pacu|larimichthys|animal|poultry|mice)\b'),
    ('E2', r'\b(ct|mri|magnetic resonance|computed tomography|tomograph\w*|radiograph\w*|x-ray|fundus|retina\w*|ophthalm\w*|ultrasound|echocardiograph\w*|optic disc|mammograph\w*|cardiac|carotid)\b'),
    ('E3', r'\b(pose|poses|posture|gait|motion|activity|activities|action|gesture|re-identification|tracking|fall|movement|kinematics|people localization|person identification|crowd)\b'),
    ('E4', r'\b(garment|garments|cloth|clothing|try-on|tryon|fashion|avatar|avatars|rendering|animation|animations|apparel|dress|corset|mannequin|wrinkles)\b'),
    ('E5', r'\b(diet|dietary|nutrition|nutritional|food|foods|sodium|salt|app|apps|application|intervention|trial|weight loss|diabetes)\b'),
]
