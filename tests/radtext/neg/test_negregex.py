from typing import Tuple

import bioc

from radtext.models.neg import NegRegex
from tests import Resource_Dir

# negation = Resource_Dir / 'patterns/regex_negation.yml'
# uncertainty_pre_neg = Resource_Dir / 'patterns/regex_uncertainty_pre_negation.yml'
# uncertainty_post_neg = Resource_Dir / 'patterns/regex_uncertainty_post_negation.yml'
# double_neg = Resource_Dir / 'patterns/regex_double_negation.yml'
regex_patterns = Resource_Dir / 'patterns/regex_patterns.yml'

negregex = NegRegex()
negregex.load_yml2(regex_patterns)


def _get(text, concept_start, concept_end) -> Tuple[bioc.BioCPassage, bioc.BioCAnnotation]:
    passage = bioc.BioCPassage.of_text(text, 0)
    ann = bioc.BioCAnnotation()
    ann.id = 0
    ann.text = text[concept_start:concept_end]
    ann.add_location(bioc.BioCLocation(concept_start, concept_end))
    return passage, ann


def test_uncertainty_pre_neg():
    passage, ann = _get('No evidence to rule out effusion.', 24, 32)
    negregex.setup(passage, ann)
    m = negregex.match_uncertainty_pre_neg()
    assert m
    assert ann.infons['uncertainty']
    assert 'regex_uncertainty_pre_neg_pattern_id' in ann.infons


def test_uncertainty_post_neg():
    passage, ann = _get('Effusion is possible.', 0, 8)
    negregex.setup(passage, ann)
    m = negregex.match_uncertainty_post_neg()
    assert m
    assert ann.infons['uncertainty']
    assert 'regex_uncertainty_post_neg_pattern_id' in ann.infons


def test_neg():
    passage, ann = _get('No effusion is seen', 3, 11)
    negregex.setup(passage, ann)
    m = negregex.match_neg()
    assert m
    assert ann.infons['negation']
    assert 'regex_neg_pattern_id' in ann.infons


def test_double_neg():
    passage, ann = _get('Cannot exclude effusion', 15, 23)
    negregex.setup(passage, ann)
    m = negregex.match_double_neg()
    assert m
    assert ann.infons['uncertainty']
    assert 'regex_double_neg_pattern_id' in ann.infons


if __name__ == '__main__':
    test_neg()
    test_double_neg()
