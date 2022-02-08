import sys

import bioc
import pytest

from radtext.models.bllipparser import BllipParser, BioCParserBllip


def test_parse():
    text = 'No pneumothorax.'
    tree = '(S1 (S (S (NP (DT No) (NN pneumothorax))) (. .)))'

    parser = BllipParser()
    t = parser.parse(text)
    assert str(t) == tree, str(t)

    with pytest.raises(ValueError):
        parser.parse('')

    with pytest.raises(ValueError):
        parser.parse('\n')

    if sys.version_info[0] == 2:
        with pytest.raises(ValueError):
            parser.parse(u'\xe6')
    else:
        t = parser.parse(u'\xe6')
        assert str(t) == u'(S1 (S (NP (NN \xe6))))'


def test_parse_doc():
    text = 'No pneumothorax.'
    tree = '(S1 (S (S (NP (DT No) (NN pneumothorax))) (. .)))'
    sentence = bioc.BioCSentence.of_text(text)

    parser = BioCParserBllip()
    s = parser.process_sentence(sentence, '')
    assert s.infons['parse tree'] == tree

    # test empty sentence
    sentence = bioc.BioCSentence.of_text('')
    s = parser.process_sentence(sentence, '')
    assert s.infons['parse tree'] is None
