"""
Usage:
    split_section regex [options] -i FILE -o FILE
    split_section medspacy [options] -i FILE -o FILE

Options:
    --section-titles FILE
    -o FILE
    -i FILE
"""
import copy

import bioc
import docopt
import tqdm

from cmd_utils import process_options
from radtext.models.section_split.section_split_regex import BioCSectionSplitterRegex, SECTION_TITLES, combine_patterns


def main():
    argv = docopt.docopt(__doc__)
    process_options(argv)

    try:
        if argv['regex']:
            if argv['--section-titles']:
                with open(argv['--section-titles']) as fp:
                    section_titles = [line.strip() for line in fp]
            else:
                section_titles = SECTION_TITLES
            pattern = combine_patterns(section_titles)
            sec_splitter = BioCSectionSplitterRegex(regex_pattern=pattern)
        elif argv['medspacy']:
            import medspacy
            from radtext.models.section_split.section_split_medspacy import BioCSectionSplitterMedSpacy
            nlp = medspacy.load(enable=["sectionizer"])
            sec_splitter = BioCSectionSplitterMedSpacy(nlp)
        else:
            raise KeyError
    except KeyError as e:
        raise e

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    new_collection = bioc.BioCCollection()
    new_collection.infons = copy.deepcopy(collection.infons)
    for doc in tqdm.tqdm(collection.documents):
        new_doc = sec_splitter.process_document(doc)
        new_collection.add_document(new_doc)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(new_collection, fp)


if __name__ == '__main__':
    main()
