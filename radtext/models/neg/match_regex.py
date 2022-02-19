import re
from typing import List, Pattern

import yaml

from bioc import BioCPassage, BioCAnnotation
from radtext.models.neg.constants import NEGATION, UNCERTAINTY


class NegRegexPattern:
    def __init__(self, id, pattern_str: str):
        self.id = id
        self.pattern_str = pattern_str
        self.pattern_obj = self.compile()

    def __str__(self):
        return '[id=%s,pattern=%s]' % (self.id, self.pattern_str)

    def compile(self) -> Pattern:
        pattern_str = self.pattern_str.replace(' ', r'\s+')
        pattern_str = pattern_str.replace('XXXXX', r'X{2,}')
        return re.compile(pattern_str, re.I | re.M)


def load_regex_yml(file) -> List[NegRegexPattern]:
    """
    Read a pattern file in the yaml format
    """
    with open(file) as fp:
        objs = yaml.load(fp, yaml.FullLoader)

    patterns = []
    if objs:
        for obj in objs:
            patterns.append(NegRegexPattern(obj['id'], obj['pattern']))
    return patterns


class NegRegex:
    def __init__(self):
        self.negation_patterns = []
        self.uncertainty_pre_neg_patterns = []
        self.uncertainty_post_neg_patterns = []
        self.double_negation_patterns = []
        # private
        self._text = None  # type: str or None
        self._passage = None  # type: BioCPassage or None
        self._ann = None  # type: BioCAnnotation or None

    def load_yml(self,
                 negation_file,
                 uncertainty_pre_neg_file,
                 uncertainty_post_neg_file,
                 double_neg_file):
        self.negation_patterns = load_regex_yml(negation_file)
        self.uncertainty_pre_neg_patterns = load_regex_yml(uncertainty_pre_neg_file)
        self.uncertainty_post_neg_patterns = load_regex_yml(uncertainty_post_neg_file)
        self.double_negation_patterns = load_regex_yml(double_neg_file)
        # private
        self._text = None  # type: str or None
        self._passage = None  # type: BioCPassage or None
        self._ann = None  # type: BioCAnnotation or None

    def load_yml2(self, pattern_file):
        with open(pattern_file) as fp:
            objs = yaml.load(fp, yaml.FullLoader)
        for obj in objs['negation']:
            self.negation_patterns.append(NegRegexPattern(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_pre']:
            self.uncertainty_pre_neg_patterns.append(NegRegexPattern(obj['id'], obj['pattern']))
        for obj in objs['uncertainty_post']:
            self.uncertainty_post_neg_patterns.append(NegRegexPattern(obj['id'], obj['pattern']))
        for obj in objs['double_negation']:
            self.double_negation_patterns.append(NegRegexPattern(obj['id'], obj['pattern']))

    def setup(self, passage: BioCPassage, ann: BioCAnnotation):
        ann_span = ann.total_span
        start = ann_span.offset - passage.offset
        end = ann_span.end - passage.offset
        self._passage = passage
        self._text = get_text(passage.text, start, end)
        self._ann = ann

    def match_neg(self) -> bool:
        for p in self.negation_patterns:
            m = p.pattern_obj.search(self._text)
            if m:
                self._ann.infons[NEGATION] = 'True'
                self._ann.infons['regex_neg_pattern_id'] = p.id
                self._ann.infons['regex_neg_pattern_str'] = p.pattern_str
                return True
        return False

    def match_double_neg(self) -> bool:
        for p in self.double_negation_patterns:
            m = p.pattern_obj.search(self._text)
            if m:
                self._ann.infons[UNCERTAINTY] = 'True'
                self._ann.infons['regex_double_neg_pattern_id'] = p.id
                self._ann.infons['regex_double_neg_pattern_str'] = p.pattern_str
                return True
        return False

    def match_uncertainty_pre_neg(self) -> bool:
        for p in self.uncertainty_pre_neg_patterns:
            m = p.pattern_obj.search(self._text)
            if m:
                self._ann.infons[UNCERTAINTY] = 'True'
                self._ann.infons['regex_uncertainty_pre_neg_pattern_id'] = p.id
                self._ann.infons['regex_uncertainty_pre_neg_pattern_str'] = p.pattern_str
                return True
        return False

    def match_uncertainty_post_neg(self) -> bool:
        for p in self.uncertainty_post_neg_patterns:
            m = p.pattern_obj.search(self._text)
            if m:
                self._ann.infons[UNCERTAINTY] = 'True'
                self._ann.infons['regex_uncertainty_post_neg_pattern_id'] = p.id
                self._ann.infons['regex_uncertainty_post_neg_pattern_str'] = p.pattern_str
                return True
        return False


def get_text(text: str, start: int, end: int) -> str:
    """
    Returns text with the annotation replaced by XXXXX
    """
    text = text[:start] + 'X' * (end - start) + text[end:]
    text = re.sub(r'\n', ' ', text)
    # text = re.sub(r'\s+', ' ', text)
    return text
