import bioc

from radtext.core import BioCProcessor
from radtext.pphilter.philter import Philter
from bioc import BioCPassage, BioCSentence


class BioCDeidPhilter(BioCProcessor):
    def __init__(self, philter: Philter):
        self.philter = philter

    def deidentify_anns(self, text, offset):
        results = self.philter.deidentify(text)
        anns = []
        for i, r in enumerate(results):
            ann = bioc.BioCAnnotation()
            ann.id = 'A%d' % i
            ann.add_location(bioc.BioCLocation(r['start'] + offset, r['stop'] - r['start']))
            ann.text = r['word']
            ann.infons['phi_type'] = r['phi_type']
            anns.append(ann)
        return anns

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        text = passage.text
        anns = self.deidentify_anns(text, passage.offset)
        passage.annotations += anns
        return passage

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        text = sentence.text
        anns = self.deidentify_anns(text, sentence.offset)
        sentence.annotations += anns
        return sentence

    def deidentify_passage(self, passage: BioCPassage, replacement='X'):
        passage.text = self.deidentify_text(passage.text, passage.offset, passage.annotations, replacement)
        return passage

    def deidentify_sentence(self, sentence: BioCSentence, replacement='X'):
        sentence.text = self.deidentify_text(sentence.text, sentence.offset, sentence.annotations, replacement)
        return sentence

    def deidentify_text(self, text, offset, anns, replacement='X'):
        for ann in anns:
            if 'phi_type' in ann.infons:
                loc = ann.total_span
                text = text[:loc.offset - offset] + replacement * loc.length + text[loc.end - offset:]
        return text