"""
Convert OMOP CDM .csv file to the BioC output file.

Usage:
    cdm2bioc [options] -i FILE -o FILE

Options:
    -i FILE
    -o FILE
"""

import bioc
import docopt
import pandas as pd 

if __name__ == '__main__':
	argv = docopt.docopt(__doc__)

	df = pd.read_csv(argv['-i'], dtype=str)
	collection = bioc.BioCCollection()
	for idx, row in df.iterrows():
		text = row['note_text']
		note_id = row['note_id']

		if pd.isna(note_id) or pd.isna(text):
			continue

		doc = bioc.utils.as_document(text)
		doc.id = note_id
		collection.add_document(doc)

	with open(argv['-o'], 'w') as fp:
		bioc.dump(collection, fp)