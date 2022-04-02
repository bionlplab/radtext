"""
Usage:
    preprocess stanza [options] -i FILE -o FILE
    preprocess spacy [--overwrite --spacy-model NAME] -i FILE -o FILE

Options:
    --overwrite
    --spacy-model NAME   spaCy traiend model [default: en_core_web_sm]
    -o FILE
    -i FILE
"""
import bioc
import docopt
import spacy
import tqdm
import stanza
from stanza.pipeline.core import ResourcesFileNotFoundError

from radtext.cmd.cmd_utils import process_options, process_file
from radtext.models.preprocess_spacy import BioCSpacy
from radtext.models.preprocess_stanza import BioCStanza


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    if argv['stanza']:
        try:
            nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')
        except ResourcesFileNotFoundError:
            print('Install spacy model using \'python -m spacy download en_core_web_sm\'')
            return
        processor = BioCStanza(nlp)
    elif argv['spacy']:
        try:
            nlp = spacy.load(argv['--spacy-model'])
        except IOError:
            print('Install spacy model using \'python -m spacy download en_core_web_sm\'')
            return
        processor = BioCSpacy(nlp)
    else:
        raise KeyError

    process_file(argv['-i'], argv['-o'], processor, bioc.DOCUMENT)


if __name__ == '__main__':
    main()
