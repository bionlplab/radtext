#export PYTHONPATH=$PYTHONPATH:src

PHRASE=radtext/resources/chexpert_phrases.yml
NGREX_PATTERN=radtext/resources/patterns/ngrex_patterns.yml
REGEX_PATTERN=radtext/resources/patterns/regex_patterns.yml

while getopts i:o:d: flag
do
  case "${flag}" in
    i) input=${OPTARG};;
    o) output=${OPTARG};;
    d) top_dir=${OPTARG};;
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
extension="${filename##*.}"
filename="${filename%.*}"

# download models
radtext-download all
# ner
radtext-ner regex --phrase $PHRASE -i $input -o $top_dir/$filename.ner.xml
# ssplit
radtext-ssplit -i $top_dir/$filename.ner.xml -o $top_dir/$filename.ssplit.xml
# parse
radtext-parse -i $top_dir/$filename.ssplit.xml -o $top_dir/$filename.bllip.xml
# convert constituency tree to dependencies
radtext-tree2dep -i $top_dir/$filename.bllip.xml -o $top_dir/$filename.depparse.xml
# neg
radtext-neg --ngrex_negation $NGREX_PATTERN --regex_patterns $REGEX_PATTERN -i $top_dir/$filename.depparse.xml -o $output
