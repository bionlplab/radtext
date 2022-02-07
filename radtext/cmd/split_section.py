"""
Usage:
    split_section reg [options] -i FILE -o FILE
    split_section medspacy [options] -i FILE -o FILE

Options:
    --section-titles FILE
    -o FILE
    -i FILE
"""
import copy
import logging
import re
from typing import List, Pattern

import bioc
import docopt
import tqdm

from cmd_utils import process_options
from radtext.section_split_regex import BioCSectionSplitterRegex

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


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    if argv['reg']:
        if argv['--section-titles']:
            with open(argv['--section-titles']) as fp:
                section_titles = [line.strip() for line in fp]
        else:
            section_titles = SECTION_TITLES
        pattern = combine_patterns(section_titles)
        sec_splitter = BioCSectionSplitterRegex(regex_pattern=pattern)
    elif argv['medspacy']:
        import medspacy
        from radtext.section_split_medspacy import BioCSectionSplitterMedSpacy
        nlp = medspacy.load(enable=["sectionizer"])
        sec_splitter = BioCSectionSplitterMedSpacy(nlp)
    else:
        raise KeyError

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    new_collection = bioc.BioCCollection()
    new_collection.infons = copy.deepcopy(collection.infons)
    for doc in tqdm.tqdm(collection.documents):
        new_doc = sec_splitter.process_document(doc)
        new_collection.add_document(new_doc)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(new_collection, fp)


if __name__ == '__main__':
    main()
