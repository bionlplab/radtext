"""
Usage:
    ner spacy [options] --radlex FILE -i FILE -o FILE
    ner regex [options] --phrases FILE -i FILE -o FILE

Options:
    --overwrite
    --radlex FILE
    -o FILE
    -i FILE
    --phrases FILE
"""
import sys
sys.path.append('..')
from typing import Iterable, Tuple

import bioc
import docopt
import tqdm
import en_core_web_sm
from cmd_utils import process_options
from radtext.ner_regex import NerRegExExtractor, BioCNerRegex
from radtext.ner_spacy import NerSpacyExtractor, BioCNerSpacy
import pandas as pd


def get_class_id(url: str) -> str:
    """http://www.radlex.org/RID/#RID43314"""
    if len(url) == 0:
        return 'ROOT'
    elif '/#' in url:
        return url[url.rfind('/') + 2:]
    elif '/' in url:
        return url[url.rfind('/') + 1:]
    else:
        return url


def iterparse_RadLex4(pathname) -> Iterable[Tuple[str, str, str]]:
    df = pd.read_excel(pathname, dtype=str)
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        if not pd.isna(row['Comment']) and \
                (row['Comment'].lower().startswith('duplicate') or row['Comment'].lower() == 'not needed'):
            continue

        label = row['Preferred Label']
        if label is None or label == '':
            continue

        id = row['Class ID']
        id = get_class_id(id)
        yield id, label, label
        synonyms = row['Synonyms']
        if isinstance(synonyms, str):
            for t in synonyms.split('|'):
                yield id, label, t.strip()


if __name__ == '__main__':
    argv = docopt.docopt(__doc__)
    process_options(argv)

    nlp = en_core_web_sm.load()

    if argv['spacy']:
        data_itr = iterparse_RadLex4(argv['--radlex'])
        extractor = NerSpacyExtractor(nlp, data_itr)
        processor = BioCNerSpacy(extractor)
    elif argv['regex']:
        extractor = NerRegExExtractor(argv['--phrases'])
        processor = BioCNerRegex(extractor)
    else:
        raise ValueError('No ontology is given')

    # reader = bioc.BioCXMLDocumentReader(argv['-i'])
    # collection = reader.get_collection_info()
    #
    # writer = bioc.BioCXMLDocumentWriter(argv['-o'])
    # writer.write_collection_info(collection)
    #
    # for doc in tqdm.tqdm(reader):
    #     for passage in tqdm.tqdm(doc.passages, leave=False):
    #         processor.process_passage(passage, doc.id)
    #     writer.write_document(doc)
    #
    # reader.close()
    # writer.close()

    with open(argv['-i']) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        for passage in tqdm.tqdm(doc.passages, leave=False):
            processor.process_passage(passage, doc.id)

    with open(argv['-o'], 'w') as fp:
        bioc.dump(collection, fp)
