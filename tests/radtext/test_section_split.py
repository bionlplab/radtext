import bioc
import medspacy

from radtext.models.section_split.section_split_medspacy import BioCSectionSplitterMedSpacy
from radtext.models.section_split.section_split_regex import BioCSectionSplitterRegex

text = """findings: pa and lat cxr at 7:34 p.m.. heart and mediastinum are
stable. lungs are unchanged. air- filled cystic changes. no
pneumothorax. osseous structures unchanged scoliosis
impression: stable chest.
dictating 
"""

def test_section_split_medspacy():
    d = bioc.BioCDocument.of_text(text)

    nlp = medspacy.load(enable=["sectionizer"])
    splitter = BioCSectionSplitterMedSpacy(nlp)
    splitter.process_document(d)
    assert len(d.passages) == 4
    assert len(d.annotations) == 2
    assert d.annotations[0].text == 'findings:'
    assert d.annotations[1].text == 'impression:'


def test_section_split_regex():
    d = bioc.BioCDocument.of_text(text)

    splitter = BioCSectionSplitterRegex()
    splitter.process_document(d)
    assert len(d.passages) == 4
    assert len(d.annotations) == 2
    assert d.annotations[0].text == 'findings:'
    assert d.annotations[1].text == 'impression:'
