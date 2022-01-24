import re
import sys
from typing import List, Match, Pattern

import yaml

from bioc import BioCPassage, BioCAnnotation
from radtext.neg.constants import NEGATION, UNCERTAINTY, NegPattern, NegResult


class NegRegexPattern(NegPattern):
    def compile(self) -> Pattern:
        pattern_str = self.pattern_str.replace(' ', r'\s+')
        pattern_str = pattern_str.replace('XXXXX', r'X{2,}')
        return re.compile(pattern_str, re.I | re.M)


class NegRegexResult(NegResult):
    def __init__(self, category: str, matcher: Match, pattern: NegRegexPattern, *args):
        super(NegRegexResult, self).__init__(category, matcher, pattern, *args)

    def get_span(self):
        start = sys.maxsize
        end = -1
        for m in self.matchers:
            start = min(start, m.start())
            end = max(end, m.end())
        return start, end


def load_regex_yml(file, type: str) -> List[NegRegexPattern]:
    """
    Read a pattern file in the yaml format
    """
    with open(file) as fp:
        objs = yaml.load(fp, yaml.FullLoader)

    patterns = []
    if objs:
        for obj in objs:
            patterns.append(NegRegexPattern(obj['id'], type, obj['pattern']))
    return patterns


class NegRegex:
    def __init__(self, negation_file, uncertainty_pre_neg_file, uncertainty_post_neg_file,
                 double_neg_file):
        self.negation_patterns = load_regex_yml(negation_file, NEGATION)
        self.uncertainty_pre_neg_patterns = load_regex_yml(uncertainty_pre_neg_file, UNCERTAINTY)
        self.uncertainty_post_neg_patterns = load_regex_yml(uncertainty_post_neg_file, UNCERTAINTY)
        self.double_negation_patterns = load_regex_yml(double_neg_file, UNCERTAINTY)
        # private
        self._text = None
        self._passage = None

    def setup(self, passage: BioCPassage, ann: BioCAnnotation):
        ann_span = ann.total_span
        start = ann_span.offset - passage.offset
        end = ann_span.end - passage.offset
        self._passage = passage
        self._text = get_text(passage.text, start, end)

    def match_neg(self):
        for p in self.negation_patterns:
            m = p.pattern_obj.search(self._text)
            if m:
                if 'k0' in p.pattern_obj.groupindex:
                    k0_end = m.end('k0')
                    for p2 in self.double_negation_patterns:
                        text2 = get_text(self._passage.text, m.start('k0'), k0_end)
                        for m2 in p2.pattern_obj.finditer(text2, 0, k0_end):
                            if m2.end('f') == k0_end:
                                return NegRegexResult(UNCERTAINTY, m, p, m2, p2)
                return NegRegexResult(NEGATION, m, p)
        return None

    def match_uncertainty_pre_neg(self):
        for p in self.uncertainty_pre_neg_patterns:
            m = p.pattern_obj.search(self._text)
            if m:
                return NegRegexResult(UNCERTAINTY, m, p)
        return None

    def match_uncertainty_post_neg(self):
        for p in self.uncertainty_post_neg_patterns:
            m = p.pattern_obj.search(self._text)
            if m:
                return NegRegexResult(UNCERTAINTY, m, p)
        return None


def get_text(text: str, start: int, end: int) -> str:
    """
    Returns text with the annotation replaced by XXXXX
    """
    text = text[:start] + 'X' * (end - start) + text[end:]
    text = re.sub(r'\n', ' ', text)
    # text = re.sub(r'\s+', ' ', text)
    return text
