from typing import List

from bioc import BioCDocument, BioCPassage, BioCSentence


class BioCProcessor:
    def process_document(self, doc: BioCDocument) -> BioCDocument:
        for passage in doc.passages:
            self.process_passage(passage, docid=doc.id)
        return doc

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        for sentence in passage.sentences:
            self.process_sentence(sentence, docid)
        return passage

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        raise NotImplementedError


class BioCPipeline:
    def __init__(self, processors: List[BioCProcessor]):
        self.processors = processors

    def process_document(self, doc: BioCDocument):
        for processor in self.processors:
            doc = processor.process_document(doc)
        return doc

    def __call__(self, doc):
        return self.process_document(doc)
