import bioc

from radtext.core import BioCProcessor
from radtext.pphilter.philter import Philter


class BioCDeidPhilter(BioCProcessor):
    def __init__(self, philter: Philter):
        self.philter = philter

    def deidentify_anns(self, text):
        results = self.philter.deidentify(text)
        anns = []
        for i, r in enumerate(results):
            ann = bioc.BioCAnnotation()
            ann.id = 'A%d' % i
            ann.add_location(bioc.BioCLocation(r['start'], r['stop'] - r['start']))
            ann.text = r['word']
            ann.infons['phi_type'] = r['phi_type']
            anns.append(ann)
        return anns

    def process_document(self, doc: bioc.BioCDocument, replacement='X') -> bioc.BioCDocument:
        """
        De-identify document
        """
        for passage in doc.passages:
            text = passage.text
            anns = self.deidentify_anns(text)
            for ann in anns:
                loc = ann.total_span
                text = text[:loc.offset] + replacement * loc.length + text[loc.end:]
            passage.text = text
        return doc

