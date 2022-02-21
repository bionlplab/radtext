from datetime import datetime
from typing import List, Union

from bioc import BioCDocument, BioCPassage, BioCSentence, BioCCollection


class BioCProcessor:
    def __init__(self, nlp_system: str):
        self.nlp_date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.nlp_system = nlp_system

    def process_collection(self, collection: BioCCollection) -> BioCCollection:
        for document in collection.documents:
            self.process_document(document)
        return collection

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
    def __init__(self):
        self.processors = []  # type: List[BioCProcessor]

    def process_collection(self, collection: BioCCollection) -> BioCCollection:
        for processor in self.processors:
            collection = processor.process_collection(collection)
        return collection

    def process_document(self, document: BioCDocument) -> BioCDocument:
        for processor in self.processors:
            document = processor.process_document(document)
        return document

    def process_passage(self, passage: BioCPassage) -> BioCPassage:
        for processor in self.processors:
            passage = processor.process_passage(passage)
        return passage

    def process_sentence(self, sentence: BioCSentence) -> BioCSentence:
        for processor in self.processors:
            sentence = processor.process_sentence(sentence)
        return sentence

    def __call__(self, doc: Union[BioCCollection, BioCDocument, BioCPassage, BioCSentence, str]):
        if isinstance(doc, BioCCollection):
            return self.process_collection(doc)
        elif isinstance(doc, BioCDocument):
            return self.process_document(doc)
        elif isinstance(doc, BioCPassage):
            return self.process_passage(doc)
        elif isinstance(doc, BioCSentence):
            return self.process_sentence(doc)
        elif isinstance(doc, str):
            return self.process_sentence(BioCSentence.of_text(doc))
        else:
            raise TypeError('Input should be a string or bioc data model.')
