from bioc import BioCPassage, BioCSentence, BioCAnnotation, BioCRelation, BioCNode, BioCLocation

from radtext.core import BioCProcessor


class BioCSpacy(BioCProcessor):
    def __init__(self, nlp):
        self.nlp = nlp

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        text = passage.text
        doc = self.nlp(text)

        del passage.sentences[:]
        for sent in doc.sents:
            s = BioCSentence()
            s.offset = sent.start_char + passage.offset
            s.text = sent.text_with_ws
            for token in sent:
                ann = BioCAnnotation()
                ann.id = 'T%s' % token.i
                ann.infons['tag'] = token.tag_
                ann.infons['note_nlp_concept_id'] = token.lemma_
                ann.text = token.text
                ann.add_location(BioCLocation(token.idx, len(token)))
                s.add_annotation(ann)

                if token.dep_ == 'ROOT':
                    ann.infons['ROOT'] = True
                    continue

                rel = BioCRelation()
                rel.id = 'R%s' % token.i
                rel.infons['dependency'] = token.dep_
                rel.add_node(BioCNode(refid='T%s' % token.i, role="dependant"))
                rel.add_node(BioCNode(refid='T%s' % token.head.i, role="governor"))
                s.add_relation(rel)

            passage.add_sentence(s)

        return passage
