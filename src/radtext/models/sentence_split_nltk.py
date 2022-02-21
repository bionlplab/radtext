import logging
from typing import List, Generator, Tuple

import nltk
from bioc import BioCPassage, BioCSentence

from radtext.core import BioCProcessor


def split_newline(text: str, sep='\n') -> Generator[Tuple[str, int], None, None]:
    """
    Split the text based on sep (default: \n).
    """
    lines = text.split(sep)
    offset = 0
    for line in lines:
        offset = text.index(line, offset)
        yield line, offset
        offset += len(line)


def no_split_newline(text):
    yield text, 0


def split(text: str, newline: bool = False) -> Generator[Tuple[str, int], None, None]:
    """
    Split the text using nltk sent_tokenize.

    Yields:
         (sentence, offset)
    """
    if len(text) == 0:
        return

    if newline:
        line_splitter = split_newline
    else:
        line_splitter = no_split_newline

    for line, line_offset in line_splitter(text):
        sent_list = nltk.sent_tokenize(line)  # type: List[str]
        offset = 0
        for sent in sent_list:
            offset = line.find(sent, offset)
            if offset == -1:
                raise IndexError('Cannot find %s in %s' % (sent, text))
            yield sent, offset + line_offset
            offset += len(sent)


class BioCSSplitterNLTK(BioCProcessor):
    """NLTK sentence splitter"""

    def __init__(self, newline: bool = False):
        """
        Args:
            newline: split the newline.
        """
        super(BioCSSplitterNLTK, self).__init__('ssplit:nltk')
        self.newline = newline

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        """
        Split text into sentences with offsets.
        """
        try:
            sentences = list(split(passage.text, self.newline))
        except IndexError as e:
            logging.error('%s:%s: %s', docid, passage.offset, str(e))
            return passage

        del passage.sentences[:]
        for text, offset in sentences:
            sentence = BioCSentence()
            sentence.infons['nlp_system'] = self.nlp_system
            sentence.infons['nlp_date_time'] = self.nlp_date_time
            sentence.offset = offset + passage.offset
            sentence.text = text
            passage.add_sentence(sentence)
        return passage

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        raise NotImplementedError