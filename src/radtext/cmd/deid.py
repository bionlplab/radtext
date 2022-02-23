"""
Usage:
    deid [options] -i FILE -o FILE

Options:
    --overwrite
    -o FILE
    -i FILE
    --repl CHAR    PHI replacement char [default: X]
"""
import bioc
import docopt
import tqdm

from radtext.cmd.cmd_utils import process_options
from radtext.models.deid import BioCDeidPhilter


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    processor = BioCDeidPhilter(argv['--repl'])

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        processor.process_document(doc)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    main()
