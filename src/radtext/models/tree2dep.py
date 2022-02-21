import logging

import StanfordDependencies
import bioc
from StanfordDependencies import Sentence
from bioc import BioCSentence

from radtext.core import BioCProcessor


JPYPE = 'jpype'
SUBPROCESS = 'subprocess'


def adapt_value(value: str) -> str:
    """
    Adapt string in PTB
    """
    value = value.replace("-LRB-", "(")
    value = value.replace("-RRB-", ")")
    value = value.replace("-LSB-", "[")
    value = value.replace("-RSB-", "]")
    value = value.replace("-LCB-", "{")
    value = value.replace("-RCB-", "}")
    value = value.replace("-lrb-", "(")
    value = value.replace("-rrb-", ")")
    value = value.replace("-lsb-", "[")
    value = value.replace("-rsb-", "]")
    value = value.replace("``", "\"")
    value = value.replace("''", "\"")
    value = value.replace("`", "'")
    return value


def convert_dg(dependency_graph, text, offset, ann_index=0, rel_index=0, has_lemmas=True):
    """
    Convert dependency graph to annotations and relations
    """
    logger = logging.getLogger(__name__)
    annotations = []
    relations = []
    annotation_id_map = {}
    start = 0
    for node in dependency_graph:
        if node.index in annotation_id_map:
            continue
        node_form = node.form
        index = text.find(node_form, start)
        if index == -1:
            node_form = adapt_value(node.form)
            index = text.find(node_form, start)
            if index == -1:
                logger.debug('Cannot convert parse tree to dependency graph at %d\n%d\n%s',
                             start, offset, str(dependency_graph))
                return [], []

        ann = bioc.BioCAnnotation()
        ann.id = 'T{}'.format(ann_index)
        ann.text = node_form
        ann.infons['tag'] = node.pos
        if has_lemmas:
            ann.infons['lemma'] = node.lemma.lower()
            # ann.infons['note_nlp_concept_id'] = node.lemma.lower()

        start = index

        ann.add_location(bioc.BioCLocation(start + offset, len(node_form)))
        annotations.append(ann)
        annotation_id_map[node.index] = ann_index
        ann_index += 1
        start += len(node_form)

    for node in dependency_graph:
        if node.head == 0:
            ann = annotations[annotation_id_map[node.index]]
            ann.infons['ROOT'] = True
            continue
        relation = bioc.BioCRelation()
        relation.id = 'R{}'.format(rel_index)
        relation.infons['dependency'] = node.deprel
        if node.extra:
            relation.infons['extra'] = node.extra
        relation.add_node(bioc.BioCNode('T{}'.format(
            annotation_id_map[node.index]), 'dependant'))
        relation.add_node(bioc.BioCNode('T{}'.format(
            annotation_id_map[node.head]), 'governor'))
        relations.append(relation)
        rel_index += 1

    return annotations, relations


class Ptb2DepConverter:
    """
    Convert ptb trees to universal dependencies
    """

    basic = 'basic'
    collapsed = 'collapsed'
    CCprocessed = 'CCprocessed'
    collapsedTree = 'collapsedTree'

    def __init__(self, representation='CCprocessed', universal=True):
        """
        Args:
            representation(str): Currently supported representations are
                'basic', 'collapsed', 'CCprocessed', and 'collapsedTree'
            universal(bool): if True, use universal dependencies if they're available
        """
        try:
            import jpype
            self.backend = JPYPE
        except ImportError:
            self.backend = SUBPROCESS

        self.sd = StanfordDependencies.get_instance(backend=self.backend)
        self.representation = representation
        self.universal = universal
        self.has_lemma = (self.backend == JPYPE)

    def convert(self, parse_tree: str) -> Sentence:
        """
        Convert ptb trees

        Args:
            parse_tree: parse tree in PTB format

        Examples:
            (ROOT (NP (JJ hello) (NN world) (. !)))
        """
        if self.backend == JPYPE:
            return self.sd.convert_tree(parse_tree,
                                        representation=self.representation,
                                        universal=self.universal,
                                        add_lemmas=True)
        elif self.backend == SUBPROCESS:
            return self.sd.convert_tree(parse_tree,
                                        representation=self.representation,
                                        universal=self.universal)
        else:
            raise ValueError("Unknown backend: %r (known backends: 'subprocess' and 'jpype')" % self.backend)



class BioCPtb2DepConverter(BioCProcessor):
    def __init__(self, representation='CCprocessed', universal=True):
        super(BioCPtb2DepConverter, self).__init__('tree2dep')
        self.converter = Ptb2DepConverter(representation=representation, universal=universal)
        self.model = 'PyStanfordDependencies'

    def process_sentence(self, sentence: BioCSentence, docid: str = None):
        # check for empty infons, don't process if empty
        # this sometimes happens with poorly tokenized sentences
        if not sentence.infons \
                or ('parse_tree' not in sentence.infons) \
                or (sentence.infons['parse_tree'] is None) \
                or sentence.infons['parse_tree'] == 'None':
            return

        try:
            dependency_graph = self.converter.convert(sentence.infons['parse_tree'])
            anns, rels = convert_dg(dependency_graph, sentence.text,
                                    sentence.offset,
                                    has_lemmas=self.converter.has_lemma)
            for ann in anns:
                ann.infons['nlp_system'] = self.nlp_system
                ann.infons['nlp_date_time'] = self.nlp_date_time
            for rel in rels:
                rel.infons['nlp_system'] = self.nlp_system
                rel.infons['nlp_date_time'] = self.nlp_date_time

            sentence.annotations = anns
            sentence.relations = rels
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.exception("%s:%s: Cannot process sentence: %s", docid, sentence.offset, sentence.text)
            print(e)
        return sentence