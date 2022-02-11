"""
Usage:
    ner spacy [options] --radlex FILE -i FILE -o FILE
    ner regex [options] --phrases FILE -i FILE -o FILE

Options:
    --overwrite
    --radlex FILE
    -o FILE
    -i FILE
    --phrases FILE
"""
import logging
import re
from pathlib import Path
from typing import Iterable, Tuple, Pattern
import bioc
import docopt
import spacy
import tqdm
import yaml
from spacy.matcher import PhraseMatcher

from radtext.cmd.cmd_utils import process_options
from radtext.models.ner.ner_regex import NerRegExExtractor, BioCNerRegex, NerRegexPattern
from radtext.models.ner.ner_spacy import NerSpacyExtractor, BioCNerSpacy, NerSpacyPhraseMatchers
import pandas as pd

# def iterparse_RadLex4(pathname) -> Iterable[Tuple[str, str, str]]:
#     df = pd.read_excel(pathname, dtype=str)
#     for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
#         if not pd.isna(row['Comment']) and \
#                 (row['Comment'].lower().startswith('duplicate') or row['Comment'].lower() == 'not needed'):
#             continue
#
#         label = row['Preferred Label']
#         if label is None or label == '':
#             continue
#
#         id = row['Class ID']
#         id = get_class_id(id)
#         yield id, label, label
#         synonyms = row['Synonyms']
#         if isinstance(synonyms, str):
#             for t in synonyms.split('|'):
#                 yield id, label, t.strip()


def load_RadLex4(pathname, nlp, min_term_size: int=1, max_term_size: int=9, min_char_size=3, max_char_size=100):
    def get_class_id(url: str) -> str:
        """http://www.radlex.org/RID/#RID43314"""
        if len(url) == 0:
            return 'ROOT'
        elif '/#' in url:
            return url[url.rfind('/') + 2:]
        elif '/' in url:
            return url[url.rfind('/') + 1:]
        else:
            return url

    matchers = NerSpacyPhraseMatchers()
    matchers.include_text_matcher = PhraseMatcher(nlp.vocab, attr='ORTH')
    matchers.include_lemma_matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')

    df = pd.read_excel(pathname)
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        if not pd.isna(row['Comment']) \
                and (row['Comment'].lower().startswith('duplicate') or row['Comment'].lower() == 'not needed'):
            continue

        concept = row['Preferred Label']
        if concept is None or type(concept) is not str or concept == '':
            continue

        phrases = [concept]

        concept_id = row['Class ID']
        concept_id = get_class_id(concept_id)
        matchers.id2concept[concept_id] = concept

        synonyms = row['Synonyms']
        if isinstance(synonyms, str):
            phrases += [t.strip() for t in synonyms.split('|')]

        docs = []
        for phrase in phrases:
            if min_char_size <= len(phrase) <= max_char_size:
                try:
                    doc = nlp(phrase.lower())
                except:
                    logging.exception('Cannot parse row: %s' % concept_id)
                else:
                    if min_term_size <= len(doc) <= max_term_size:
                        docs.append(doc)

        matchers.include_text_matcher.add(concept_id, docs)
        matchers.include_lemma_matcher.add(concept_id, docs)

    return matchers


def load_yml(pathname):
    def ner_compile(pattern_str: str) -> Pattern:
        pattern_str = re.sub(' ', r'\\s+', pattern_str)
        return re.compile(pattern_str, re.I | re.M)

    with open(pathname) as fp:
        phrases = yaml.load(fp, yaml.FullLoader)

    patterns = []
    for concept_id, (concept, v) in enumerate(phrases.items()):
        npattern = NerRegexPattern()
        npattern.concept_id = str(concept_id)
        npattern.concept = concept

        if 'include' in v:
            npattern.include_patterns += [ner_compile(p) for p in v['include']]
        else:
            raise ValueError('%s: No patterns' % concept)

        if 'exclude' in v:
            npattern.exclude_patterns += [ner_compile(p) for p in v['exclude']]

        patterns.append(npattern)
    logging.debug("%s: Loading %s phrases.", pathname, len(patterns))
    return patterns


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)

    try:
        if argv['spacy']:
            nlp = spacy.load('en_core_web_sm', exclude=['ner', 'parser', 'tok2vec', 'senter'])
            matchers = load_RadLex4(argv['--radlex'], nlp)
            extractor = NerSpacyExtractor(nlp, matchers)
            processor = BioCNerSpacy(extractor, 'RadLex')
        elif argv['regex']:
            patterns = load_yml(argv['--phrases'])
            extractor = NerRegExExtractor(patterns)
            processor = BioCNerRegex(extractor, name=Path(argv['--phrases']).stem)
    except KeyError as e:
        raise e

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        for passage in tqdm.tqdm(doc.passages, leave=False):
            processor.process_passage(passage, doc.id)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
