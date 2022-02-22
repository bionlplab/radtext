# Named entity recognition

The named entity recognition (NER) module recognizes mention spans of a
particular entity type (e.g., abnormal findings) from the reports. In RadText,
NER is can be invoked by the name `ner`.

RadText provides two sub-modules for NER:

* The rule-based method uses regular expressions that combine information from
terminological resources and characteristics of the entities of interest.
They are manually constructed by domain experts.
* [**SpaCy's PhraseMatcher**](https://spacy.io/api/phrasematcher) provides another
way to efficiently match large terminology lists. RadText uses PhraseMatcher to
recognize concepts in the [RadLex ontology](http://radlex.org/).

| Name      | Annotator class name |
|-----------|----------------------|
| ner:regex | NerRegExExtractor    |
| ner:spacy | NerSpacyExtractor    |

**Example Usage**

```shell
$ radext-ner regex --phrase /path/to/patterns.yml -i /path/to/input.xml -o /path/to/output.xml
```

```shell
$ radext-ner spacy --radlex /path/to/Radlex4.1.xlsx -i /path/to/input.xml -o /path/to/output.xml
```