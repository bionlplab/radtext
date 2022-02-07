"""
Usage:
    neg [options] -i FILE -o FILE

Options:
    --regex_negation FILE               [default: resources/patterns/regex_negation.yml]
    --regex_uncertainty_pre_neg FILE    [default: resources/patterns/regex_uncertainty_pre_negation.yml]
    --regex_uncertainty_post_neg FILE   [default: resources/patterns/regex_uncertainty_post_negation.yml]
    --regex_double_neg FILE             [default: resources/patterns/regex_double_negation.yml]
    --ngrex_negation FILE               [default: resources/patterns/ngrex_negation.yml]
    --ngrex_uncertainty_pre_neg FILE    [default: resources/patterns/ngrex_uncertainty_pre_negation.yml]
    --ngrex_uncertainty_post_neg FILE   [default: resources/patterns/ngrex_uncertainty_post_negation.yml]
    --ngrex_double_neg FILE             [default: resources/patterns/ngrex_double_negation.yml]
    --overwrite
    --sort_anns
    -o FILE
    -i FILE
"""
import sys
sys.path.append('..')
import bioc
import docopt
import tqdm

from cmd_utils import process_options
from radtext.neg.match_ngrex import NegGrex
from radtext.neg.match_regex import NegRegex
from radtext.neg.neg_cleanup import NegCleanUp
from radtext.neg.neg_pipeline import BioCNeg

if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)
    regex_actor = NegRegex(
        argv['--regex_negation'],
        argv['--regex_uncertainty_pre_neg'],
        argv['--regex_uncertainty_post_neg'],
        argv['--regex_double_neg'])
    ngrex_actor = NegGrex(
        argv['--ngrex_negation'],
        argv['--ngrex_uncertainty_pre_neg'],
        argv['--ngrex_uncertainty_post_neg'],
        argv['--ngrex_double_neg'])

    neg_actor = BioCNeg(regex_actor=regex_actor, ngrex_actor=ngrex_actor)
    cleanup_actor = NegCleanUp(argv['--sort_anns'])

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        for passage in tqdm.tqdm(doc.passages, leave=False):
            neg_actor.process_passage(passage, doc.id)
            cleanup_actor.process_passage(passage, doc.id)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
