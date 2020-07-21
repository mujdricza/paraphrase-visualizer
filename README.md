# paraphrase-visualizer
This script visualizes token sequences as a graphml graph in a form of
* a finite state automaton with one node per token; or
* a paraphrase graph.

The output graphml file can be displayed with a graphml viewer like [yED](https://www.yworks.com/products/yed). The output file does not contain any node positioning, thus the user can utilize the different layouts provided by the graphml viewer for the final graph representation.

# Requirements

* python>=3.7
* yaml

# Intro

The base for the output graph(s) is a list of sentences in a simple text file with one tokenized sentence per line.

In the output graph(s), the start and end tokens in the input sentences are marked.

The option `-e`/`--end_points` adds an artificial start and end token to the input sequences. Thus, the output graph is guaranteed to be a connected graph. Otherwise, also multiple (sub)graphs can be built according to the input sentences.

## Automaton graph generation

`src/automaton_graphml_builder.py <input_fn> [-o <output_dir>] [-e]`

This script generates (a) "finite state automaton" graph(s) from the input sentences. 

Note that from this automaton, you cannot exactly reconstruct the original sentences.

## Paraphrase graph generation

`src/paraphrase_graphml_builder.py <input_fn> [-o <output_dir>] [-e]`

This script generates (a) graph(s) from the input sentences.

# Contact

Eva Mujdricza-Maydt, me.levelek@gmx.de
