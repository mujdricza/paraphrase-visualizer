#!/usr/bin/env python3.8

"""
This script just build a deterministic finite automaton from input sentence tokens.
(Simple version.)

Note that from this automaton, you cannot exactly reconstruct the original sentences.
"""

__author__ = "Eva Mujdricza-Maydt"
__version__ = "20200410"

import logging
import os
import sys
from typing import List, Any, Dict

from __init__ import logger
from paraphrase_graphml_builder import get_arguments
from paraphrase_utils import GRAPHML, FORMAT, \
    get_config, escape_text, read_sentences, _get_width



def build_graphml_automaton(input_filename:str, config:Dict[str, Any], end_points:bool) -> None:
    
    tokenized_sentences = read_sentences(input_filename, config, end_points)
    nodes = _generate_nodes(tokenized_sentences, config)
    edges = _generate_edges(tokenized_sentences)
    
    return nodes, edges


def write_graphml(nodes, edges, graphml_output_filename: str) -> None:
    with open(graphml_output_filename, "w") as f:
        f.write(GRAPHML.HEADER.value)
        f.write(os.linesep)
        f.write(GRAPHML.GRAPHML_START.value)
        f.write(os.linesep)
        f.write(GRAPHML.GRAPH_START_STRF.value.format(graphml_output_filename))
        f.write(os.linesep)

        # nodes
        for node in nodes:
            f.write(node)
            f.write(os.linesep)

        # edges
        for edge in edges:
            f.write(edge)
            f.write(os.linesep)

        f.write(GRAPHML.GRAPH_END.value)
        f.write(os.linesep)
        f.write(GRAPHML.GRAPHML_END.value)


def __get_background_color(token:str, start_tokens, end_tokens, config:Dict[str, Any]) -> str:

    if token in start_tokens:
        return config[FORMAT.COLOR_START.value]
    elif token in end_tokens:
        return config[FORMAT.COLOR_END.value]
    return config[FORMAT.COLOR_GENERAL.value]


def __get_double_frame(token_word, end_tokens) -> str:
    
    if token_word in end_tokens:
        return ' hasLineColor="true" lineColor="#000000"'
    return ''


def _generate_nodes(data_tokenized:List[List[str]], config:Dict[str,Any]) -> List[str]:

    nodes = []
    start_tokens = []
    end_tokens = []

    for tokens in data_tokenized:
        for idx, token in enumerate(tokens):
            if idx == 0 and token not in start_tokens:
                start_tokens.append(token)
            if idx == len(tokens)-1 and token not in end_tokens:
                end_tokens.append(token)
                
            escaped_token = escape_text(token)
            node = GRAPHML.NODE_STRF.value.format(
                "id_" + escaped_token,
                str(_get_width(token, config)),
                __get_background_color(token, start_tokens, end_tokens, config),
                __get_double_frame(token, end_tokens),
                escaped_token
            )
            nodes.append(node)
    
    return nodes
    
    
def _generate_edges(data_tokenized):
    edges = []

    for s_id, tokens in enumerate(data_tokenized):
        for i in range(len(tokens) - 1):
            token_i = "id_" + escape_text(tokens[i])
            token_j = "id_" + escape_text(tokens[i+1])
            edge = GRAPHML.EDGE_STRF.value.format(
                f"id_s{s_id}_f{i}_t{i+1}",
                token_i,
                token_j
            )
            edges.append(edge)

    return edges


def main():

    args = get_arguments(sys.argv)
    
    config_fn = args.config
    config = get_config(config_fn)
    
    input_fn = args.input_filename
    
    
    end_points = args.end_points
    ep = " with additional start/end points" if end_points else ""
    logger.info(f"Reading sentences from '{input_fn}'{ep}.")
    
    output_dir = args.output_dir if args.output_dir else os.path.dirname(os.path.realpath(input_fn))
    os.makedirs(output_dir, exist_ok=True)
    ep = "_we" if end_points else ""
    output_fn = os.path.join(output_dir, os.path.splitext(os.path.basename(input_fn))[0] + ep + "_fsa.graphml")
    
    nodes, edges = build_graphml_automaton(input_fn, config, end_points)
    logger.info(f"Automaton graph with {len(nodes)} nodes and {len(edges)} edges built.")
    write_graphml(nodes, edges, output_fn)
    logger.info(f"See output in '{output_fn}'.")

if __name__ == "__main__":
    main()

