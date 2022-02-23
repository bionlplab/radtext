import logging
import os
import string
from typing import Union

from bioc import BioCSentence
from bllipparser import RerankingParser

from radtext.core import BioCProcessor
from radtext.models.constants import DEFAULT_OPTIONS


def is_punct(text) -> bool:
    for c in text:
        if c not in string.punctuation:
            return False
    return True


def singleton(cls, *args, **kw):
 instances = {}
 def _singleton(*args, **kw):
    if cls not in instances:
         instances[cls] = cls(*args, **kw)
    return instances[cls]
 return _singleton


@singleton
class BllipParser:
    def __init__(self, model_dir: str=DEFAULT_OPTIONS['--bllip-model']):
        self.model_dir = os.path.expanduser(model_dir)
        print('loading model %s ...' % self.model_dir)
        self.rrp = RerankingParser.from_unified_model_dir(self.model_dir)

    def parse(self, s: Union[None, str]):
        """Parse the sentence text using Reranking parser.

        Args:
            s: one sentence

        Returns:
            ScoredParse: parse tree, ScoredParse object in RerankingParser; None if failed

        Raises:
            ValueError
        """
        if s is None or (isinstance(s, str) and len(s.strip()) == 0):
            raise ValueError('Cannot parse empty sentence: {}'.format(s))
        nbest = self.rrp.parse(str(s))
        return nbest[0].ptb_parse


class BioCParserBllip(BioCProcessor):
    def __init__(self, model_dir: str=DEFAULT_OPTIONS['--bllip-model']):
        super(BioCParserBllip, self).__init__('parse:bllip')
        self.parser = BllipParser(model_dir=model_dir)

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        sentence.infons['parse_tree'] = None
        try:
            text = sentence.text
            print(text)
            if not is_punct(text):
                sentence.infons['nlp_system'] = self.nlp_system
                sentence.infons['nlp_date_time'] = self.nlp_date_time
                sentence.infons['parse_tree'] = str(self.parser.parse(text))
        except Exception as e:
            logging.exception('%s:%s: Cannot parse sentence: %s. %s', docid, sentence.offset, sentence.text, e)
        return sentence
