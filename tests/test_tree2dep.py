import bioc
from StanfordDependencies import StanfordDependencies

from radtext.models.tree2dep import BioCPtb2DepConverter


def test_convert():
    text = 'No pneumothorax.'
    tree = '(S1 (S (S (NP (DT No) (NN pneumothorax))) (. .)))'
    s = bioc.BioCSentence.of_text(text, 0)
    s.infons['parse_tree'] = tree

    converter = BioCPtb2DepConverter()
    converter.process_sentence(s)

    assert len(s.annotations) == 3, len(s.annotations)
    assert len(s.relations) == 2
    assert s.annotations[0].text == 'No'
    assert s.annotations[0].infons['tag'] == 'DT'
    assert s.annotations[0].infons['lemma'] == 'no'
    assert s.annotations[0].total_span.offset == 0

    assert s.annotations[1].text == 'pneumothorax'
    assert s.annotations[1].infons['tag'] == 'NN'
    assert s.annotations[1].infons['lemma'] == 'pneumothorax'
    assert s.annotations[1].total_span.offset == 3

    assert s.annotations[2].text == '.'
    assert s.annotations[2].infons['tag'] == '.'
    assert s.annotations[2].infons['lemma'] == '.'
    assert s.annotations[2].total_span.offset == 15

    assert s.relations[0].infons['dependency'] == 'neg'
    assert s.relations[0].nodes[0].refid == 'T0'
    assert s.relations[0].nodes[1].refid == 'T1'

    assert s.relations[1].infons['dependency'] == 'punct'
    assert s.relations[1].nodes[0].refid == 'T2'
    assert s.relations[1].nodes[1].refid == 'T1'

    # test empty parse tree
    del s.annotations[:]

    del s.infons['parse_tree']
    converter.process_sentence(s)

    s.infons['parse_tree'] = None
    converter.process_sentence(s)


def test_convert_subprocess():
    converter = BioCPtb2DepConverter()
    converter.converter.backend = 'subprocess'
    converter.converter.has_lemma = False
    converter.converter.sd = StanfordDependencies.get_instance(backend='subprocess')
    text = 'No pneumothorax.'
    tree = '(S1 (S (S (NP (DT No) (NN pneumothorax))) (. .)))'
    s = bioc.BioCSentence.of_text(text, 0)
    s.infons['parse_tree'] = tree
    converter.process_sentence(s)
    assert 'lemma' not in s.annotations[1].infons