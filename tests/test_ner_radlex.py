import bioc
import pytest
import spacy

from radtext.models.ner.ner_spacy import BioCNerSpacy, NerSpacyExtractor
from radtext.models.ner.radlex import RadLex4


@pytest.fixture
def radlex(resource_dir):
    phrases_file = resource_dir / 'Radlex4.1.xlsx'
    return RadLex4(phrases_file)


def test_ner(radlex):
    nlp = spacy.load('en_core_web_sm', exclude=['ner', 'parser', 'senter'])
    matchers = radlex.get_spacy_matchers(nlp)
    extractor = NerSpacyExtractor(nlp, matchers)
    processor = BioCNerSpacy(extractor, 'RadLex')

    text = """No findings to account for symptoms"""
    doc = bioc.BioCDocument.of_text(text)
    processor.process_document(doc)

    extracted_terms = set(ann.text for ann in doc.passages[0].annotations)
    actual_terms = {'symptoms'}
    assert actual_terms == extracted_terms

#
# if __name__ == '__main__':
#     test_ner()
