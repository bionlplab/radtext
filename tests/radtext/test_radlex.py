import spacy
from spacy.matcher import PhraseMatcher

from radtext.models.ner.radlex import RadLex4
from tests import Resource_Dir

phrases_file = Resource_Dir / 'Radlex4.1.xlsx'
radlex = RadLex4(phrases_file)


def test_graph():
    G = radlex.get_graph()
    assert 'RID39050' in G
    item = G.nodes['RID39050']['item']
    assert item.preferred_name == 'symptom'
    print(G.nodes['RID39050']['item'])


def test_spacy_matcher():
    nlp = spacy.load('en_core_web_sm', exclude=['ner', 'parser', 'senter'])
    text_matcher = PhraseMatcher(nlp.vocab, attr='ORTH')
    lemma_matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')

    doc = nlp('symptom')
    text_matcher.add('RID39050', [doc])
    lemma_matcher.add('RID39050', [doc])

    text = """No findings to account for symptoms"""
    doc = nlp(text)

    matches = lemma_matcher(doc)
    assert doc.vocab.strings[matches[0][0]] == 'RID39050'
    assert matches[0][1] == 5
    assert matches[0][2] == 6
    assert doc[matches[0][1]].idx == 27
    assert doc[matches[0][2]-1].idx + len(doc[matches[0][2]-1]) == 35

    matches = text_matcher(doc)
    assert len(matches) == 0


def test_matcher2():
    nlp = spacy.load('en_core_web_sm', exclude=['ner', 'parser', 'senter'])
    matchers = radlex.get_spacy_matchers(nlp)
    text = """No findings to account for symptoms"""
    doc = nlp(text)
    matches = matchers.include_lemma_matcher(doc)
    assert doc.vocab.strings[matches[0][0]] == 'RID39050'
    assert matches[0][1] == 5
    assert matches[0][2] == 6
    assert doc[matches[0][1]].idx == 27
    assert doc[matches[0][2] - 1].idx + len(doc[matches[0][2] - 1]) == 35


if __name__ == '__main__':
    test_matcher2()