import bioc
import pytest
from StanfordDependencies import StanfordDependencies

from radtext.models.tree2dep import BioCPtb2DepConverter

@pytest.fixture
def sentence():
    text = 'No pneumothorax.'
    tree = '(S1 (S (S (NP (DT No) (NN pneumothorax))) (. .)))'
    s = bioc.BioCSentence.of_text(text, 0)
    s.infons['parse_tree'] = tree
    return s


def test_convert(sentence):
    converter = BioCPtb2DepConverter()
    converter.process_sentence(sentence)

    assert len(sentence.annotations) == 3, len(sentence.annotations)
    assert len(sentence.relations) == 2
    assert sentence.annotations[0].text == 'No'
    assert sentence.annotations[0].infons['tag'] == 'DT'
    assert sentence.annotations[0].infons['lemma'] == 'no'
    assert sentence.annotations[0].total_span.offset == 0

    assert sentence.annotations[1].text == 'pneumothorax'
    assert sentence.annotations[1].infons['tag'] == 'NN'
    assert sentence.annotations[1].infons['lemma'] == 'pneumothorax'
    assert sentence.annotations[1].total_span.offset == 3

    assert sentence.annotations[2].text == '.'
    assert sentence.annotations[2].infons['tag'] == '.'
    assert sentence.annotations[2].infons['lemma'] == '.'
    assert sentence.annotations[2].total_span.offset == 15

    assert sentence.relations[0].infons['dependency'] == 'neg'
    assert sentence.relations[0].nodes[0].refid == 'T0'
    assert sentence.relations[0].nodes[1].refid == 'T1'

    assert sentence.relations[1].infons['dependency'] == 'punct'
    assert sentence.relations[1].nodes[0].refid == 'T2'
    assert sentence.relations[1].nodes[1].refid == 'T1'

    # test empty parse tree
    del sentence.annotations[:]

    del sentence.infons['parse_tree']
    converter.process_sentence(sentence)

    sentence.infons['parse_tree'] = None
    converter.process_sentence(sentence)


def test_convert_subprocess(sentence):
    converter = BioCPtb2DepConverter()
    converter.converter.backend = 'subprocess'
    converter.converter.has_lemma = False
    converter.converter.sd = StanfordDependencies.get_instance(backend='subprocess')
    converter.process_sentence(sentence)
    assert 'lemma' not in sentence.annotations[1].infons