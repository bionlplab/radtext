from pathlib import Path

UNCERTAINTY = "possible"
NEGATION = "absent"
POSITIVE = "present"

# HOME_DIR = Path.home()
LOCAL_DIR = Path.home() / '.radtext'
LOCAL_RESOURCE_DIR = LOCAL_DIR / 'resources'
RADTEXT_RESOURCES_GITHUB = 'https://raw.githubusercontent.com/bionlplab/radtext-resources/main/resources'

DEFAULT_OPTIONS = {
	'--rep': 'X',
	'--section-titles': LOCAL_RESOURCE_DIR / 'section_titles.txt',
	'--spacy-model': 'en_core_web_sm',
	'--bllip-model': LOCAL_DIR / 'bllipparser/BLLIP-GENIA-PubMed',
	'--newline': False,
	'--phrases': LOCAL_RESOURCE_DIR / 'cxr14_phrases_v2.yml',
	'--radlex': LOCAL_RESOURCE_DIR / 'Radlex4.1.xlsx',
	'--regex_patterns': LOCAL_RESOURCE_DIR / 'patterns/regex_patterns.yml',
	'--ngrex_patterns': LOCAL_RESOURCE_DIR / 'patterns/ngrex_patterns.yml',
}

DEFAULT_ANNOTATORS = [
	'deid:philter',
	'secsplit:regex',
	'ssplit:nltk',
	'ner:regex',
	'parse:bllip',
	'tree2dep',
	'neg:negbio'
]

ALL_ANNOTATORS = [
	'deid:philter',
	'secsplit:regex',
	'secsplit:medspacy',
	'ssplit:nltk',
	'ner:regex',
	'ner:spacy',
	'parse:bllip',
	'tree2dep',
	'neg:negbio',
]

BLLIP_MODEL_URL = 'https://nlp.stanford.edu/~mcclosky/models/BLLIP-GENIA-PubMed.tar.bz2'
