import logging
import os
import string
import tempfile
from typing import Union

from bioc import BioCSentence
from bllipparser import ModelFetcher
from bllipparser import RerankingParser

from radtext.core import BioCProcessor

MODELS = {
    'BLLIP-GENIA-PubMed': 'https://nlp.stanford.edu/~mcclosky/models/BLLIP-GENIA-PubMed.tar.bz2',
}


def is_punct(text) -> bool:
    for c in text:
        if c not in string.punctuation:
            return False
    return True


class BllipParser:
    _rrp = None

    def __init__(self, model_dir=None, model_name='BLLIP-GENIA-PubMed'):
        super(BllipParser, self).__init__()
        self.model_dir = model_dir
        self.model_name = model_name

    @property
    def rrp(self):
        if not self._rrp:
            if self.model_dir is None:
                logging.debug("downloading GENIA+PubMed model if necessary ...")
                self.model_dir = ModelFetcher.download_and_install_model(
                    MODELS['BLLIP-GENIA-PubMed'],
                    os.path.join(tempfile.gettempdir(), 'models'))
            elif not os.path.exists(self.model_dir) \
                    or not os.path.exists(os.path.join(self.model_dir, self.model_name)):
                self.model_dir = ModelFetcher.download_and_install_model(
                    MODELS[self.model_name],
                    self.model_dir)
            else:
                self.model_dir = os.path.join(self.model_dir, self.model_name)
            self.model_dir = os.path.expanduser(self.model_dir)
            logging.debug('loading model %s ...' % self.model_dir)
            self._rrp = RerankingParser.from_unified_model_dir(self.model_dir)
        return self._rrp

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
    PARSE_TREE_ATTRIBUTE = 'parse tree'

    def __init__(self, model_dir=None, model_name='BLLIP-GENIA-PubMed'):
        self.parser = BllipParser(model_dir=model_dir, model_name=model_name)

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        sentence.infons[self.PARSE_TREE_ATTRIBUTE] = None
        try:
            text = sentence.text
            if not is_punct(text):
                sentence.infons[self.PARSE_TREE_ATTRIBUTE] = str(self.parser.parse(text))
        except Exception as e:
            logging.exception('%s:%s: Cannot parse sentence: %s. %s', docid, sentence.offset, sentence.text, e)
        return sentence
