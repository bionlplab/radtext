from pathlib import Path
from typing import Dict, Union

from bioc import BioCCollection, BioCDocument, BioCPassage, BioCSentence
import stanza
import spacy

from stanza.pipeline.core import ResourcesFileNotFoundError

from radtext.cmd.ner import load_yml
from radtext.core import BioCProcessor
from radtext.models.bllipparser import BioCParserBllip
from radtext.models.constants import DEFAULT_OPTIONS
from radtext.models.deid import BioCDeidPhilter
from radtext.models.ner.ner_spacy import BioCNerSpacy, NerSpacyExtractor
from radtext.models.ner.radlex import RadLex4
from radtext.models.preprocess_stanza import BioCStanza
from radtext.models.section_split.section_split_medspacy import \
				BioCSectionSplitterMedSpacy
from radtext.models.section_split.section_split_regex import \
	BioCSectionSplitterRegex, combine_patterns
from radtext.models.preprocess_spacy import BioCSpacy
from radtext.models.ner.ner_regex import NerRegExExtractor, BioCNerRegex
from radtext.models.neg.match_ngrex import NegGrexPatterns
from radtext.models.neg import NegRegexPatterns
from radtext.models.neg.neg import BioCNeg
from radtext.models.sentence_split_nltk import BioCSSplitterNLTK
from radtext.models.tree2dep import BioCPtb2DepConverter

DEFAULT_ANNOTATORS = ['deid', 'split_section_regex', 'ssplit', 'ner_regex',
					  'parse', 'tree2dep', 'neg']


class Pipeline():
	def __init__(self, annotators=None, argv=None):
		if annotators is None:
			annotators = DEFAULT_ANNOTATORS
		if argv is None:
			argv = DEFAULT_OPTIONS

		self.annotators = annotators
		self.argv = argv

		self.processors = {}  # type: Dict[str, BioCProcessor]
		if 'deid' in annotators:
			processor = BioCDeidPhilter(argv['--repl'])
			self.processors['deid'] = processor

		if 'split_section_regex' in annotators:
			with open(argv['--section-titles']) as fp:
				section_titles = [line.strip() for line in fp]
			pattern = combine_patterns(section_titles)
			processor = BioCSectionSplitterRegex(regex_pattern=pattern)
			self.processors['split_section_regex'] = processor

		if 'split_section_medspacy' in annotators:
			import medspacy
			nlp = medspacy.load(enable=["sectionizer"])
			processor = BioCSectionSplitterMedSpacy(nlp)
			self.processors['split_section_medspacy'] = processor

		if 'preprocess_spacy' in annotators:
			try:
				nlp = spacy.load(argv['--spacy-model'])
			except IOError:
				print('Install spacy model using '
					  '\'python -m spacy download en_core_web_sm\'')
				return
			processor = BioCSpacy(nlp)
			self.processors['preprocess_spacy'] = processor

		if 'preprocess_stanza' in annotators:
			try:
				nlp = stanza.Pipeline('en',
									  processors='tokenize,pos,lemma,depparse')
			except ResourcesFileNotFoundError:
				print('Install stanza model using \'stanza.download()')
				return
			processor = BioCStanza(nlp)
			self.processors['preprocess_stanza'] = processor

		if 'parse' in annotators:
			processor = BioCParserBllip(model_dir=argv['--bllip_model'])
			self.processors['parse'] = processor

		if 'ssplit' in annotators:
			processor = BioCSSplitterNLTK(newline=argv['--newline'])
			self.processors['ssplit'] = processor

		if 'ner_regex' in annotators:
			patterns = load_yml(argv['--phrases'])
			extractor = NerRegExExtractor(patterns)
			processor = BioCNerRegex(extractor,
									 name=Path(argv['--phrases']).stem)
			self.processors['ner_regex'] = processor

		if 'ner_spacy' in annotators:
			nlp = spacy.load(argv['--spacy-model'],
							 exclude=['ner', 'parser', 'senter'])
			radlex = RadLex4(argv['--radlex'])
			matchers = radlex.get_spacy_matchers(nlp)
			extractor = NerSpacyExtractor(nlp, matchers)
			processor = BioCNerSpacy(extractor, 'RadLex')
			self.processors['ner_spacy'] = processor

		if 'neg' in annotators:
			regex_actor = NegRegexPatterns()
			regex_actor.load_yml2(argv['--regex_patterns'])
			ngrex_actor = NegGrexPatterns()
			ngrex_actor.load_yml2(argv['--ngrex_patterns'])

			processor = BioCNeg(regex_actor=regex_actor,
								ngrex_actor=ngrex_actor)
			self.processors['neg'] = processor

		if 'tree2dep' in annotators:
			processor = BioCPtb2DepConverter()
			self.processors['tree2dep'] = processor

	def process_collection(self, collection: BioCCollection) -> BioCCollection:
		for annotator in self.annotators:
			self.processors[annotator].process_collection(collection)
		return collection

	def process_document(self, document: BioCDocument) -> BioCDocument:
		for annotator in self.annotators:
			document = self.processors[annotator].process_document(document)
		return document

	def process_passage(self, passage: BioCPassage) -> BioCPassage:
		for annotator in self.annotators:
			passage = self.processors[annotator].process_passage(passage)
		return passage

	def process_sentence(self, s: BioCSentence) -> BioCSentence:
		for annotator in self.annotators:
			s = self.processors[annotator].process_sentence(s)
		return s

	def __call__(self, doc:Union[BioCCollection, BioCDocument, BioCPassage, BioCSentence, str]):
		if isinstance(doc, BioCCollection):
			return self.process_collection(doc)
		elif isinstance(doc, BioCDocument):
			return self.process_document(doc)
		elif isinstance(doc, BioCPassage):
			return self.process_passage(doc)
		elif isinstance(doc, BioCSentence):
			return self.process_sentence(doc)
		elif isinstance(doc, str):
			return self.process_sentence(BioCSentence.of_text(doc))
		else:
			raise TypeError('Input should be a string or bioc data model.')
