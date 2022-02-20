from pathlib import Path

import bioc
import pytest

from radtext.models.deid import BioCDeidPhilter
from tests import Example_Dir


def test_deid():
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    file = Example_Dir / 'ex3.xml'
    with open(file) as fp:
        collection = bioc.load(fp)
        passage = collection.documents[0].passages[0]

    file = Example_Dir / 'ex3.deid_philter.xml'
    with open(file) as fp:
        deid_collection = bioc.load(fp)
        deid_passage = deid_collection.documents[0].passages[0]

    deid = BioCDeidPhilter()
    passage = deid.process_passage(passage)
    assert passage.text == deid_passage.text

    sentence = collection.documents[1].passages[0].sentences[0]
    deid_sentence = deid_collection.documents[1].passages[0].sentences[0]
    sentence = deid.process_sentence(sentence)
    assert sentence.text == deid_sentence.text


def test_repl():
    with pytest.raises(ValueError):
        BioCDeidPhilter('XX')

