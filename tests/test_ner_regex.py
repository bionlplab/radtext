import bioc

from radtext.models.ner.ner_regex import NerRegExExtractor, BioCNerRegex
from radtext.cmd.ner import load_yml


def test_ner(resource_dir):
    phrases_file = resource_dir / 'chexpert_phrases.yml'
    patterns = load_yml(phrases_file)
    extractor = NerRegExExtractor(patterns)
    processor = BioCNerRegex(extractor, name='chexpert_phrases')

    text = """findings: pa and lat cxr at 7:34 p.m.. heart and mediastinum are
stable. lungs are unchanged. air- filled cystic changes. no
pneumothorax. osseous structures unchanged scoliosis
impression: stable chest.
dictating """
    doc = bioc.BioCDocument.of_text(text)
    processor.process_document(doc)

    extracted_terms = set(ann.text for ann in doc.passages[0].annotations)
    actual_terms = {'mediastinum', 'pneumothorax', 'scoliosis'}
    assert actual_terms == extracted_terms
