# Negation Detection

For negation detection, RadText employs
[NegBio](https://github.com/bionlplab/negbio2), which utilizes universal
dependencies for pattern definition and subgraph matching for graph traversal
search so that the scope for negation/uncertainty is not limited to the fixed
word distance.

## Options

| Option name      | Default                                  | Description                      |
|:-----------------|:-----------------------------------------|:---------------------------------|
| --regex_patterns | `$resources/patterns/regex_patterns.yml` | Regular expression patterns      |
| --ngrex_patterns | `$resources/patterns/ngrex_patterns.yml` | Nregex-based expression patterns |
| --sort_anns      | `False`                                  | Sort annotations by its location |

## Example Usage

```shell
$ radext-neg -i /path/to/input.xml -o /path/to/output.xml
```

```python
from radtext.models.neg.match_ngrex import NegGrexPatterns
from radtext.models.neg import NegRegexPatterns
from radtext.models.neg import NegCleanUp
from radtext.models.neg.neg import BioCNeg

regex_actor = NegRegexPatterns()
regex_actor.load_yml2(argv['--regex_patterns'])
ngrex_actor = NegGrexPatterns()
ngrex_actor.load_yml2(argv['--ngrex_patterns'])
neg_actor = BioCNeg(regex_actor=regex_actor, ngrex_actor=ngrex_actor)
cleanup_actor = NegCleanUp(argv['--sort_anns'])
```

## Nregex

A Nregex pattern is a regular expression-like pattern that is designed to match node and edge configurations within a
graph. The Nregex pattern allows matching on the attributes of nodes (e.g., lemma) and edges (e.g., dependency type). 
The Nregex follows [Semgrex](https://nlp.stanford.edu/software/tregex.shtml) but only supports "immediate domination"
operations (`>` and`<`).

```{warning}
Like Tregex, there is no pre-indexing of the data to be searched. Rather there is a linear scan through the all nodes in
the graph. As a result, matching is **slower**.
```

### Nodes and relations

A node or relation is represented by a set of attributes and their values contained by curly braces:
`{attr1:value1;attr2:value2;...}`. `{}` represents any node in the graph. Attributes must be plain strings;
values can ONLY be regular expressions blocked off by "`/`". Regular expressions must match the whole attribute
value. For example, `{lemma:/structure/}` matches any nodes with "structure" as their lemma, while
`{lemma:/structure.*/}` matches "structure" and "structures".

```{warning}
Currently, supported node attribute is `lemma`. Supported relation attribute is `dependency`.
```

### Nregex pattern language

| Symbol          | Meaning                                      |
|:----------------|:---------------------------------------------|
| A <reln B       | A is the dependent of a relation reln with B |
| A >reln B       | A is the governor of a relation reln with B  |

### Boolean relational operators

Relations can be combined using the '&' and '|' operators

### Naming nodes

Nodes can be given names (a.k.a. handles) using '='. A named node will be stored in a map that maps names to nodes so
that if a match is found, the node corresponding to the named node can be extracted from the map. For example,
`{lemma:/no/}=k2` will match a node with lemma "no" and assign the name "k2". After a match is found, the map can be
queried with the name to retrieved the matched node using `match.node('k2')`
