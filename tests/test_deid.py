import bioc
import pytest

from radtext.models.deid import BioCDeidPhilter


def test_deid():
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    text = 'Comparison: July 18, 2010.'
    passage = bioc.BioCPassage.of_text(text, 0)

    deid = BioCDeidPhilter()
    deid_passage = deid.process_passage(passage)
    assert deid_passage.text == 'Comparison: XXXXXXXXXXXXX.'

    text = "Patient's Name: LATTE, MONICA"
    sentence = bioc.BioCSentence.of_text(text, 0)
    deid_sentence = deid.process_sentence(sentence)
    assert deid_sentence.text == "Patient's Name: XXXXXXXXXXXXX"


def test_repl():
    with pytest.raises(ValueError):
        BioCDeidPhilter('XX')

