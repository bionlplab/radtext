import logging
import re
from typing import List, Pattern

import tqdm
from bioc import BioCSentence, BioCPassage, BioCDocument, BioCLocation, BioCAnnotation, BioCCollection

from radtext.core import BioCProcessor
from radtext.utils import is_passage_empty, strip_passage

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


def combine_patterns(patterns: List[str]) -> Pattern:
    logger = logging.getLogger(__name__)
    p = '|'.join(patterns)
    logger.debug('Section patterns: %s', p)
    return re.compile(p, re.IGNORECASE | re.MULTILINE)


def _default_patterns():
    return combine_patterns(SECTION_TITLES)


class BioCSectionSplitterRegex(BioCProcessor):
    def __init__(self, regex_pattern: Pattern=None):
        super(BioCSectionSplitterRegex, self).__init__('secsplit:regex')
        if regex_pattern is None:
            self.pattern = _default_patterns()
        else:
            self.pattern = regex_pattern

    def process_collection(self, collection: BioCCollection) -> BioCCollection:
        new_docs = []
        for doc in tqdm.tqdm(collection.documents, desc='Split Section'):
            new_doc = self.process_document(doc)
            new_docs.append(new_doc)
        collection.documents = new_docs
        return collection

    def process_document(self, doc: BioCDocument) -> BioCDocument:
        """
        Split one report into sections. Section splitting is a deterministic
        consequence of section titles.
        """

        # text = doc.passages[0].text
        # offset = doc.passages[0].offset

        def create_passage(text, offset, start, end, title=None):
            passage = BioCPassage()
            passage.infons['nlp_system'] = self.nlp_system
            passage.infons['nlp_date_time'] = self.nlp_date_time
            passage.offset = start + offset
            passage.text = text[start:end]
            if title is not None:
                passage.infons['section_concept'] = title[:-1].strip() if title[-1] == ':' else title.strip()
                passage.infons['type'] = 'title_1'
            strip_passage(passage)
            return passage

        passages = list(doc.passages)
        del doc.passages[:]
        anns = []
        for i, passage in enumerate(passages):
            text = passage.text
            offset = passage.offset
            local_start = 0
            for matcher in self.pattern.finditer(text):
                logging.debug('Match: %s', matcher.group())
                # add last
                local_end = matcher.start()
                if local_end != local_start:
                    passage = create_passage(text, offset, local_start, local_end)
                    if not is_passage_empty(passage):
                        doc.add_passage(passage)

                local_start = local_end

                # add title
                local_end = matcher.end()
                passage = create_passage(text, offset, local_start, local_end, text[local_start:local_end])
                if not is_passage_empty(passage):
                    doc.add_passage(passage)

                    ann = BioCAnnotation()
                    ann.id = 'S{}'.format(i)
                    ann.text = passage.text
                    ann.infons['section_concept'] = passage.infons['section_concept']
                    ann.infons['type'] = passage.infons['type']
                    ann.infons['nlp_system'] = self.nlp_system
                    ann.infons['nlp_date_time'] = self.nlp_date_time
                    ann.add_location(BioCLocation(offset + local_start, local_end - local_start))
                    anns.append(ann)

                local_start = local_end

            # add last piece
            local_end = len(text)
            if local_start < local_end:
                passage = create_passage(text, offset, local_start, local_end)
                if not is_passage_empty(passage):
                    doc.add_passage(passage)
            doc.annotations += anns
        return doc

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        raise NotImplementedError

