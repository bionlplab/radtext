# Dependency Parsing

Dependency Parsing is the process to analyze the grammatical structure in a
sentence and find out related words as well as the type of the relationship
between them.

RadText utilizes the Universal Dependency Graph
([UDG](https://universaldependencies.org/)) to describe the grammatical
relationships in a sentence. UDG is a directed graph, which represents all
universal dependency information in a sentence. The vertices in a UDG represent
the information such as the word, part-of-speech and the word lemma.
The edges in a UDG represent the typed dependencies from the governor to its
dependent and are labeled with the corresponding dependency type. UDG
effectively represents the syntactic head of each word in a
sentence and the dependency relation between words.

* **spaCy**: See `Text preprocessing` > `spaCy`
* **Stanza**: See `Text preprocessing` > `Stanza` 
* **Bllip**: RadText obtains the universal dependencies by applying the 
[Stanford dependency converter](https://github.com/dmcc/PyStanfordDependencies) 
with the `CCProcessed` and `Universal` option. 

## Example Usage

```shell
$ radext-tree2dep -i /path/to/input.xml -o /path/to/output.xml
```

```python
from radtext.models.tree2dep import BioCPtb2DepConverter
converter = BioCPtb2DepConverter()
```