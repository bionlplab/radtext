"""
Usage:
    tree2dep [options] -i FILE -o FILE

Options:
    --overwrite
    -o FILE
    -i FILE
"""
import bioc
import docopt
import tqdm

from radtext.cmd.cmd_utils import process_options
from radtext.models.tree2dep import BioCPtb2DepConverter


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    converter = BioCPtb2DepConverter()

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        for passage in tqdm.tqdm(doc.passages, leave=False):
            for sentence in tqdm.tqdm(passage.sentences, leave=False):
                converter.process_sentence(sentence, doc.concept_id)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    main()