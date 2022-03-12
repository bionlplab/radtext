import re
from typing import List

import yaml

from bioc import BioCPassage, BioCAnnotation
from radtext.models.constants import UNCERTAINTY, NEGATION


class NegRegexPattern:
    def __init__(self, id, pattern_str: str, pattern_obj):
        self.id = id
        self.pattern_str = pattern_str # type: str
        self.pattern_obj = pattern_obj

    @staticmethod
    def compile(id, pattern_str: str):
        pattern_str = pattern_str.replace(' ', r'\s+').replace('XXXXX', r'X{2,}')
        pattern_obj = re.compile(pattern_str, re.I | re.M)
        return NegRegexPattern(id, pattern_str, pattern_obj)

    def __str__(self):
        return '[id=%s,pattern=%s]' % (self.id, self.pattern_str)


def load_regex_yml(file) -> List[NegRegexPattern]:
    """
    Read a pattern file in the yaml format
    """
    with open(file) as fp:
        objs = yaml.load(fp, yaml.FullLoader)

    patterns = []
    if objs:
        for obj in objs:
            patterns.append(NegRegexPattern.compile(obj['id'], obj['pattern']))
    return patterns


def get_text(text: str, start: int, end: int) -> str:
    """
    Returns text with the annotation replaced by XXXXX
    """
    text = text[:start] + 'X' * (end - start) + text[end:]
    text = re.sub(r'\n', ' ', text)
    # text = re.sub(r'\s+', ' ', text)
    return text


class NegRegexPatterns:
    def __init__(self):
        self.negation_patterns = []
        self.uncertainty_pre_neg_patterns = []
        self.uncertainty_post_neg_patterns = []
        self.double_negation_patterns = []

    def load_yml(self,
                 negation_file,
                 uncertainty_pre_neg_file,
                 uncertainty_post_neg_file,
                 double_neg_file):
        self.negation_patterns = load_regex_yml(negation_file)
        self.uncertainty_pre_neg_patterns = load_regex_yml(uncertainty_pre_neg_file)
        self.uncertainty_post_neg_patterns = load_regex_yml(uncertainty_post_neg_file)
        self.double_negation_patterns = load_regex_yml(double_neg_file)

    def load_yml2(self, pattern_file):
        with open(pattern_file) as fp:
            objs = yaml.load(fp, yaml.FullLoader)
        for obj in objs['negation']:
            self.negation_patterns.append(NegRegexPattern.compile(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_pre']:
            self.uncertainty_pre_neg_patterns.append(NegRegexPattern.compile(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_post']:
            self.uncertainty_post_neg_patterns.append(NegRegexPattern.compile(obj['id'], obj['pattern']))
        for obj in objs['double_negation']:
            self.double_negation_patterns.append(NegRegexPattern.compile(obj['id'], obj['pattern']))

    def assert_(self, passage: BioCPassage, ann: BioCAnnotation):
        return NegRegexAssertion(self, passage, ann)


class NegRegexAssertion:
    def __init__(self, patterns: 'NegRegexPatterns', passage: BioCPassage, ann: BioCAnnotation):
        start = ann.total_span.offset - passage.offset
        end = ann.total_span.end - passage.offset
        self.passage = passage  # type: BioCPassage
        self.text = get_text(passage.text, start, end)  # type: str
        self.ann = ann  # type: BioCAnnotation
        self.patterns = patterns

    def assert_neg(self) -> bool:
        for p in self.patterns.negation_patterns:
            m = p.pattern_obj.search(self.text)
            if m:
                self.ann.infons[NEGATION] = True
                self.ann.infons['regex_neg_pattern_id'] = p.id
                self.ann.infons['regex_neg_pattern_str'] = p.pattern_str
                return True
        return False

    def assert_double_neg(self) -> bool:
        for p in self.patterns.double_negation_patterns:
            m = p.pattern_obj.search(self.text)
            if m:
                self.ann.infons[UNCERTAINTY] = True
                self.ann.infons['regex_double_neg_pattern_id'] = p.id
                self.ann.infons['regex_double_neg_pattern_str'] = p.pattern_str
                return True
        return False

    def assert_uncertainty_pre_neg(self) -> bool:
        for p in self.patterns.uncertainty_pre_neg_patterns:
            m = p.pattern_obj.search(self.text)
            if m:
                self.ann.infons[UNCERTAINTY] = True
                self.ann.infons['regex_uncertainty_pre_neg_pattern_id'] = p.id
                self.ann.infons['regex_uncertainty_pre_neg_pattern_str'] = p.pattern_str
                return True
        return False

    def assert_uncertainty_post_neg(self) -> bool:
        for p in self.patterns.uncertainty_post_neg_patterns:
            m = p.pattern_obj.search(self.text)
            if m:
                self.ann.infons[UNCERTAINTY] = True
                self.ann.infons['regex_uncertainty_post_neg_pattern_id'] = p.id
                self.ann.infons['regex_uncertainty_post_neg_pattern_str'] = p.pattern_str
                return True
        return False