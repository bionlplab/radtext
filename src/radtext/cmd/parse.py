"""
Usage:
    parse [options] -i FILE -o FILE

Options:
    --overwrite
    --bllip_model DIR     Bllip parser model path [default: ~/.radtext/bllipparser/BLLIP-GENIA-PubMed]
    -o FILE
    -i FILE
"""
import bioc
import docopt
import tqdm
from radtext.cmd.cmd_utils import process_options
from radtext.models.bllipparser import BioCParserBllip


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)

    processor = BioCParserBllip(model_dir=argv['--bllip_model'])

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        processor.process_document(doc)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
