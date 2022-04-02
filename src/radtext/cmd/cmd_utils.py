import logging
import os

import tqdm

import bioc
from radtext.core import BioCProcessor


def process_options(argv):
    set_logging(argv)
    check_outfile(argv)


def set_logging(argv):
    if '--verbose' not in argv:
        verbose = 0
    else:
        verbose = int(argv['--verbose'])

    if verbose == 0:
        logging_level = logging.CRITICAL
    elif verbose == 1:
        logging_level = logging.INFO
    elif verbose == 2:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    format = r'%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s'
    # logging.basicConfig(level=logging.DEBUG, format=format, datefmt='%m-%d %H:%M', filename=filename, filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging_level)
    # set a format which is simpler for console use
    formatter = logging.Formatter(format)
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def check_outfile(argv):
    if '--overwrite' not in argv:
        return
    if not argv['--overwrite'] and os.path.exists(argv['-o']):
        print('%s exists.' % argv['-o'])
        exit(1)


def process_file(src, dest, processor: BioCProcessor, level: int):
    with open(src) as fp:
        collection = bioc.load(fp)

    for doc in tqdm.tqdm(collection.documents):
        if level == bioc.DOCUMENT:
            processor.process_document(doc)
        elif level == bioc.PASSAGE:
            for passage in tqdm.tqdm(doc.passages, leave=False):
                processor.process_passage(passage, doc.id)
        elif level == bioc.SENTENCE:
            for passage in tqdm.tqdm(doc.passages, leave=False):
                for sentence in tqdm.tqdm(passage.sentences, leave=False):
                    processor.process_sentence(sentence, doc.id)

    with open(dest, 'w') as fp:
        bioc.dump(collection, fp)