from datetime import datetime

import bioc

from radtext.core import BioCProcessor
from radtext.section_split_regex import strip, is_empty


class BioCSectionSplitterMedSpacy(BioCProcessor):
    def __init__(self, nlp):
        self.nlp = nlp

    def process_document(self, doc: bioc.BioCDocument) -> bioc.BioCDocument:
        """
        Split one report into sections. Section splitting is a deterministic
        consequence of section titles.
        """
        def create_passage(text, offset, start, end, title=None) -> bioc.BioCPassage:
            passage = bioc.BioCPassage()
            passage.offset = start + offset
            passage.text = text[start:end]
            if title is not None:
                passage.infons['section_concept'] = title[:-1].strip() if title[-1] == ':' else title.strip()
                passage.infons['type'] = 'title_1'
            strip(passage)
            return passage

        offset, text = bioc.utils.get_text(doc)
        del doc.passages[:]

        anns = []
        medspacy_doc = self.nlp(text)
        for i, title in enumerate(medspacy_doc._.section_titles):
            if len(title) == 0:
                continue
            passage = create_passage(text, offset, title.start_char, title.end_char, title.text)
            if not is_empty(passage):
                doc.add_passage(passage)
                ann = bioc.BioCAnnotation()
                ann.id = 'S{}'.format(i)
                ann.text = passage.text
                ann.infons['section_concept'] = passage.infons['section_concept']
                ann.infons['type'] = passage.infons['type']
                ann.infons['nlp_system'] = 'medspacy'
                ann.infons['nlp_date_time'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                ann.add_location(bioc.BioCLocation(offset + title.start_char, title.end_char - title.start_char))
                anns.append(ann)

        for body in medspacy_doc._.section_bodies:
            passage = create_passage(text, offset, body.start_char, body.end_char)
            if not is_empty(passage):
                doc.add_passage(passage)

        doc.passages = sorted(doc.passages, key=lambda p: p.offset)
        doc.annotations += anns
        return doc
