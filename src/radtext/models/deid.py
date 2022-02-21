from typing import Tuple, List

import bioc

from radtext.core import BioCProcessor
from radtext.models.pphilter import Philter
from bioc import BioCPassage, BioCSentence


class BioCDeidPhilter(BioCProcessor):
    def __init__(self, repl: str = 'X'):
        super(BioCDeidPhilter, self).__init__('deid:philter')
        self.philter = Philter()
        self.repl = repl
        if len(repl) != 1:
            raise ValueError('The replacement repl cannot have one char: %s' % repl)

    def deidentify(self, text: str, offset: int) -> Tuple[str, List[bioc.BioCAnnotation]]:
        """
        Replace PHI with replacement repl.
        """
        results = self.philter.deidentify(text)
        anns = []
        for i, r in enumerate(results):
            ann = bioc.BioCAnnotation()
            ann.id = 'A%d' % i
            ann.add_location(bioc.BioCLocation(r['start'] + offset, r['stop'] - r['start']))
            ann.text = r['word']
            ann.infons['source_concept'] = r['phi_type']
            ann.infons['nlp_system'] = self.nlp_system
            ann.infons['nlp_date_time'] = self.nlp_date_time
            anns.append(ann)

        for ann in anns:
            loc = ann.total_span
            text = text[:loc.offset - offset] + self.repl * loc.length + text[loc.end - offset:]
        return text, anns

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        text, anns = self.deidentify(passage.text, passage.offset)
        passage.annotations += anns
        passage.text = text

        for sentence in passage.sentences:
            self.process_sentence(sentence, docid)

        return passage

    def process_sentence(self, sentence: BioCSentence, docid: str = None) -> BioCSentence:
        text, anns = self.deidentify(sentence.text, sentence.offset)
        sentence.annotations += anns
        sentence.text = text
        return sentence
