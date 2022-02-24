# Section Split

This module splits the report into sections. 
RadText provides two options for section split.

## secsplit:regex

The **rule-based method** uses a list of section titles to split the notes.

### Options

| Option name      | Default                          | Description            |
|:-----------------|:---------------------------------|:-----------------------|
| --section-titles | `$resources/section_titles.txt`  | List of section titles |

```shell
$ radtext-secsplit regex -i /path/to/input.xml -o /path/to/output.xml
```

```python
from radtext.models.section_split.section_split_regex import BioCSectionSplitterRegex, combine_patterns
with open(argv['--section-titles']) as fp:
    section_titles = [line.strip() for line in fp]
pattern = combine_patterns(section_titles)
processor = BioCSectionSplitterRegex(regex_pattern=pattern)
```

## secsplit:medspacy

[**MedSpaCy**](https://github.com/medspacy/medspacy) is a spaCy tool for performing
clinical NLP and text processing tasks.
It includes an implementation of clinical section detection based on rule-based
matching of the section titles with default rules adapted from
[SecTag](https://pubmed.ncbi.nlm.nih.gov/18999303/) and
expanded through practice.

```shell
$ radtext-secsplit medspacy -i /path/to/input.xml -o /path/to/output.xml
```

```python
import medspacy
from radtext.models.section_split.section_split_medspacy import BioCSectionSplitterMedSpacy
nlp = medspacy.load(enable=["sectionizer"])
processor = BioCSectionSplitterMedSpacy(nlp)
```
