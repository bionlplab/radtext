"""
Usage:
    run_module [--verbose] <command> [<args>...]
Options:
    --verbose   Print more information about progress.
The most commonly used negbio commands are:
    csv2bioc
    deid
    split_section
    preprocess
    ner
    parse
    neg
    collect_label
"""

from subprocess import call
import logging
import os

def parse_args(doc, **kwargs):
    argv = docopt.docopt(doc, **kwargs)
    if argv['--verbose']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.debug('Arguments:\n%s', get_args(argv))
    return argv

def main():
    args = parse_args(__doc__, version='radanony', options_first=True)
    logging.debug('CWD: %s', os.getcwd())

    argv = args['<args>']
    if args['<command>'] == 'csv2bioc':
        exit(call(['python', '-m', 'cmd.csv2bioc'] + argv))
    elif args['<command>'] == 'deid':
        exit(call(['python', '-m', 'cmd.deidentify'] + argv))
    elif args['<command>'] == 'split_section':
        exit(call(['python', '-m', 'cmd.split_section'] + argv))
    elif args['<command>'] == 'preprocess':
        exit(call(['python', '-m', 'cmd.preprocess_pipeline'] + argv))
    elif args['<command>'] == 'ner':
        exit(call(['python', '-m', 'cmd.ner'] + argv))
    elif args['<command>'] == 'parse':
        exit(call(['python', '-m', 'cmd.parse'] + argv))
    elif args['<command>'] == 'neg':
        exit(call(['python', '-m', 'cmd.neg'] + argv))
    elif args['<command>'] == 'collect_label':
        exit(call(['python', '-m', 'cmd.collect_neg_labels'] + argv))
    elif args['<command>'] in ['help', None]:
        exit(call(['python', '-m', 'negbio.negbio_pipeline', '--help']))
    else:
        exit("%r is not a command. See 'help'." % args['<command>'])


if __name__ == '__main__':
    main()