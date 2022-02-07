"""
Run RadText's entire pipeline or partial execution.

Usage:
	pipeline TEXT 

"""
import bioc
import docopt
import pandas as pd
import tqdm
import copy
import logging
import re
import yaml
import spacy

# for deid
from radtext.deid import BioCDeidPhilter
from radtext.pphilter.philter import Philter

# for split_section
from typing import List, Pattern
from radtext.section_split_regex import BioCSectionSplitterRegex

# for preprocess
from radtext.core import BioCPipeline
from radtext.convert_ptb_to_ud import BioCPtb2DepConverter
from radtext.preprocess_spacy import BioCSpacy

# for ner
from typing import Iterable, Tuple
from radtext.ner_regex import NerRegExExtractor, BioCNerRegex

# for neg
from radtext.neg.match_ngrex import NegGrex
from radtext.neg.match_regex import NegRegex
from radtext.neg.neg_cleanup import NegCleanUp
from radtext.neg.neg_pipeline import BioCNeg

# for collect_labels
import collections
from typing import Dict, Set
from radtext.neg.constants import NEGATION, UNCERTAINTY
from radtext.collect_neg_labels import merge_labels, is_cardiomegaly, find_findings, aggregate, create_prediction

SECTION_TITLES = [
    "ABDOMEN AND PELVIS:",
    "CLINICAL HISTORY:",
    "CLINICAL INDICATION:",
    "COMPARISON:",
    "COMPARISON STUDY DATE:",
    "EXAM:",
    "EXAMINATION:",
    "FINDINGS:",
    "HISTORY:",
    "IMPRESSION:",
    "INDICATION:",
    "MEDICAL CONDITION:",
    "PROCEDURE:",
    "REASON FOR EXAM:",
    "REASON FOR STUDY:",
    "REASON FOR THIS EXAMINATION:",
    "TECHNIQUE:",
    "FINAL REPORT",
]

RESOURCE_DIR = 'radtext/resources/'
PHRASES = RESOURCE_DIR + 'cxr14_phrases_v2.yml'
COLLECT_PHRASES = RESOURCE_DIR + 'chexpert_phrases.yml'

REGEX_NEGATION = RESOURCE_DIR + 'patterns/regex_negation.yml'
REGEX_UNCERTAINTY_PRE_NEG = RESOURCE_DIR + 'patterns/regex_uncertainty_pre_negation.yml'
REGEX_UNCERTAINTY_POST_NEG= RESOURCE_DIR + 'patterns/regex_uncertainty_post_negation.yml'
REGEX_DOUBLE_NEG = RESOURCE_DIR + 'patterns/regex_double_negation.yml'
NGREX_NEGATION = RESOURCE_DIR + 'patterns/ngrex_negation.yml'
NGREX_UNCERTAINTY_PRE_NEG = RESOURCE_DIR + 'patterns/ngrex_uncertainty_pre_negation.yml'
NGREX_UNCERTAINTY_POST_NEG = RESOURCE_DIR + 'patterns/ngrex_uncertainty_post_negation.yml'
NGREX_DOUBLE_NEG = RESOURCE_DIR +'patterns/ngrex_double_negation.yml'

POSITIVE = 'p'
NEGATIVE = 'n'
UNCERTAIN = 'u'
NOT_MENTIONED = '-'

class Pipeline():
	def __init__(self, annotators=None):
		self.input_id = None
		self.input_text = None
		self.collection = bioc.BioCCollection()
		self.annotators = annotators

	def input2bioc(self):
		doc = bioc.utils.as_document(self.input_text)
		doc.id = self.input_id
		self.collection.add_document(doc)

	def deid(self):
		philter = Philter()
		deid = BioCDeidPhilter(philter)
		for doc in tqdm.tqdm(self.collection.documents):
			for passage in tqdm.tqdm(doc.passages, leave=False):
				deid.process_passage(passage, doc.id)

	def combine_patterns(self, patterns: List[str]) -> Pattern:
		logger = logging.getLogger(__name__)
		p = '|'.join(patterns)
		logger.debug('Section patterns: %s', p)
		return re.compile(p, re.IGNORECASE | re.MULTILINE)

	def split_section(self):
		section_titles = SECTION_TITLES
		pattern = self.combine_patterns(section_titles)
		sec_splitter = BioCSectionSplitterRegex(regex_pattern=pattern)

		new_collection = bioc.BioCCollection()
		new_collection.infons = copy.deepcopy(self.collection.infons)
		for doc in tqdm.tqdm(self.collection.documents):
			new_doc = sec_splitter.process_document(doc)
			new_collection.add_document(new_doc)
		self.collection = new_collection

	def preprocess(self):
		nlp = spacy.load("en_core_web_sm")
		processor = BioCSpacy(nlp)

		for doc in tqdm.tqdm(self.collection.documents):
			processor.process_document(doc)

	def ner(self):
		nlp = spacy.load("en_core_web_sm")
		extractor = NerRegExExtractor(PHRASES)
		processor = BioCNerRegex(extractor)

		for doc in tqdm.tqdm(self.collection.documents):
			for passage in tqdm.tqdm(doc.passages, leave=False):
				processor.process_passage(passage, doc.id)

	def parse(self):
		nlp = en_core_web_sm.load()
		processor = BioCSpacy(nlp)

		for doc in tqdm.tqdm(self.collection.documents):
			processor.process_document(doc)

	def neg(self):
		regex_actor = NegRegex(
			REGEX_NEGATION,
			REGEX_UNCERTAINTY_PRE_NEG,
			REGEX_UNCERTAINTY_POST_NEG,
			REGEX_DOUBLE_NEG)
		ngrex_actor = NegGrex(
			NGREX_NEGATION,
			NGREX_UNCERTAINTY_PRE_NEG,
			NGREX_UNCERTAINTY_POST_NEG,
			NGREX_DOUBLE_NEG)

		neg_actor = BioCNeg(regex_actor=regex_actor, ngrex_actor=ngrex_actor)
		cleanup_actor = NegCleanUp(None)

		for doc in tqdm.tqdm(self.collection.documents):
			for passage in tqdm.tqdm(doc.passages, leave=False):
				neg_actor.process_passage(passage, doc.id)
				cleanup_actor.process_passage(passage, doc.id)

	def collect_labels(self, phrases_file=COLLECT_PHRASES):
		with open(phrases_file) as fp:
			phrases = yaml.load(fp, yaml.FullLoader)

		rows = []
		cnt = collections.Counter()

		for doc in tqdm.tqdm(self.collection.documents):
			label_dict = aggregate(doc)
			label_dict = merge_labels(label_dict)
			findings = {k: v for k, v in label_dict.items() if k in phrases.keys()}
			findings['docid'] = str(doc.id)
			rows.append(findings)

		columns = ['docid'] + sorted(phrases.keys())
		row_df = pd.DataFrame(sorted(rows, key=lambda x: x['docid']), columns=columns)
		row_df = row_df.fillna(NOT_MENTIONED)

		return row_df

	def process(self, input_text, input_id=0):
		self.input_id = input_id
		self.input_text = input_text

		self.input2bioc()
		if self.annotators == 'csv2bioc':
			return self.collection

		self.deid()
		if self.annotators == 'deid':
			return self.collection

		self.split_section()
		if self.annotators == 'split_section':
			return self.collection

		self.preprocess()
		if self.annotators == 'preprocess':
			return self.collection

		self.ner()
		if self.annotators == 'ner':
			return self.collection

		self.parse()
		if self.annotators == 'parse':
			return self.collection

		self.neg()

		return self.collection

	def __call__(self, doc):
		assert isinstance(doc, str), 'Input should be a string.'
		return self.process(doc)

