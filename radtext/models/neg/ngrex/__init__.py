"""
A NgrexPattern is a tgrep-type pattern for matching node configurations in one of the Networkx 
structures. Unlike tgrep but like Unix grep, there is no pre-indexing of the data to be searched. 
Rather there is a linear scan through the graph where matches are sought.

A node/edge is represented by a set of attributes and their values contained by curly braces: 
`{attr1:value1;attr2:value2;...}`. Therefore, {} represents any node/edge in the graph. 
Attributes must be plain strings; values can be regular expressions blocked off by "/". 
(I think regular expressions must match the whole attribute value; so that /NN/ matches "NN" only, 
while /NN.* / matches "NN", "NNS", "NNP", etc.)
"""

from radtext.models.neg.ngrex.pattern import NgrexPattern, NgrexMatch
from . import parser
from . import pattern


def compile(ngrex: str) -> NgrexPattern:
    """
    Compiles the given expression into a pattern
    """
    p = parser.yacc.parse(ngrex)
    pattern.validate_names(p)
    return p
