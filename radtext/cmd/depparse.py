"""
Usage:
    preprocess stanza [options] -i FILE -o FILE
    preprocess spacy [options] -i FILE -o FILE
    preprocess bllip [options] -i FILE -o FILE

Options:
    --overwrite
    --spacy-model <str>     Spacy model [default: en_core_web_sm]
    --bllip_model <str>     Bllip parser model path [default: ]
    -o FILE
    -i FILE
"""
import bioc
import docopt
import spacy
import tqdm
from cmd_utils import process_options
from radtext.parse_bllip import BioCParserBllip
from radtext.preprocess_spacy import BioCSpacy
from radtext.preprocess_stanza import BioCStanza


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)

    if argv['stanza']:
        import stanza
        nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')
        processor = BioCStanza(nlp)
    elif argv['spacy']:
        try:
            nlp = spacy.load(argv['--spacy-model'])
        except IOError:
            print('Install spacy model using \'python -m spacy download en_core_web_sm\'')
            exit(1)
        processor = BioCSpacy(nlp)
    elif argv['bllip']:
        processor = BioCParserBllip(model_dir=argv['--model'])
    else:
       raise KeyError

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        processor.process_document(doc)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
