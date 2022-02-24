# Constituency Parsing

RadText uses the [Bllip parser](https://github.com/BLLIP/bllip-parser)
to obtain the parse tree. The Bllip parser was trained on the biomedical text.

## Options

| Option name   | Default                                   | Description             |
|:--------------|:------------------------------------------|:------------------------|
| --bllip_model | `$radtext/bllipparser/BLLIP-GENIA-PubMed` | Bllip parser model path |


## Example Usage

```shell
$ radext-parse -i /path/to/input.xml -o /path/to/output.xml
```

```python
from radtext.models.bllipparser import BioCParserBllip
processor = BioCParserBllip(model_dir=argv['--bllip_model'])
```