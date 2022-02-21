from typing import Pattern, List, Generator, Iterable

import bioc
from bioc import BioCPassage, BioCSentence

from radtext.core import BioCProcessor
from radtext.models.ner.utils import NERMatch, remove_duplicates, longest_matching, remove_excludes


class NerRegexPattern:
    def __init__(self):
        self.concept_id = None  # type: str | None
        self.concept = None  # type: str | None
        self.include_patterns = []  # type: List[Pattern]
        self.exclude_patterns = []  # type: List[Pattern]

    def finditer_include(self, text: str) -> Generator[NERMatch, None, None]:
        yield from self._finditer(text, self.include_patterns)

    def finditer_exclude(self, text: str) -> Generator[NERMatch, None, None]:
        yield from self._finditer(text, self.exclude_patterns)

    def _finditer(self, text: str, patterns: List[Pattern]) -> Generator[NERMatch, None, None]:
        for p in patterns:
            for m in p.finditer(text):
                nermatch = NERMatch()
                nermatch.pattern = m.re.pattern
                nermatch.match = m
                nermatch.concept_id = self.concept_id
                nermatch.concept = self.concept
                nermatch.start = m.start()
                nermatch.end = m.end()
                nermatch.text = m.group()
                yield nermatch


class NerRegExExtractor:
    def __init__(self, patterns: Iterable[NerRegexPattern]):
        self.patterns = patterns

    def findall(self, text: str) -> List[NERMatch]:
        results = []
        for pattern in self.patterns:
            includes_matches = [m for m in pattern.finditer_include(text)]
            excludes_matches = [m for m in pattern.finditer_exclude(text)]
            includes_matches = remove_excludes(includes_matches, excludes_matches)
            results += includes_matches
        results = remove_duplicates(results)
        results = longest_matching(results)
        return results


class BioCNerRegex(BioCProcessor):
    punctuation = "!,.:;? \n\t()/"

    def __init__(self, extractor: NerRegExExtractor, name: str):
        super(BioCNerRegex, self).__init__('ner:regex')
        self.extractor = extractor
        self.model = name

    def ner(self, text, offset):
        anns = []
        for match in self.extractor.findall(text):
            start = match.start
            end = match.end
            while start > 0:
                if text[start - 1] in self.punctuation:
                    break
                start -= 1
            while end < len(text):
                if text[end] in self.punctuation:
                    break
                end += 1

            ann = bioc.BioCAnnotation()
            ann.id = 'a{}'.format(start)
            ann.infons['ner_pattern_str'] = match.pattern
            ann.infons['note_nlp_concept_id'] = match.concept_id
            ann.infons['note_nlp_concept'] = match.concept
            ann.infons['nlp_system'] = self.nlp_system
            ann.infons['nlp_date_time'] = self.nlp_date_time
            ann.add_location(bioc.BioCLocation(start + offset, end - start))
            ann.text = match.text
            anns.append(ann)
        return anns

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        anns = self.ner(passage.text, passage.offset)
        passage.annotations += anns
        return passage

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        anns = self.ner(sentence.text, sentence.offset)
        sentence.annotations += anns
        return sentence


