#!/bin/bash

export PYTHONPATH=.

top_dir=$HOME'/Results'

# resources files
ner_phrase_file=$top_dir$/resources/cxr14_phrases_v2.yml
phrase_file=$top_dir$/resources/chexpert_phrases.yml

# intermediate output files
csv_file=$top_dir/$input.csv 
bioc_file=$top_dir/$bioc.xml
bioc_deid_file=$top_dir/$deid.xml
section_file=$top_dir/$section.xml
ud_file=$top_dir/$ud.xml
ner_file=$top_dir/$ner.xml
parse_file=$top_dir/$parse.xml
neg_file=$top_dir/$neg.xml
neg_csv_file=$top_dir/$output.csv

while [ "$1" != "" ]; do
  case "$1" in
    'csv2bioc' )
      echo "CSV 2 BioC"
      python cmd/csv2bioc.py -i "$csv_file" -o "$bioc_file"
      ;;
    'deid' )
      echo "de identification"
      python cmd/deidentify.py -i "$bioc_file" -o "$bioc_deid_file"
      ;;
    'split_section' )
      echo "Split section"
      pip install medspacy
      python cmd/split_section.py medspacy -i "$bioc_deid_file" -o "$section_file"
      ;;
    'preprocess' )
      echo "Preprocess"
      pip install -U pip setuptools wheel
      pip install -U spacy
      python -m spacy download en_core_web_sm
      python cmd/preprocess_pipeline.py spacy -i "$section_file" -o "$ud_file" --overwrite
      ;;
    'ner' )
      echo "Named entity recognition"
      pip install intervaltree
      python cmd/ner.py regex --phrases "$ner_phrase_file" -i "$ud_file" -o "$ner_file" --overwrite
      ;;
    'parse' )
      echo "Dependency Parsing"
      python cmd/parse.py -i "$ner_file" -o "$parse_file"
      ;;
    'neg' )
      echo "Negation/Uncertainty detection"
      python cmd/neg.py -i "$parse_file" -o "$neg_file" --overwrite
      ;;
    'collect_neg_label' )
      echo "Collect negation/uncertainty detection"
      python cmd/collect_neg_labels.py --phrases "$phrase_file" -i "$neg_file" -o "$neg_csv_file"
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
