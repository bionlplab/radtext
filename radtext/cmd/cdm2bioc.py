"""
Convert OMOP CDM .csv file to the BioC output file.

Usage:
    cdm2bioc [options] -i FILE -o FILE

Options:
    -i FILE
    -o FILE
"""
import sys
sys.path.append('..')

import bioc
import docopt
import pandas as pd 

from radtext.bioc_cdm_converter import CDM2BioC

if __name__ == '__main__':
	argv = docopt.docopt(__doc__)

	df = pd.read_csv(argv['-i'], dtype=str)
	# initialize CDM2BioC converter
	cdm2bioc = CDM2BioC()
	# convert
	collection = cdm2bioc.convert(df)

	with open(argv['-o'], 'w') as fp:
		bioc.dump(collection, fp)