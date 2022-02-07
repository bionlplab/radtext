"""
Usage:
    preprocess stanza [options] -i FILE -o FILE
    preprocess spacy [options] -i FILE -o FILE

Options:
    --overwrite
    --model <str>       en_core_web_sm [default: en_core_web_sm]
    --processors <str>  [default: ssplit,parse,ptb2ud]
    -o FILE
    -i FILE
"""
import sys
sys.path.append('..')
import bioc
import docopt
import tqdm
from cmd_utils import process_options
from radtext.convert_ptb_to_ud import BioCPtb2DepConverter
from radtext.core import BioCPipeline
from radtext.parse_bllip import BioCParserBllip
from radtext.preprocess_spacy import BioCSpacy
from radtext.preprocess_stanza import BioCStanza


from radtext.sentence_split_nltk import BioCSSplitterNLTK


def get_ptakes_processors(argv):
    processors = []
    for p in argv['--processors'].split(','):
        if p == 'ssplit':
            if '--newline' in argv and argv['--newline']:
                newline = True
            else:
                newline = False
            processors.append(BioCSSplitterNLTK(newline=newline))
        elif p == 'parse':
            processors.append(BioCParserBllip())
        elif p == 'ptb2ud':
            processors.append(BioCPtb2DepConverter())
        else:
            raise ValueError('Cannot find processor: %s', p)
    return processors


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)

    if argv['stanza']:
        import stanza
        nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')
        processor = BioCStanza(nlp)
    elif argv['spacy']:
        if argv['--model'] == 'en_core_web_sm':
            import en_core_web_sm
            nlp = en_core_web_sm.load()
        else:
            import en_core_web_sm

            nlp = en_core_web_sm.load()
        processor = BioCSpacy(nlp)
    else:
       raise KeyError

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        processor.process_document(doc)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
