from pathlib import Path
from typing import List

import stanza
import spacy

from stanza.pipeline.core import ResourcesFileNotFoundError

from radtext.cmd.ner import load_yml
from radtext.core import BioCProcessor, BioCPipeline
from radtext.models.bllipparser import BioCParserBllip
from radtext.models.constants import DEFAULT_OPTIONS, DEFAULT_ANNOTATORS
from radtext.models.deid import BioCDeidPhilter
from radtext.models.ner.ner_spacy import BioCNerSpacy, NerSpacyExtractor
from radtext.models.ner.radlex import RadLex4
from radtext.models.preprocess_stanza import BioCStanza
from radtext.models.section_split.section_split_medspacy import BioCSectionSplitterMedSpacy
from radtext.models.section_split.section_split_regex import BioCSectionSplitterRegex, combine_patterns
from radtext.models.preprocess_spacy import BioCSpacy
from radtext.models.ner.ner_regex import NerRegExExtractor, BioCNerRegex
from radtext.models.neg.match_ngrex import NegGrexPatterns
from radtext.models.neg import NegRegexPatterns
from radtext.models.neg.neg import BioCNeg
from radtext.models.sentence_split_nltk import BioCSSplitterNLTK
from radtext.models.tree2dep import BioCPtb2DepConverter


class Pipeline(BioCPipeline):
	def __init__(self, annotators: List[str]=None, argv=None):
		super(Pipeline, self).__init__()

		if annotators is None:
			annotators = DEFAULT_ANNOTATORS
		if argv is None:
			argv = DEFAULT_OPTIONS

		self.annotators = annotators
		self.argv = argv

		self.processors = []  # type: List[BioCProcessor]
		for annotator in annotators:
			if annotator == 'deid:philter':
				processor = BioCDeidPhilter(argv['--repl'])
				self.processors.append(processor)
			elif annotator == 'secsplit:regex':
				with open(argv['--section-titles']) as fp:
					section_titles = [line.strip() for line in fp]
				pattern = combine_patterns(section_titles)
				processor = BioCSectionSplitterRegex(regex_pattern=pattern)
				self.processors.append(processor)
			elif annotator == 'secsplit:medspacy':
				import medspacy
				nlp = medspacy.load(enable=["sectionizer"])
				processor = BioCSectionSplitterMedSpacy(nlp)
				self.processors.append(processor)
			elif annotator == 'preprocess:spacy':
				try:
					nlp = spacy.load(argv['--spacy-model'])
				except IOError:
					print('Install spacy model using \'python -m spacy download en_core_web_sm\'')
					return
				processor = BioCSpacy(nlp)
				self.processors.append(processor)
			elif annotator == 'preprocess:stanza':
				try:
					nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')
				except ResourcesFileNotFoundError:
					print('Install stanza model using \'stanza.download()')
					return
				processor = BioCStanza(nlp)
				self.processors.append(processor)
			elif annotator == 'parse:bllip':
				processor = BioCParserBllip(model_dir=argv['--bllip-model'])
				self.processors.append(processor)
			elif annotator == 'ssplit:nltk':
				processor = BioCSSplitterNLTK(newline=argv['--newline'])
				self.processors.append(processor)
			elif annotator == 'ner:regex':
				patterns = load_yml(argv['--phrases'])
				extractor = NerRegExExtractor(patterns)
				processor = BioCNerRegex(extractor, name=Path(argv['--phrases']).stem)
				self.processors.append(processor)
			elif annotator == 'ner:spacy':
				nlp = spacy.load(argv['--spacy-model'], exclude=['ner', 'parser', 'senter'])
				radlex = RadLex4(argv['--radlex'])
				matchers = radlex.get_spacy_matchers(nlp)
				extractor = NerSpacyExtractor(nlp, matchers)
				processor = BioCNerSpacy(extractor, 'RadLex')
				self.processors.append(processor)
			elif annotator == 'neg:negbio':
				regex_actor = NegRegexPatterns()
				regex_actor.load_yml2(argv['--regex_patterns'])
				ngrex_actor = NegGrexPatterns()
				ngrex_actor.load_yml2(argv['--ngrex_patterns'])
				processor = BioCNeg(regex_actor=regex_actor, ngrex_actor=ngrex_actor)
				self.processors.append(processor)
			elif annotator == 'tree2dep':
				processor = BioCPtb2DepConverter()
				self.processors.append(processor)
			else:
				raise KeyError('%s: Do not support this annotator' % annotator)
