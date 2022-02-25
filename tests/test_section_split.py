import bioc
import medspacy
import pytest

from radtext.models.section_split.section_split_medspacy import BioCSectionSplitterMedSpacy
from radtext.models.section_split.section_split_regex import BioCSectionSplitterRegex, combine_patterns


@pytest.fixture
def document():
    text = """findings: pa and lat cxr at 7:34 p.m.. heart and mediastinum are
    stable. lungs are unchanged. air- filled cystic changes. no
    pneumothorax. osseous structures unchanged scoliosis
    impression: stable chest.
    dictating 
    """
    return bioc.BioCDocument.of_text(text)

@pytest.fixture
def section_titles(resource_dir):
    with open(resource_dir / 'section_titles.txt') as fp:
        section_titles = [line.strip() for line in fp]
    return section_titles


def test_section_split_medspacy(document):
    nlp = medspacy.load(enable=["sectionizer"])
    splitter = BioCSectionSplitterMedSpacy(nlp)
    splitter.process_document(document)
    assert len(document.passages) == 4
    assert len(document.annotations) == 2
    assert document.annotations[0].text == 'findings:'
    assert document.annotations[1].text == 'impression:'


def test_section_split_regex(document, section_titles):
    pattern = combine_patterns(section_titles)
    splitter = BioCSectionSplitterRegex(pattern)
    splitter.process_document(document)
    assert len(document.passages) == 4
    assert len(document.annotations) == 2
    assert document.annotations[0].text == 'findings:'
    assert document.annotations[1].text == 'impression:'
