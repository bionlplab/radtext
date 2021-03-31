"""
Usage:
    parse [options] -i FILE -o FILE

Options:
    --overwrite
    -o FILE
    -i FILE
"""
import os

import bioc
import docopt
import tqdm

from cmd.cmd_utils import process_options
from ptakes.parse_bllip import BioCParserBllip


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)

    parser = BioCParserBllip()

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        for passage in tqdm.tqdm(doc.passages, leave=False):
            for sentence in tqdm.tqdm(passage.sentences, leave=False):
                parser.process_sentence(sentence, doc.id)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
