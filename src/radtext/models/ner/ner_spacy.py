import collections
from typing import List, Generator

from bioc import BioCAnnotation, BioCLocation, BioCPassage, BioCSentence
from spacy.matcher import PhraseMatcher
from spacy.tokens.doc import Doc

from radtext.core import BioCProcessor
from radtext.models.ner.utils import longest_matching, remove_duplicates, remove_excludes, filter_number, \
    filter_stop_words, STOP_WORDS
from radtext.models.ner.utils import NERMatch


class NerSpacyPhraseMatchers:
    def __init__(self):
        self.include_text_matcher = None # type: PhraseMatcher | None
        self.include_lemma_matcher = None # type: PhraseMatcher | None
        self.exclude_text_matcher = None  # type: PhraseMatcher | None
        self.exclude_lemma_matcher = None  # type: PhraseMatcher | None
        self.id2concept = {}

    def finditer_include(self, doc: Doc) -> Generator[NERMatch, None, None]:
        yield from self._finditer(doc, self.include_text_matcher)
        yield from self._finditer(doc, self.include_lemma_matcher)

    def finditer_exclude(self, doc: Doc) -> Generator[NERMatch, None, None]:
        if self.exclude_text_matcher is not None:
            yield from self._finditer(doc, self.exclude_text_matcher)
        if self.exclude_lemma_matcher is not None:
            yield from self._finditer(doc, self.exclude_lemma_matcher)

    def _finditer(self, doc: Doc, matcher: PhraseMatcher) -> Generator[NERMatch, None, None]:
        for match_id, start, end in matcher(doc):
            nermatch = NERMatch()
            nermatch.concept_id = doc.vocab.strings[match_id]
            nermatch.concept = self.id2concept[nermatch.concept_id]
            nermatch.start = doc[start].idx
            nermatch.end = doc[end-1].idx + len(doc[end-1])
            nermatch.text = doc[start:end].text
            # print(nermatch)
            yield nermatch


class NerSpacyExtractor:
    def __init__(self, nlp, phrase_matchers: NerSpacyPhraseMatchers, filter_number: bool=True,
                 filter_stop_words: bool=True):
        self.nlp = nlp
        self.phrase_matchers = phrase_matchers
        self.filter_number = filter_number
        self.filter_stop_words = filter_stop_words

    def findall(self, text: str) -> List[NERMatch]:
        doc = self.nlp(text)
        includes_matches = [m for m in self.phrase_matchers.finditer_include(doc)]
        excludes_matches = [m for m in self.phrase_matchers.finditer_exclude(doc)]
        results = remove_excludes(includes_matches, excludes_matches)
        results = remove_duplicates(results)
        results = longest_matching(results)
        if self.filter_number:
            results = filter_number(results)
        if self.filter_stop_words:
            results = filter_stop_words(results, STOP_WORDS)
        return results


class BioCNerSpacy(BioCProcessor):
    def __init__(self, extractor: NerSpacyExtractor, name: str, filter_integers=True):
        super(BioCNerSpacy, self).__init__('ner:spacy')
        self.extractor = extractor
        self.filter_integers = filter_integers
        self.model = name

    # def _find_other_ids(self, ann):
    #     this_id = ann.infons['source_concept_id']
    #     if ann.text == ann.infons['source_concept']:
    #         return
    #     for i, id in enumerate(self.extractor.text2ids[ann.text], 1):
    #         if id != this_id:
    #             ann.infons['note_nlp_concept_id'] += ';{}'.format(id)
    #             ann.infons['note_nlp_concept'] += ';{}'.format(self.extractor.id2pref[id])
    #             # ann.infons[f'concept_id_{i}'] = id
    #             # ann.infons[f'preferred_name_{i}'] = self.extractor.id2pref[id]

    def ner(self, text, offset):
        anns = []
        for match in self.extractor.findall(text):
            start = match.start
            end = match.end

            ann = BioCAnnotation()
            ann.id = 'a{}'.format(match.start)
            ann.infons['note_nlp_concept_id'] = match.concept_id
            ann.infons['note_nlp_concept'] = match.concept
            ann.infons['nlp_system'] = self.nlp_system
            ann.infons['nlp_date_time'] = self.nlp_date_time
            ann.add_location(BioCLocation(start + offset, end - start))
            ann.text = match.text
            anns.append(ann)

            # find other ids
            # self._find_other_ids(ann)

            # k = ann.total_span
            # if k not in ann_map:
            #     ann_map[k] = ann

        return anns

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        anns= self.ner(passage.text, passage.offset)
        passage.annotations += anns
        for sentence in passage.sentences:
            self.process_sentence(sentence, docid)
        return passage

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        anns = self.ner(sentence.text, sentence.offset)
        sentence.annotations += anns
        return sentence

