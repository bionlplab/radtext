import bioc
import spacy

from radtext.models.ner.ner_spacy import BioCNerSpacy, NerSpacyExtractor
from radtext.models.ner.radlex import RadLex4
from tests import Resource_Dir


nlp = spacy.load('en_core_web_sm', exclude=['ner', 'parser', 'senter'])
phrases_file = Resource_Dir / 'Radlex4.1.xlsx'
radlex = RadLex4(phrases_file)
matchers = radlex.get_spacy_matchers(nlp)
extractor = NerSpacyExtractor(nlp, matchers)
processor = BioCNerSpacy(extractor, 'RadLex')


def test_ner():
    text = """No findings to account for symptoms"""
    doc = bioc.BioCDocument.of_text(text)
    processor.process_document(doc)

    extracted_terms = set(ann.text for ann in doc.passages[0].annotations)
    actual_terms = {'symptoms'}
    assert actual_terms == extracted_terms


if __name__ == '__main__':
    test_ner()
