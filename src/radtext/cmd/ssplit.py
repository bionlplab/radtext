"""
Usage:
    ssplit [options] -i FILE -o FILE

Options:
    --newline   Whether to treat newlines as sentence breaks.
    -o FILE
    -i FILE
"""
import bioc
import docopt
import tqdm

from radtext.cmd.cmd_utils import process_options
from radtext.models.sentence_split_nltk import BioCSSplitterNLTK


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    processor = BioCSSplitterNLTK(newline=argv['--newline'])

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        for passage in tqdm.tqdm(doc.passages, leave=False):
            processor.process_passage(passage, doc.concept_id)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    main()
