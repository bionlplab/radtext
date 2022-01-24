import logging

from bioc import BioCPassage, BioCSentence, BioCAnnotation, BioCRelation, BioCNode, BioCLocation

from radtext.core import BioCProcessor


class BioCStanza(BioCProcessor):
    def __init__(self, nlp):
        self.nlp = nlp

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        text = passage.text
        doc = self.nlp(text)

        del passage.sentences[:]
        for sent in doc.sentences:
            s = BioCSentence()
            s.offset = sent.tokens[0].start_char + passage.offset
            s.text = sent.text
            for i, token in enumerate(sent.tokens):
                offset = 0
                token_text = token.text
                for word in token.words:
                    ann = BioCAnnotation()
                    ann.id = 'T%s' % i
                    ann.infons['tag'] = word.xpos
                    ann.infons['note_nlp_concept_id'] = word.lemma
                    ann.text = word.text
                    ann.add_location(BioCLocation(token.start_char + offset, len(word.text)))
                    s.add_annotation(ann)

                    if word.head == 0:
                        ann.infons['ROOT'] = True
                        continue

                    rel = BioCRelation()
                    rel.id = 'R%s' % i
                    rel.infons['dependency'] = word.deprel
                    rel.add_node(BioCNode(refid='T%s' % i, role="dependant"))
                    rel.add_node(BioCNode(refid='T%s' % (word.head - 1), role="governor"))
                    s.add_relation(rel)

                    index = token_text.find(word.text, offset)
                    if index == -1:
                        logging.debug('%d: %s: Cannot find word (%s) in the sentence: %s',
                                      docid, passage.offset, word.text, sent.text)
                    offset = index

            passage.add_sentence(s)

        return passage
