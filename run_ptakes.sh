#!/bin/bash

export PYTHONPATH=.

source_dir=$HOME'/Subjects/ptakes'
venv_dir=$HOME'/Subjects/venvs/pengyifan-wcm'
top_dir=$HOME'/Data/ptakes_data/mimic-cxr'

disease=pneumoperitoneum
phrase_file=$top_dir/../${disease}.yml

prefix=reports
csv_file=$top_dir/$prefix.csv
bioc_file=$top_dir/$prefix.xml
section_file=$top_dir/${prefix}_section.xml
ud_file=$top_dir/${prefix}_ud.xml
ner_file=$top_dir/${prefix}_${disease}.xml
neg_file=$top_dir/${prefix}_${disease}_neg.xml
neg_csv_file=$top_dir/${prefix}_${disease}_neg.csv

cd "$source_dir" || exit
source "${venv_dir}/bin/activate"

while [ "$1" != "" ]; do
  case "$1" in
    'csv2bioc' )
      echo "CSV 2 BioC"
      python cmd/csv2bioc.py -i "$csv_file" -o "$bioc_file" --id_col subject_id --text_col text
      ;;
    'split_section' )
      echo "Split section"
      python cmd/split_section.py -i "$bioc_file" -o "$section_file"
      ;;
    'preprocess' )
      echo "Preprocess"
      python cmd/preprocess_pipeline.py spacy -i "$section_file" -o "$ud_file" --overwrite
      ;;
    'ner' )
      echo "Named entity recognition"
      python cmd/ner.py regex --phrases "$phrase_file" -i "$ud_file" -o "$ner_file" --overwrite
      ;;
    'neg' )
      echo "Negation/Uncertainty detection"
      python cmd/neg.py -i "$ner_file" -o "$neg_file" --overwrite
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
