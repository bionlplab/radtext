from radtext.models.bioc_cdm_converter import convert_bioc_to_note_nlp
import bioc


def test(example_dir):
    file = example_dir / 'ex4.ner_radlex.xml'

    with open(file) as fp:
        collection = bioc.load(fp)

    df = convert_bioc_to_note_nlp(collection)
    df = df[df['note_nlp_id'] == 'S1']
    assert df.iloc[0]['offset'] == 178


# if __name__ == '__main__':
#     test()