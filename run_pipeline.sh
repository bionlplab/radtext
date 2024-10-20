#export PYTHONPATH=$PYTHONPATH:src
SECTION_TITLES=resources/section_titles.txt
PHRASE=resources/cxr14_phrases_v2.yml
#RADLEX=resources/Radlex4.1.xlsx
#NGREX_PATTERN=resources/patterns/ngrex_patterns.yml
#REGEX_PATTERN=resources/patterns/regex_patterns.yml

while getopts i:o:d: flag
do
  case "${flag}" in
    i) input=${OPTARG};;
    o) output=${OPTARG};;
    d) top_dir=${OPTARG};;
    *)
  esac
done

if [ -z "$top_dir" ]; then
  top_dir=$(mktemp -d -t radtext-XXXXXXXXXX)
else
  [ -d $top_dir ] || mkdir $top_dir
fi

if [ -z "$input" ]; then
  echo "No input file"
fi

if [ -z "$output" ]; then
  echo "No output file"
fi

filename=$(basename -- "$output")
#extension="${filename##*.}"
filename="${filename%.*}"

if [ "$1" != "" ]; then
    echo "-- Download models --"
    radtext-download --all

    echo "-- CSV2BIOC --"
    # convert csv file to bioc format
    radtext-csv2bioc -i "$input" -o "$top_dir/$filename.xml"

    echo "-- De-identification --"
    radtext-deid -i "$top_dir/$filename.xml" -o "$top_dir/$filename.deid.xml"

    echo "-- Section split --"
    # section split - using regex
    radtext-secsplit regex --section-titles $SECTION_TITLES -i "$top_dir/$filename.deid.xml" -o "$top_dir/$filename.secsplit.xml"
    # section split - using medspacy
    #radtext-secsplit medspacy -i $top_dir/$filename.deid.xml -o $top_dir/$filename.secsplit.xml

    #radtext-preprocess

    echo "-- Sentence split --"
    radtext-ssplit -i "$top_dir/$filename.secsplit.xml" -o "$top_dir/$filename.ssplit.xml"

    echo "-- NER --"
    radtext-ner regex --phrase $PHRASE -i "$top_dir/$filename.ssplit.xml" -o "$top_dir/$filename.ner.xml"
    #radtext-ner spacy --radlex $RADLEX -i $top_dir/$filename.ssplit.xml -o $top_dir/$filename.ner.xml

    echo "-- Parse --"
    radtext-parse -i "$top_dir/$filename.ner.xml" -o "$top_dir/$filename.parse.xml"

    echo "-- Tree2dep --"
    # convert constituency tree to dependencies
    radtext-tree2dep -i "$top_dir/$filename.parse.xml" -o "$top_dir/$filename.depparse.xml"

    echo "-- NEG --"
    radtext-neg -i "$top_dir/$filename.depparse.xml" -o "$top_dir/$filename.neg.xml"

    echo "-- Collect labels --"
    radtext-collect --phrases $PHRASE -i "$top_dir/$filename.neg.xml" -o "$output"
fi


