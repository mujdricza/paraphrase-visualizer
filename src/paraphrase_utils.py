#!/usr/bin/env python3.8

"""
Util collection for the paraphrase_graphml_builder.py script.

"""

__author__ = "Eva Mujdricza-Maydt"
__version__ = "20200410"

from typing import List, Dict, Any
from enum import Enum
import os
import yaml

from paraphrase_Node import Node
from paraphrase_Token import Token


def get_config(config_fn: str) -> Dict:
    assert os.path.exists(config_fn), f"Config file '{config_fn}' not available."
    with open(config_fn) as f:
        return yaml.load(stream=f, Loader=yaml.Loader)


class FORMAT(Enum):
    """Names (keys) in the config file"""
    START_TOKEN = "START_TOKEN"
    END_TOKEN = "END_TOKEN"

    COLOR_GENERAL = "COLOR_GENERAL"
    COLOR_START = "COLOR_START"
    COLOR_END = "COLOR_END"

    NL = "NL"
    CHARACTER_WIDTH = "CHARACTER_WIDTH"



class GRAPHML(Enum):
    HEADER = """<?xml version="1.0" encoding="UTF-8"?>"""
    GRAPHML_START = """
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
<!-- keys for YEd -->
<key for="node" id="yednode" yfiles.type="nodegraphics"/>
<key for="edge" id="yededge" yfiles.type="edgegraphics"/>

<!-- keys for graph -->

<!-- keys for node -->

<!-- keys for port -->

<!-- keys for edge -->
"""

    GRAPHML_END = "</graphml>"
    GRAPH_START_STRF = """<graph edgedefault="directed" id="{}">"""
    GRAPH_END = "</graph>"
    NODE_STRF = """<node id="{}">
      <data key="yednode">
        <y:ShapeNode>
          <y:Geometry height="30.0" width="{}" />
          <y:Fill color="{}" transparent="false"/>
          <y:NodeLabel fontFamily="Consolas" fontSize="12"{}>{}</y:NodeLabel>
          <y:Shape type="roundrectangle"/>
        </y:ShapeNode>
      </data>
</node>
""" # id, width, color, line_color, label

    EDGE_STRF = """<edge id="{}" source="{}" target="{}">
      <data key="yededge">
        <y:PolyLineEdge>
          <y:LineStyle color="#000000" type="line" width="1.0"/>
          <y:Arrows source="none" target="standard"/>
        </y:PolyLineEdge>
      </data>
</edge>
""" # id, from, to




def read_sentences(filename: str, config, add_start_and_end_points:bool) -> List[str]:

    with open(filename) as f:
        sentences = [line.strip() for line in f.readlines() if line.strip()]
    
    tokenized_sentences = []
    for sentence in sentences:
        tokenized_sentence = sentence.split()
        if add_start_and_end_points:
            
            start_token = config[FORMAT.START_TOKEN.value]
            tokenized_sentence.insert(0, start_token)
            end_token = config[FORMAT.END_TOKEN.value]
            tokenized_sentence.append(end_token)
        tokenized_sentences.append(tokenized_sentence)
    
    return tokenized_sentences
    

def escape_text(token):
    """In xml, some characters are not allowed for a text node. Escape them."""
    
    token = token.replace("&", "&amp;")
    token = token.replace("<", "&lt;")
    token = token.replace(">", "&gt;")
    token = token.replace('"', "&quot;")
    token = token.replace("'", "&apos;")
    return token


def _get_width(token:str, config:Dict[str, Any]) -> float:

    return float(2*3 + len(token)*config[FORMAT.CHARACTER_WIDTH.value])


# def _get_background_color(token:str, config:Dict[str, Any]) -> str:
#
#     if token.startswith(config[FORMAT.START_TOKEN.value]):
#         return config[FORMAT.COLOR_START.value]
#     elif token.endswith(config[FORMAT.END_TOKEN.value]):
#         return config[FORMAT.COLOR_END.value]
#     return config[FORMAT.COLOR_GENERAL.value]


def _get_background_color(node:Node, config:Dict[str, Any]) -> str:
    
    if node.has_start_token():
        return config[FORMAT.COLOR_START.value]
    elif node.has_end_token():  # NOTE that start token marking is prioritized
        return config[FORMAT.COLOR_END.value]
    return config[FORMAT.COLOR_GENERAL.value]


def _get_double_frame(node:Node) -> str:
    
    if node.has_end_token():
        return ' hasLineColor="true" lineColor="#000000"'
    return ''


def _format_node(node_obj, config:Dict[str, Any]):
    token_word = node_obj.token_word
    escaped_token_word = escape_text(token_word)
    escaped_node_id = escape_text(node_obj.node_id)
    
    return GRAPHML.NODE_STRF.value.format(
        escaped_node_id,
        _get_width(token_word, config),
        _get_background_color(node_obj, config),
        _get_double_frame(node_obj),
        escaped_token_word
    )


def _format_edge(source_node_id, target_node_id):
    
    escaped_sni = escape_text(source_node_id)
    escaped_tni = escape_text(target_node_id)
    return GRAPHML.EDGE_STRF.value.format(
        f"id_{escaped_sni}_{escaped_tni}_edge",
        escaped_sni,
        escaped_tni
    )


def write_graphml(node_dict: Dict[str, Node], config:Dict[str, Any], graphml_output_filename: str) -> None:
    
    with open(graphml_output_filename, "w") as f:
        f.write(GRAPHML.HEADER.value)
        f.write(os.linesep)
        f.write(GRAPHML.GRAPHML_START.value)
        f.write(os.linesep)
        f.write(GRAPHML.GRAPH_START_STRF.value.format(graphml_output_filename))
        f.write(os.linesep)

        # nodes
        node_ids = set(node_dict.keys())
        for node_id, node_obj in node_dict.items():
            f.write(_format_node(node_obj, config))
            f.write(os.linesep)

        # edges: write only outgoing edges!!!
        for curr_node_id, node_obj in node_dict.items():

            for outgoing_node_id in node_obj.outgoing_node_ids:
                if outgoing_node_id not in node_ids:
                    nd = '\n'.join([str(item) for id, item in node_dict.items()])
                    msg = f"Outgoing node id '{outgoing_node_id}' requested by node {node_obj} not in the graph!\n{nd}"
                    raise ValueError(msg)
                f.write(_format_edge(curr_node_id, outgoing_node_id))
                f.write(os.linesep)

        f.write(GRAPHML.GRAPH_END.value)
        f.write(os.linesep)
        f.write(GRAPHML.GRAPHML_END.value)

