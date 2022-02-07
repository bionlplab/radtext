import logging
import os


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
