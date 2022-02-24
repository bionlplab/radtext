# Sentence Split

This module splits the report into sentences using
[NLTK](https://www.nltk.org/api/nltk.tokenize.html).

## Options

| Option name  | Default  | Description                                   |
|:-------------|:---------|:----------------------------------------------|
| --newline    | `False`  | Whether to treat newlines as sentence breaks. |

## Example Usage

```shell
$ radtext-ssplit -i /path/to/input.xml -o /path/to/output.xml
```

```python
from radtext.models.sentence_split_nltk import BioCSSplitterNLTK
processor = BioCSSplitterNLTK(newline=argv['--newline'])
```