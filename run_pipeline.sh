#!/bin/bash

export PYTHONPATH=.

top_dir=$HOME/Documents/Github/radtext

# resources files
ner_phrase_file=$top_dir/resources/cxr14_phrases_v2.yml
phrase_file=$top_dir/resources/chexpert_phrases.yml

# intermediate output files
csv_file=$top_dir/example.csv 
bioc_file=$top_dir/bioc.xml
bioc_deid_file=$top_dir/Results/deid.xml
section_file=$top_dir/Results/section.xml
ud_file=$top_dir/Results/ud.xml
ner_file=$top_dir/Results/ner.xml
parse_file=$top_dir/Results/parse.xml
neg_file=$top_dir/Results/neg.xml
neg_csv_file=$top_dir/Results/output.csv


if [ -z "$1" ]
then
  echo "-- CSV 2 BioC --"
  python cmd/csv2bioc.py -i "$csv_file" -o "$bioc_file"

  echo "-- De-identification --"
  python cmd/deidentify.py -i "$bioc_file" -o "$bioc_deid_file"

  echo "-- Split section --"
  pip install medspacy
  python cmd/split_section.py medspacy -i "$bioc_deid_file" -o "$section_file"

  echo "-- Preprocess --"
  pip install -U pip setuptools wheel
  pip install -U spacy
  python -m spacy download en_core_web_sm
  python cmd/preprocess_pipeline.py spacy -i "$section_file" -o "$ud_file" --overwrite

  echo "-- Named entity recognition --"
  pip install intervaltree
  python cmd/ner.py regex --phrases "$ner_phrase_file" -i "$ud_file" -o "$ner_file" --overwrite

  echo "-- Dependency Parsing --"
  python cmd/parse.py spacy -i "$ner_file" -o "$parse_file"

  echo "-- Negation/Uncertainty detection --"
  python cmd/neg.py -i "$parse_file" -o "$neg_file" --overwrite

  echo "-- Collect negation/uncertainty detection --"
  python cmd/collect_neg_labels.py --phrases "$phrase_file" -i "$neg_file" -o "$neg_csv_file"

  echo "-- Complete --"

fi


while [ "$1" != "" ]; do
  case "$1" in
    'csv2bioc' )
      echo "-- CSV 2 BioC --"
      python cmd/csv2bioc.py -i "$csv_file" -o "$bioc_file"
      ;;
    'deid' )
      echo "-- De-identification --"
      python cmd/deidentify.py -i "$bioc_file" -o "$bioc_deid_file"
      ;;
    'split_section' )
      echo "-- Split section --"
      pip install medspacy
      python cmd/split_section.py medspacy -i "$bioc_deid_file" -o "$section_file"
      ;;
    'preprocess' )
      echo "-- Preprocess --"
      pip install -U pip setuptools wheel
      pip install -U spacy
      python -m spacy download en_core_web_sm
      python cmd/preprocess_pipeline.py spacy -i "$section_file" -o "$ud_file" --overwrite
      ;;
    'ner' )
      echo "-- Named entity recognition --"
      pip install intervaltree
      python cmd/ner.py regex --phrases "$ner_phrase_file" -i "$ud_file" -o "$ner_file" --overwrite
      ;;
    'parse' )
      echo "-- Dependency Parsing --"
      python cmd/parse.py spacy -i "$ner_file" -o "$parse_file"
      ;;
    'neg' )
      echo "-- Negation/Uncertainty detection --"
      python cmd/neg.py -i "$parse_file" -o "$neg_file" --overwrite
      ;;
    'collect_label' )
      echo "-- Collect negation/uncertainty detection --"
      python cmd/collect_neg_labels.py --phrases "$phrase_file" -i "$neg_file" -o "$neg_csv_file"
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done