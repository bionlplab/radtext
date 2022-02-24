# Named entity recognition

The named entity recognition (NER) module recognizes mention spans of a
particular entity type (e.g., abnormal findings) from the reports.
RadText provides two sub-modules for NER.

## ner:regex

The rule-based method uses regular expressions that combine information from
terminological resources and characteristics of the entities of interest.
They are manually constructed by domain experts.

### Options

| Option name | Default                           | Description     |
|:------------|:----------------------------------|:----------------|
| --phrase    | `$resources/cxr14_phrases_v2.yml` | Phrase patterns |


### Example Usage

```shell
$ radext-ner regex --phrase /path/to/patterns.yml -i /path/to/input.xml -o /path/to/output.xml
```

```python
from pathlib import Path
from radtext.models.ner.ner_regex import NerRegExExtractor, BioCNerRegex
from radtext.cmd.ner import load_yml

patterns = load_yml(argv['--phrases'])
extractor = NerRegExExtractor(patterns)
processor = BioCNerRegex(extractor, name=Path(argv['--phrases']).stem)
```

### Phrase patterns

The pattern file is in the [yaml](https://yaml.org/) format. It contains a list of concepts where the key serves as the
preferred name. Each concept should contain three attributes: `concept_id`, `include`, and
`exclude`. 
`include` contains the regular expressions that the concept will match.
`exclude` contains the regular expressions that the concept will not match, even if its substring will match the regular
expressions in the `include`

Using the following example, RadText will recognize "emphysema", but reject "subcutaneous emphysema" though "emphysema"
is part of "subcutaneous emphysema".

```yaml
Emphysema:
  concept_id: RID4799
  include:
    - emphysema
  exclude:
    - subcutaneous emphysema
```

## ner:spacy

* [**SpaCy's PhraseMatcher**](https://spacy.io/api/phrasematcher) provides another
way to efficiently match large terminology lists. RadText uses PhraseMatcher to
recognize concepts in the [RadLex ontology](http://radlex.org/).

### Options

| Option name   | Default                            | Description              |
|:--------------|:-----------------------------------|:-------------------------|
| --radlex      | `$resources/Radlex4.1.xlsx`        | The RadLex ontology file |
| --spacy-model | `en_core_web_sm`                   | The spaCy model          |


### Example Usage

```shell
$ radext-ner spacy --radlex /path/to/Radlex4.1.xlsx -i /path/to/input.xml -o /path/to/output.xml
```

```python
import spacy
from radtext.models.ner.ner_spacy import NerSpacyExtractor, BioCNerSpacy
from radtext.models.ner.radlex import RadLex4

nlp = spacy.load(argv['--spacy-model'], exclude=['ner', 'parser', 'senter'])
radlex = RadLex4(argv['--radlex'])
matchers = radlex.get_spacy_matchers(nlp)
extractor = NerSpacyExtractor(nlp, matchers)
processor = BioCNerSpacy(extractor, 'RadLex')
```
