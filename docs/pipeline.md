# Pipeline

In this section, we introduce in more detail the options of RadText's pipeline.

## De-identification

See [this doc](pipeline/deid.md)

## Section Split

See [this doc](pipeline/secsplit.md)

## Text preprocessing

See [this doc](pipeline/preprocess.md).

## Sentence Split

See [this doc](pipeline/ssplit.md).

## Constituency Parsing

See [this doc](pipeline/parse.md).

## Named Entity Recognition

See [this doc](pipeline/ner.md).

## Dependency Parsing

See [this doc](pipeline/depparse.md).

## Negation Detection

See [this doc](pipeline/neg.md).

## Labels Collection

The final step merges all the labels and produces the output .csv file.

```shell
$ python radtext/cmd/collect_neg_labels.py \
    --phrases /path/to/patterns.yml \
    -i /path/to/input.xml \
    -o /path/to/output_file.csv
```

