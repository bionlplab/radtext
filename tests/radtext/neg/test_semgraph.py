import json
from pathlib import Path

import bioc
from bioc import biocjson
import tests
from radtext.models.neg import semgraph

__tests_dir = Path(tests.__file__).parent

json_str = r"""
{
  "offset": 0, 
  "infons": {"parse tree": "(S1 (S (NP (NP (NNS findings)) (: :) (NP (NN chest)) (: :) (NP (CD four) (NNS images)) (: :) (NP (NP (JJ right) (NN picc)) (PP (IN with) (NP (NN tip))) (PP (IN within) (NP (DT the) (JJ upper) (NN svc)))) (. .))))"}, 
  "text": "findings:\nchest: four images:\nright picc with tip within the upper svc.", 
  "annotations": [
    {"id": "T0", "infons": {"tag": "NNS", "lemma": "finding", "ROOT": "True"}, "text": "findings", "locations": [{"offset": 0, "length": 8}]}, 
    {"id": "T1", "infons": {"tag": ":", "lemma": ":"}, "text": ":", "locations": [{"offset": 8, "length": 1}]}, 
    {"id": "T2", "infons": {"tag": "NN", "lemma": "chest"}, "text": "chest", "locations": [{"offset": 10, "length": 5}]}, 
    {"id": "T3", "infons": {"tag": ":", "lemma": ":"}, "text": ":", "locations": [{"offset": 15, "length": 1}]}, 
    {"id": "T4", "infons": {"tag": "CD", "lemma": "four"}, "text": "four", "locations": [{"offset": 17, "length": 4}]}, 
    {"id": "T5", "infons": {"tag": "NNS", "lemma": "image"}, "text": "images", "locations": [{"offset": 22, "length": 6}]}, 
    {"id": "T6", "infons": {"tag": ":", "lemma": ":"}, "text": ":", "locations": [{"offset": 28, "length": 1}]}, 
    {"id": "T7", "infons": {"tag": "JJ", "lemma": "right"}, "text": "right", "locations": [{"offset": 30, "length": 5}]}, 
    {"id": "T8", "infons": {"tag": "NN", "lemma": "picc"}, "text": "picc", "locations": [{"offset": 36, "length": 4}]}, 
    {"id": "T9", "infons": {"tag": "IN", "lemma": "with"}, "text": "with", "locations": [{"offset": 41, "length": 4}]}, 
    {"id": "T10", "infons": {"tag": "NN", "lemma": "tip"}, "text": "tip", "locations": [{"offset": 46, "length": 3}]}, 
    {"id": "T11", "infons": {"tag": "IN", "lemma": "within"}, "text": "within", "locations": [{"offset": 50, "length": 6}]}, 
    {"id": "T12", "infons": {"tag": "DT", "lemma": "the"}, "text": "the", "locations": [{"offset": 57, "length": 3}]}, 
    {"id": "T13", "infons": {"tag": "JJ", "lemma": "upper"}, "text": "upper", "locations": [{"offset": 61, "length": 5}]}, 
    {"id": "T14", "infons": {"tag": "NN", "lemma": "svc"}, "text": "svc", "locations": [{"offset": 67, "length": 3}]}, 
    {"id": "T15", "infons": {"tag": ".", "lemma": "."}, "text": ".", "locations": [{"offset": 70, "length": 1}]}
  ], 
  "relations": [
    {"id": "R0", "infons": {"dependency": "punct"}, "nodes": [{"refid": "T1", "role": "dependant"}, {"refid": "T0", "role": "governor"}]}, 
    {"id": "R1", "infons": {"dependency": "dep"}, "nodes": [{"refid": "T2", "role": "dependant"}, {"refid": "T0", "role": "governor"}]}, 
    {"id": "R2", "infons": {"dependency": "punct"}, "nodes": [{"refid": "T3", "role": "dependant"}, {"refid": "T0", "role": "governor"}]}, 
    {"id": "R3", "infons": {"dependency": "nummod"}, "nodes": [{"refid": "T4", "role": "dependant"}, {"refid": "T5", "role": "governor"}]}, 
    {"id": "R4", "infons": {"dependency": "dep"}, "nodes": [{"refid": "T5", "role": "dependant"}, {"refid": "T0", "role": "governor"}]}, 
    {"id": "R5", "infons": {"dependency": "punct"}, "nodes": [{"refid": "T6", "role": "dependant"}, {"refid": "T0", "role": "governor"}]}, 
    {"id": "R6", "infons": {"dependency": "amod"}, "nodes": [{"refid": "T7", "role": "dependant"}, {"refid": "T8", "role": "governor"}]}, 
    {"id": "R7", "infons": {"dependency": "dep"}, "nodes": [{"refid": "T8", "role": "dependant"}, {"refid": "T0", "role": "governor"}]}, 
    {"id": "R8", "infons": {"dependency": "case"}, "nodes": [{"refid": "T9", "role": "dependant"}, {"refid": "T10", "role": "governor"}]}, 
    {"id": "R9", "infons": {"dependency": "nmod:with"}, "nodes": [{"refid": "T10", "role": "dependant"}, {"refid": "T8", "role": "governor"}]}, 
    {"id": "R10", "infons": {"dependency": "case"}, "nodes": [{"refid": "T11", "role": "dependant"}, {"refid": "T14", "role": "governor"}]}, 
    {"id": "R11", "infons": {"dependency": "det"}, "nodes": [{"refid": "T12", "role": "dependant"}, {"refid": "T14", "role": "governor"}]}, 
    {"id": "R12", "infons": {"dependency": "amod"}, "nodes": [{"refid": "T13", "role": "dependant"}, {"refid": "T14", "role": "governor"}]}, 
    {"id": "R13", "infons": {"dependency": "nmod:within"}, "nodes": [{"refid": "T14", "role": "dependant"}, {"refid": "T8", "role": "governor"}]}, 
    {"id": "R14", "infons": {"dependency": "punct"}, "nodes": [{"refid": "T15", "role": "dependant"}, {"refid": "T0", "role": "governor"}]}
  ]
}
"""


def _read_graph():
    s = biocjson.fromJSON(json.loads(json_str), bioc.SENTENCE)
    g = semgraph.load(s)
    return g


def test_load():
    s = biocjson.fromJSON(json.loads(json_str), bioc.SENTENCE)
    g = semgraph.load(s)
    assert len(g) == 16
    assert g.size() == 15

    s = bioc.BioCSentence()
    g = semgraph.load(s)
    assert len(g) == 0
    assert g.size() == 0


def test_has_get():
    g = _read_graph()
    assert semgraph.has_out_edge(g, 'T0', {"punct"})
    assert not semgraph.has_out_edge(g, 'T2', {"punct"})
    assert not semgraph.has_out_edge(g, 'T0', {""})

    assert semgraph.has_in_edge(g, 'T1', {"punct"})
    assert not semgraph.has_in_edge(g, 'T2', {"punct"})
    assert not semgraph.has_in_edge(g, 'T1', {""})

    assert semgraph.has_out_node(g, 'T0', {":"})
    assert not semgraph.has_out_node(g, 'T1', {":"})
    assert not semgraph.has_out_node(g, 'T0', {""})

    assert semgraph.has_in_node(g, 'T1', {"finding"})
    assert not semgraph.has_in_node(g, 'T4', {"finding"})
    assert not semgraph.has_in_node(g, 'T1', {""})

    assert semgraph.get_in(g, 'T1', {"finding"}, {"punct"})
    assert semgraph.get_in(g, 'T1', {""}, {"punct"}) is None

    assert semgraph.has_in(g, 'T1', {"finding"}, {"punct"})
    assert not semgraph.has_in(g, 'T1', {""}, {"punct"})

    assert semgraph.has_out(g, 'T0', {":"}, {"punct"})
    assert not semgraph.has_out(g, 'T0', {""}, {"punct"})



if __name__ == '__main__':
    test_has_get()