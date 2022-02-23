import hashlib
import logging
import os
from os import PathLike
from pathlib import Path
from typing import List, NewType, Union

import nltk
import subprocess
import sys

import requests
import tqdm

from radtext.models.constants import DEFAULT_OPTIONS, ALL_ANNOTATORS, LOCAL_DIR, LOCAL_RESOURCE_DIR, \
    RADTEXT_RESOURCES_GITHUB, BLLIP_MODEL_URL

RadTextPath = NewType('RadTextPath', Union[str, PathLike, bytes])


def get_md5(path: RadTextPath) -> str:
    """
    Get the MD5 value of a path.
    """
    with open(path, 'rb') as fin:
        data = fin.read()
    return hashlib.md5(data).hexdigest()


def assert_file_exists(path: RadTextPath, md5: str=None):
    assert os.path.exists(path), "Could not find file at %s" % path
    if md5:
        file_md5 = get_md5(path)
        assert file_md5 == md5, "md5 for %s is %s, expected %s" % (path, file_md5, md5)


def file_exists(path: RadTextPath, md5: str=None):
    """
    Check if the file at `path` exists and match the provided md5 value.
    """
    if md5 is None:
        return os.path.exists(path)
    else:
        return os.path.exists(path) and get_md5(path) == md5


def ensure_dir(path: RadTextPath):
    """
    Create dir in case it does not exist.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def download_file(url: str, path: RadTextPath, proxies=None, raise_for_status=False) -> int:
    """
    Download a URL into a file as specified by `path`.
    """
    desc = 'Downloading ' + url
    print(desc)
    r = requests.get(url, stream=True, proxies=proxies)
    with open(path, 'wb') as f:
        file_size = int(r.headers.get('content-length'))
        default_chunk_size = 131072

        with tqdm.tqdm(total=file_size, unit='B', unit_scale=True, desc=desc) as pbar:
            for chunk in r.iter_content(chunk_size=default_chunk_size):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    pbar.update(len(chunk))
    if raise_for_status:
        r.raise_for_status()
    return r.status_code


def request_file(url: str, path: RadTextPath, proxies=None, md5: str=None, raise_for_status=False):
    """
    Download a URL into a file as specified by `path`.
    """
    ensure_dir(path)
    if file_exists(path, md5):
        logging.info(f'File exists: {path}.')
        return
    download_file(url, path, proxies, raise_for_status)
    assert_file_exists(path, md5)


def request_radtext(dst, md5: str=None, proxies=None):
    base = os.path.basename(dst)
    request_file('{}/{}'.format(RADTEXT_RESOURCES_GITHUB, base), dst, md5=md5, proxies=proxies)


def download(annotators: List[str]=None, argv=None, proxies=None):
    if annotators is None:
        annotators = ALL_ANNOTATORS
    if argv is None:
        argv = DEFAULT_OPTIONS

    request_radtext(DEFAULT_OPTIONS['--section-titles'], proxies=proxies)
    request_radtext(DEFAULT_OPTIONS['--phrases'], proxies=proxies)
    request_radtext(DEFAULT_OPTIONS['--radlex'], proxies=proxies)
    request_radtext(DEFAULT_OPTIONS['--regex_patterns'], proxies=proxies)
    request_radtext(DEFAULT_OPTIONS['--ngrex_patterns'], proxies=proxies)

    for annotator in annotators:
        if annotator == 'deid:philter':
            print('Downloading: NLTK averaged_perceptron_tagger')
            nltk.download('averaged_perceptron_tagger')
        elif annotator in ['preprocess:spacy', 'ner:spacy']:
            print('Downloading: space %s' % argv['--spacy-model'])
            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', argv['--spacy-model']])
        elif annotator == 'preprocess:stanza':
            import stanza
            print('Downloading: Stanza en')
            stanza.download('en')
        elif annotator == 'parse:bllip':
            from bllipparser import ModelFetcher
            model_dir = argv['--bllip-model'].parent
            print("Downloading: %s from [%s]" % (model_dir, BLLIP_MODEL_URL))
            if not model_dir.exists():
                model_dir.mkdir(parents=True)
            ModelFetcher.download_and_install_model(BLLIP_MODEL_URL, str(model_dir))
        elif annotator == 'ssplit:nltk':
            print('Downloading: NLTK punkt')
            nltk.download('punkt')
        elif annotator == 'ner:regex':
            print('Downloading: NLTK stopwords')
            nltk.download('stopwords')
        elif annotator == 'tree2dep':
            print("Downloading: StanfordDependencies")
            import StanfordDependencies
            StanfordDependencies.StanfordDependencies(download_if_missing=True)
        elif annotator in ['secsplit:regex', 'secsplit:medspacy', 'neg:negbio']:
            pass
        else:
            raise KeyError('%s: Do not support this annotator' % annotator)

