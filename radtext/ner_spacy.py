import collections
import logging
from itertools import permutations
from typing import List, Set, Iterable, Tuple, Iterator, Any, Match
import nltk
nltk.download('stopwords')
import tqdm
from bioc import BioCAnnotation, BioCLocation, BioCPassage
from intervaltree import IntervalTree
from nltk.corpus import stopwords
from spacy.matcher import PhraseMatcher
from spacy.tokenizer import Tokenizer
from spacy.tokens.doc import Doc
from typing.re import Pattern

from radtext.core import BioCProcessor
from radtext.ner_regex import PTakesMatch, longest_matching, remove_duplicates

STOP_WORDS = set(stopwords.words('english'))


class PSpacyDoc:
    def __init__(self, doc_raw, doc_lemma):
        # assert len(doc_raw) == len(doc_lemma), doc_raw
        self.doc_raw = doc_raw
        self.doc_lemma = doc_lemma

        raws = [token for token in self.doc_raw if not token.is_space]
        lemmas = [token for token in self.doc_lemma if not token.is_space]
        assert len(raws) == len(lemmas), self.doc_raw
        # self.lemma2raw = {}
        # for token, lemma in zip(raws, lemmas):
        #     self.lemma2raw[lemma.i] = token.i
        # self.lemma2raw[lemma.idx + len(lemma.text)] = token.idx + len(token.text)

    def __str__(self):
        return self.doc_raw.text

    def __repr__(self):
        s = 'Raw:   {}\nLemma: {}\n'.format(self.doc_raw.text, self.doc_lemma.text)
        for a in self.doc_raw:
            s += '{} {}'.format(a.idx, a) + '\n'
        # s += '\n' + str(self.lemma2raw)
        return s

    def finditer_matcher(self, matcher: PhraseMatcher, on_lemma=True) -> Iterator[Tuple[Any, int, int]]:
        if on_lemma:
            doc = self.doc_lemma
        else:
            doc = self.doc_raw
        yield from matcher(doc)

    def finditer_regex(self, pattern: Pattern, group=0, on_lemma=True, **kwargs) -> Iterator[Tuple[Match, int, int]]:
        """
        Skip if the character indices don't map to a valid span.
        """
        logging.debug(repr(self))
        if on_lemma:
            doc = self.doc_lemma
        else:
            doc = self.doc_raw

        for m in pattern.finditer(doc, **kwargs):
            start, end = m.span(group)
            span = doc.char_span(start, end)
            if span:
                yield m, span.start, span.end

    def search_regex(self, pattern: Pattern, group=0, on_lemma=True, **kwargs) -> Tuple[Any, int, int]:
        logging.debug(repr(self))
        if on_lemma:
            doc = self.doc_lemma
        else:
            doc = self.doc_raw
        m = pattern.search(doc.text, **kwargs)
        if m:
            start, end = m.span(group)
            logging.debug('Find char [%s: %s]', start, end)
            span = doc.char_span(start, end)
            if span:
                logging.debug('Find token [%s: %s]', span.start, span.end)
                return m, span.start, span.end
        return None, -1, -1


def filter_number(anns: Iterable[BioCAnnotation]):
    new_anns = []
    for a in anns:
        try:
            float(a.text)
        except:
            new_anns.append(a)
    return new_anns


def filter_stop_words(anns: Iterable[BioCAnnotation], stop_words: Set):
    return [a for a in anns if a.text not in stop_words]


class NerSpacyExtractor:
    def __init__(self, nlp, data: Iterable[Tuple[str, str, str]], min_term_size=2, filter_integers=True):
        self.nlp = nlp
        self.id2pref = {}
        self.min_term_size = min_term_size
        self.filter_integers = filter_integers
        self.text2ids = collections.defaultdict(set)

        # create PhraseMatcher
        tokenizer = Tokenizer(nlp.vocab)
        matcher = PhraseMatcher(nlp.vocab, max_length=10)
        for id, pref_label, text in tqdm.tqdm(data):
            if id not in self.id2pref:
                self.id2pref[id] = pref_label
            self.text2ids[text].add(id)

            if 0 <= len(text) < 3:
                continue
            try:
                phrase = tokenizer(text.lower())
            except:
                logging.exception('Cannot parse row: %s' % id)
            else:
                if 9 >= len(phrase) >= 1:
                    matcher.add(id, None, phrase)
        self.matcher = matcher

    def findall(self, text: str) -> List[PTakesMatch]:
        doc_raw = self.nlp(text)
        words = [token.lemma_.lower() for token in doc_raw]
        doc_lemma = Doc(self.nlp.vocab, words=words)
        doc = PSpacyDoc(doc_raw, doc_lemma)

        results = []
        for match_id, start, end in doc.finditer_matcher(self.matcher):
            # print(start, end, doc.doc_lemma[start:end].text)
            m = PTakesMatch()
            m.id = self.nlp.vocab.strings[match_id]
            m.category = self.id2pref[m.id]
            m.start = doc.doc_raw[start].idx
            m.text = doc.doc_raw[start:end].text
            m.end = m.start + len(m.text)
            results.append(m)

        for match_id, start, end in doc.finditer_matcher(self.matcher, on_lemma=False):
            # print(start, end, doc.doc_raw[start:end].text)
            m = PTakesMatch()
            m.id = self.nlp.vocab.strings[match_id]
            m.category = self.id2pref[m.id]
            m.start = doc.doc_raw[start].idx
            m.text = doc.doc_raw[start:end].text
            m.end = m.start + len(m.text)
            results.append(m)

        results = remove_duplicates(results)
        results = longest_matching(results)
        return results


class BioCNerSpacy(BioCProcessor):
    def __init__(self, extractor: NerSpacyExtractor, filter_integers=True):
        self.extractor = extractor
        self.filter_integers = filter_integers

    def _find_other_ids(self, ann):
        this_id = ann.infons['source_concept_id']
        if ann.text == ann.infons['source_concept']:
            return
        for i, id in enumerate(self.extractor.text2ids[ann.text], 1):
            if id != this_id:
                ann.infons['source_concept_id'] += ';{}'.format(id)
                ann.infons['source_concept'] += ';{}'.format(self.extractor.id2pref[id])
                # ann.infons[f'concept_id_{i}'] = id
                # ann.infons[f'preferred_name_{i}'] = self.extractor.id2pref[id]

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        ann_map = collections.OrderedDict()
        for match in self.extractor.findall(passage.text):
            start = match.start
            end = match.end

            ann = BioCAnnotation()
            ann.id = 'a{}'.format(match.start)
            ann.infons['source_concept_id'] = match.id
            ann.infons['source_concept'] = match.category
            ann.add_location(BioCLocation(start + passage.offset, end - start))
            ann.text = match.text

            # find other ids
            self._find_other_ids(ann)

            k = ann.total_span
            if k not in ann_map:
                ann_map[k] = ann

        anns = ann_map.values()
        if self.filter_integers:
            anns = filter_number(anns)
        # anns = filter_min_size(anns, self.min_term_size)
        anns = filter_stop_words(anns, STOP_WORDS)

        for ann in anns:
            passage.add_annotation(ann)
        return passage
