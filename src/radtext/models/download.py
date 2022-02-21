import nltk
import subprocess
import sys
from pathlib import Path
from radtext import MODELS
from radtext.models.constants import DEFAULT_OPTIONS

DEFAULT_CONFIG = {
    'all': True,
    '--spacy-model': DEFAULT_OPTIONS['--spacy-model'],
    '---bllip_model': DEFAULT_OPTIONS['--bllip_model'],
}

def download(argv):
    if argv['deid'] or argv['all']:
        nltk.download('averaged_perceptron_tagger')
    if argv['stanza'] or argv['all']:
        import stanza
        stanza.download('en')
    if argv['spacy'] or argv['all']:
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download',
                               argv['--spacy-model']])
    if argv['ssplit'] or argv['all']:
        nltk.download('punkt')
    if argv['bllip'] or argv['all']:
        from bllipparser import ModelFetcher
        model_dir = Path(argv['--bllip_model'])
        if not model_dir.exists():
            model_dir.mkdir(parents=True)

        print("downloading GENIA+PubMed model ... [%s]" % model_dir)
        ModelFetcher.download_and_install_model(MODELS['BLLIP-GENIA-PubMed'],
                                                str(model_dir))
    if argv['tree2dep'] or argv['all']:
        import StanfordDependencies
        StanfordDependencies.StanfordDependencies(download_if_missing=True)
    if argv['ner'] or argv['all']:
        nltk.download('stopwords')


def download_all():
    return download(DEFAULT_CONFIG)
