import logging
from typing import Tuple, Generator

import yaml
from spacy.matcher import PhraseMatcher

from radtext.models.ner.ner_spacy import NerSpacyPhraseMatchers


class YmlItem:
    def __init__(self):
        self.concept_id = None
        self.preferred_name = None
        self.excludes_synonyms = []
        self.includes_synonyms = []


class YmlVocab:
    def __init__(self, filename):
        self.filename = filename

    def iterrows(self) -> Tuple[int, Generator[YmlItem, None, None]]:
        with open(self.filename) as fp:
            phrases = yaml.load(fp, yaml.FullLoader)

        for i, e in enumerate(phrases):
            item = YmlItem()
            item.concept_id = e['concept_id']
            item.preferred_name = e['preferred_name']
            item.includes_synonyms = e['include']
            if 'exclude' in e:
                item.excludes_synonyms = e['exclude']
            yield i, item

    def get_spacy_matchers(self, nlp, min_term_size: int = 1, max_term_size: int = 9,
                           min_char_size=3, max_char_size=100) -> NerSpacyPhraseMatchers:
        matchers = NerSpacyPhraseMatchers()
        matchers.include_text_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
        matchers.include_lemma_matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')
        matchers.exclude_text_matcher= PhraseMatcher(nlp.vocab, attr='LOWER')
        matchers.exclude_lemma_matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')

        for i, item in self.iterrows():
            matchers.id2concept[item.concept_id] = item.preferred_name

            docs = []
            for phrase in item.includes_synonyms:
                if min_char_size <= len(phrase) <= max_char_size:
                    try:
                        doc = nlp(phrase.lower())
                    except:
                        logging.exception('Cannot parse row: %s' % item.concept_id)
                    else:
                        if min_term_size <= len(doc) <= max_term_size:
                            docs.append(doc)
            matchers.include_text_matcher.add(item.concept_id, docs)
            matchers.include_lemma_matcher.add(item.concept_id, docs)

            docs = []
            for phrase in item.excludes_synonyms:
                if min_char_size <= len(phrase) <= max_char_size:
                    try:
                        doc = nlp(phrase.lower())
                    except:
                        logging.exception('Cannot parse row: %s' % item.concept_id)
                    else:
                        if min_term_size <= len(doc) <= max_term_size:
                            docs.append(doc)
            matchers.exclude_text_matcher.add(item.concept_id, docs)
            matchers.exclude_lemma_matcher.add(item.concept_id, docs)

        return matchers