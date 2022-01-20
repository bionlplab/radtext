import bioc
import docopt
import pandas as pd 
import tqdm
import json

class BioC2CDM:
	def convert(self, cdm_df, collection):
		nlp_date = collection.date

		for doc in tqdm.tqdm(collection.documents):
			nlp_system = None
			section_concept_id = None
			note_id = doc.id
			for passage in tqdm.tqdm(doc.passages, leave=False):
				if passage.infons != None:
					if 'title' in passage.infons:
						section_concept_id = passage.infons['title']

				for ann in passage.annotations:
					note_nlp_id, offset, lexical_variant, note_nlp_concept_id, \
					term_exists, term_temporal, term_modifiers = None, None, None, None, None, None, None 

					note_nlp_id = None
					for location in ann.locations:
						if location.offset != None:
							offset = location.offset
					lexical_variant = ann.text
					if 'preferred_name' in ann.infons:
						note_nlp_concept_id = ann.infons['preferred_name']
					if 'concept_id' in ann.infons:
						note_nlp_source_concept_id = ann.infons['concept_id']
					if 'negation' in ann.infons:
						term_exists = ann.infons['negation']
					if 'temporal' in ann.infons:
						term_temporal = ann.infons['temporal']
					if 'modifiers' in ann.infons:
						term_modifiers = ann.infons['modifiers']

					cdm_df = cdm_df.append({"note_id": note_id, \
						"note_nlp_id": note_nlp_id, \
						"offset": offset, \
						"lexical_variant": lexical_variant, \
						"note_nlp_concept_id": note_nlp_concept_id, \
						"nlp_date": nlp_date, \
						"section_concept_id": section_concept_id, \
						"note_nlp_source_concept_id": note_nlp_source_concept_id, \
						"nlp_system": nlp_system, \
						"term_exists": term_exists, \
						"term_temporal": term_temporal, \
						"term_modifiers": term_modifiers}, ignore_index=True)

		return cdm_df

class CDM2BioC:
	def convert(self, df):
		collection = bioc.BioCCollection()
		for idx, row in df.iterrows():
			text = row['note_text']
			note_id = row['note_id']

			if pd.isna(note_id) or pd.isna(text):
				continue

			doc = bioc.utils.as_document(text)
			doc.id = note_id
			collection.add_document(doc)
		return collection
