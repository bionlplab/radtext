import logging
import re
from datetime import datetime
from typing import List, Pattern

import bioc

from radtext.core import BioCProcessor


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


def is_empty(passage: bioc.BioCPassage) -> bool:
    return len(passage.text) == 0


def strip(passage: bioc.BioCPassage) -> bioc.BioCPassage:
    start = 0
    while start < len(passage.text) and passage.text[start].isspace():
        start += 1

    end = len(passage.text)
    while end > start and passage.text[end - 1].isspace():
        end -= 1

    passage.offset += start
    logging.debug('before: %r' % passage.text)
    passage.text = passage.text[start:end]
    logging.debug('after:  %r' % passage.text)
    return passage


class BioCSectionSplitterRegex(BioCProcessor):
    def __init__(self, regex_pattern: Pattern=None):
        if regex_pattern is None:
            self.pattern = _default_patterns()
        else:
            self.pattern = regex_pattern

    def process_document(self, doc: bioc.BioCDocument) -> bioc.BioCDocument:
        """
        Split one report into sections. Section splitting is a deterministic
        consequence of section titles.
        """

        # text = doc.passages[0].text
        # offset = doc.passages[0].offset

        def create_passage(text, offset, start, end, title=None):
            passage = bioc.BioCPassage()
            passage.offset = start + offset
            passage.text = text[start:end]
            if title is not None:
                passage.infons['section_concept'] = title[:-1].strip() if title[-1] == ':' else title.strip()
                passage.infons['type'] = 'title_1'
            strip(passage)
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
                    if not is_empty(passage):
                        doc.add_passage(passage)

                local_start = local_end

                # add title
                local_end = matcher.end()
                passage = create_passage(text, offset, local_start, local_end, text[local_start:local_end])
                if not is_empty(passage):
                    doc.add_passage(passage)

                    ann = bioc.BioCAnnotation()
                    ann.id = 'S{}'.format(i)
                    ann.text = passage.text
                    ann.infons['section_concept'] = passage.infons['section_concept']
                    ann.infons['type'] = passage.infons['type']
                    ann.infons['nlp_system'] = 'regex'
                    ann.infons['nlp_date_time'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    ann.add_location(bioc.BioCLocation(offset + local_start, local_end - local_start))
                    anns.append(ann)

                local_start = local_end

            # add last piece
            local_end = len(text)
            if local_start < local_end:
                passage = create_passage(text, offset, local_start, local_end)
                if not is_empty(passage):
                    doc.add_passage(passage)
            doc.annotations += anns
        return doc


