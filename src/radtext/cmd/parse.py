"""
Usage:
    parse [options] -i FILE -o FILE

Options:
    --overwrite
    --bllip-model DIR       Bllip parser model path [default: ~/.radtext/bllipparser/BLLIP-GENIA-PubMed]
    -o FILE
    -i FILE
    --only-ner              Parse the sentences with NER annotations at the passage level
"""
import docopt

import bioc
from radtext.cmd.cmd_utils import process_options, process_file
from radtext.models.bllipparser import BioCParserBllip

def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    processor = BioCParserBllip(model_dir=argv['--bllip-model'], only_ner=argv['--only-ner'])
    process_file(argv['-i'], argv['-o'], processor, bioc.DOCUMENT)

if __name__ == '__main__':
    main()
