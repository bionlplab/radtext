import logging
import re
from pathlib import Path
from typing import Pattern, List, Match

import bioc
import yaml
from bioc import BioCPassage

from radtext.core import BioCProcessor
from radtext.utils import intersect


class PTakesMatch:
    def __init__(self):
        self.id = None
        self.start = None
        self.end = None
        self.pattern = None
        self.category = None
        self.text = None


class NerRegexPattern:
    def __init__(self, id, category, include_patterns: List[Pattern], exclude_patterns: List[Pattern]):
        self.id = id
        self.category = category
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns


def compile(pattern_str: str) -> Pattern:
    pattern_str = re.sub(' ', r'\\s+', pattern_str)
    return re.compile(pattern_str, re.I | re.M)


def remove_excludes(includes: List[Match], excludes: List[Match]) -> List[Match]:
    results = []
    for mi in includes:
        overlapped = False
        for mj in excludes:
            if intersect((mi.start(), mi.end()), (mj.start(), mj.end())):
                overlapped = True
                break
        if not overlapped:
            results.append(mi)
    return results


def remove_duplicates(matches: List[PTakesMatch]) -> List[PTakesMatch]:
    s = {(m.start, m.end, m.id): m for m in matches}
    return sorted(s.values(), key=lambda m: (m.start, m.end))


def longest_matching(matches: List[PTakesMatch]) -> List[PTakesMatch]:
    results = []
    for i, mi in enumerate(matches):
        # print(mi.start, mi.end, mi.text)
        enclosed = False
        for j, mj in enumerate(matches):
            if i == j:
                continue
            if (mj.start < mi.start and mi.end <= mj.end) or (mj.start <= mi.start and mi.end < mj.end):
                # print(mj.start, mj.end, mj.text)
                # print(mi.start, mi.end, mi.text)
                # print('Remove', mi.start, mi.end, mi.text)
                enclosed = True
                break
        if not enclosed:
            results.append(mi)
    return results


class NerRegExExtractor:
    def __init__(self, phrases_file):
        with open(phrases_file) as fp:
            self.phrases = yaml.load(fp, yaml.FullLoader)

        self.vocab_name = Path(phrases_file).stem
        self.patterns = []
        for i, (category, v) in enumerate(self.phrases.items()):
            if 'include' in v:
                includes = [compile(p) for p in v['include']]
            else:
                raise ValueError('%s: No patterns' % category)

            if 'exclude' in v:
                excludes = [compile(p) for p in v['exclude']]
            else:
                excludes = []

            self.patterns.append(NerRegexPattern(i, category, includes, excludes))
        logging.debug("%s: Loading %s phrases.", phrases_file, len(self.patterns))

    def findall(self, text: str) -> List[PTakesMatch]:
        results = []
        for pattern in self.patterns:
            includes_matches = []
            for p in pattern.include_patterns:
                for m in p.finditer(text):
                    includes_matches.append(m)

            excludes_matches = []
            for p in pattern.exclude_patterns:
                for m in p.finditer(text):
                    excludes_matches.append(m)

            includes_matches = remove_excludes(includes_matches, excludes_matches)
            for m in includes_matches:
                ptakesmatch = PTakesMatch()
                ptakesmatch.pattern = m.re.pattern
                ptakesmatch.match = m
                ptakesmatch.id = pattern.id
                ptakesmatch.category = pattern.category
                ptakesmatch.start = m.start()
                ptakesmatch.end = m.end()
                ptakesmatch.text = m.group()
                results.append(ptakesmatch)

        results = remove_duplicates(results)
        results = longest_matching(results)
        return results


class BioCNerRegex(BioCProcessor):
    def __init__(self, extractor: NerRegExExtractor):
        self.extractor = extractor

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        PUNCTS = "!,.:;? \n\t()/"
        for match in self.extractor.findall(passage.text):
            start = match.start
            end = match.end
            while start > 0:
                if passage.text[start - 1] in PUNCTS:
                    break
                start -= 1
            while end < len(passage.text):
                if passage.text[end] in PUNCTS:
                    break
                end += 1

            annotation = bioc.BioCAnnotation()
            annotation.id = 'a{}'.format(start)
            annotation.infons['ner_pattern_str'] = match.pattern
            annotation.infons["source_concept_id"] = match.id
            annotation.infons["source_concept"] = match.category
            annotation.add_location(bioc.BioCLocation(start + passage.offset, end - start))
            annotation.text = match.text
            passage.add_annotation(annotation)
        return passage
