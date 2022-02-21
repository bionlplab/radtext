from pathlib import Path

UNCERTAINTY = "possible"
NEGATION = "absent"
POSITIVE = "present"

RESOURCE_DIR = Path('radtext/resources')
DEFAULT_OPTIONS = {
	'--rep': 'X',
	'--section-titles': RESOURCE_DIR / 'section_titles.txt',
	'--spacy-model': 'en_core_web_sm',
	'--bllip-model': str(Path.home() / '.radtext/bllipparser/BLLIP-GENIA-PubMed'),
	'--newline': False,
	'--phrases': RESOURCE_DIR / 'cxr14_phrases_v2.yml',
	'--radlex': RESOURCE_DIR / 'Radlex4.1.xlsx',
	'--regex_patterns': RESOURCE_DIR / 'patterns/regex_patterns.yml',
	'--ngrex_patterns': RESOURCE_DIR / 'patterns/ngrex_patterns.yml',
}