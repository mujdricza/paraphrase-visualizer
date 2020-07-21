#!/usr/bin/env python3.8

"""
<?xml version="1.0" encoding="UTF-8"?>

<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
<!-- keys for YEd -->
<key for="node" id="yednode" yfiles.type="nodegraphics"/>
<key for="edge" id="yededge" yfiles.type="edgegraphics"/>

<!-- keys for graph -->

<!-- keys for node -->

<!-- keys for port -->

<!-- keys for edge -->

<graph edgedefault="directed" id="G">
<node id="s51874">
      <data key="yednode">
        <y:ShapeNode>
          <y:Fill color="#FFFF66" transparent="false"/>
          <y:NodeLabel>s51874<y:LabelModel>
            </y:LabelModel>
          </y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
</node>
<node id="s51869">
      <data key="yednode">
        <y:ShapeNode>
          <y:Geometry height="30.0" width="{}" />
          <y:Fill color="#FF6666" transparent="false"/>
          <y:NodeLabel>s51869<y:LabelModel>
            </y:LabelModel>
          </y:NodeLabel>
          <y:Shape type="roundrectangle"/>
        </y:ShapeNode>
      </data>
</node>
...
<edge id="s83705s83704" source="s83705" target="s83704">
      <data key="yededge">
        <y:PolyLineEdge>
          <y:LineStyle color="#00FF00" type="line" width="1.0"/>
          <y:Arrows source="none" target="standard"/>
        </y:PolyLineEdge>
      </data>
</edge>
<edge id="s84532s52164" source="s84532" target="s52164">
      <data key="yededge">
        <y:PolyLineEdge>
          <y:LineStyle color="#00FF00" type="line" width="1.0"/>
          <y:Arrows source="none" target="standard"/>
        </y:PolyLineEdge>
      </data>
</edge>
</graph>
</graphml>


- weighting edges according to transition occurrence
- coloring (weighting) nodes according to token occurrence
- mark start and end nodes

second idea:
- represent Token:
  * sentence_id
  * token_id
  * token_word
  * is_start_token
  * is_end_token
  * node_id (in the graph)
- make an artificial START and END token
- make a list of node chains - one chain for each sentence
- merge START nodes
- merge END nodes
- while there is a change in the graph:
    change = no
    for all nodes in the graph
      for all occurrences of the token in the current node in the graph:
        if occurrence > 1 with different node ids:
          collect incoming node chains upto the start
          if two incoming node chains are the same:
            merge the current node and the other node with the same token to one node
            change = yes
          collect outgoing node chains upto the end
          if two outgoing node chains are the same:
            merge the outgoing node and the other outgoing one with the same tokens to one node
            change = yes
    update nodes

"""
from __init__ import logger
import argparse
import logging
from typing import List, Tuple, Dict
import sys
import os

from paraphrase_Token import Token
from paraphrase_Node import Node
from paraphrase_utils import GRAPHML, FORMAT, get_config, write_graphml, read_sentences


def get_arguments(args:List[str]) -> argparse.Namespace:
    
    parser = argparse.ArgumentParser(description="Paraphrase graph builder (graphml).")
    parser.add_argument("input_filename", type=str,
                        help="Input filename with one tokenized sentence per line.")
    parser.add_argument("-o", "--output_dir", type=str,
                        help="Output directory for the output graphml file. "
                             "If not set, the graphml will be written in the folder of the input file.")
    parser.add_argument("-c", "--config", type=str,
                        default=os.path.join(os.path.dirname(__file__), "config.yaml"), dest="config",
                        help="Configuration file.")
    parser.add_argument("-e", "--end_points", action="store_true",
                        help="If set, additional 'start' and 'end' nodes will be added to the graph "
                             "which connect all first and last tokens in the sequences. "
                             "Thus, the output graph is garanteed to be connected.")
    
    return parser.parse_args(args[1:])  # since the zeroth arg is the script name itself


def _generate_tokens(tokenized_sentences: List[List[str]]) -> Dict[int, Dict[int, Token]]:

    token_object_dict = {}
    for sent_idx, tokens in enumerate(tokenized_sentences):
        sent_len = len(tokens)
        token_object_dict[sent_idx] = {}
        for tok_idx, token in enumerate(tokens):
            is_start_token = True if tok_idx == 0 else False
            is_end_token = True if tok_idx == sent_len-1 else False
            curr_token = Token(sent_idx, tok_idx, token, is_start_token, is_end_token)
            token_object_dict[sent_idx][tok_idx] = curr_token

    return token_object_dict


def _generate_nodes(tokens: Dict[int, Dict[int, Token]]) -> List[Node]:

    node_object_dict = {}

    # first, just make all nodes
    for sent_idx, tokidx2tok_dict in sorted(tokens.items()):

        for tok_idx, token_obj in sorted(tokidx2tok_dict.items()):

            node_id = f"id_s{sent_idx}_t{tok_idx}_node"
            curr_node = Node(node_id, token_obj)
            token_obj.node_id = node_id
            node_object_dict[node_id] = curr_node

    # link all nodes within the sentences
    for sent_idx, tokidx2tok_dict in sorted(tokens.items()):

        for tok_idx, token_obj in sorted(tokidx2tok_dict.items()):
            curr_node_id = token_obj.node_id

            if not token_obj.is_start_token:
                previous_token = tokidx2tok_dict[tok_idx-1]
                node_id_to_previous_token = previous_token.node_id
                node_object_dict[curr_node_id].add_incoming_node_id(node_id_to_previous_token)
                node_object_dict[node_id_to_previous_token].add_outgoing_node_id(curr_node_id)

    return node_object_dict


# def _generate_nodes(tokens: Dict[int, Dict[int, Token]], start_node, end_node) -> List[Node]:
#
#
#     node_object_dict = {}
#     # first, just make all nodes
#     for sent_idx, tokidx2tok_dict in sorted(tokens.items()):
#
#         for tok_idx, token_obj in sorted(tokidx2tok_dict.items()):
#
#             node_id = f"id_s{sent_idx}_t{tok_idx}_node"
#
#             curr_node = Node(node_id, token_obj.token_word)
#             token_obj.node_id = node_id
#
#             node_object_dict[node_id] = curr_node
#
#     # link all nodes within the sentences, and to the start and end nodes
#     for sent_idx, tokidx2tok_dict in sorted(tokens.items()):
#
#         for tok_idx, token_obj in sorted(tokidx2tok_dict.items()):
#             curr_node_id = token_obj.node_id
#             curr_is_start_token = token_obj.is_start_token
#             curr_is_end_token = token_obj.is_end_token
#
#             if curr_is_start_token is True:
#                 node_object_dict[curr_node_id].add_incoming_node_id(start_node.node_id)
#                 start_node.add_outgoing_node_id(curr_node_id)
#             else:
#                 previous_token = tokidx2tok_dict[tok_idx-1]
#                 node_id_to_previous_token = previous_token.node_id
#                 node_object_dict[curr_node_id].add_incoming_node_id(node_id_to_previous_token)
#                 node_object_dict[node_id_to_previous_token].add_outgoing_node_id(curr_node_id)
#
#             if curr_is_end_token is True:
#                 node_object_dict[curr_node_id].add_outgoing_node_id(end_node.node_id)
#                 end_node.add_incoming_node_id(curr_node_id)
#
#     # add start and end node to the collection, too
#     node_object_dict[start_node.node_id] = start_node
#     node_object_dict[end_node.node_id] = end_node
#
#     return node_object_dict


# def _generate_start_and_end_nodes(config) -> Tuple[Node]:
#     start_node = Node("id_START_NODE", config[FORMAT.START_TOKEN.value])
#     end_node = Node("id_END_NODE", config[FORMAT.END_TOKEN.value])
#
#     return start_node, end_node


def _get_node_id_list_with_token_word(curr_token_word:str, curr_node_id:str, node_dict: Dict[str, Node]) -> List[str]:

    node_id_list_with_token_word = []

    for node_id, node_obj in node_dict.items():
        if node_id == curr_node_id:
            continue
        if curr_token_word == node_obj.token_word:
            node_id_list_with_token_word.append(node_id)

    return node_id_list_with_token_word


def _get_incoming_node_id_chains(node_id: str, node_dict: Dict[str, Node]) -> List[List[str]]:

    incoming_node_id_chains = __get_incoming_node_id_chains(node_id, [[]], node_dict)

    return incoming_node_id_chains


def __get_incoming_node_id_chains(curr_node_id:str, curr_node_lists: List, node_dict:Dict[str, Node]) -> List[List[str]]:

    for node_list in curr_node_lists:
        node_list.append(curr_node_id)
    incoming_node_ids = node_dict[curr_node_id].incoming_node_ids
    for incoming_node_id in incoming_node_ids:
        return __get_incoming_node_id_chains(incoming_node_id, curr_node_lists, node_dict)

    return curr_node_lists


def _get_incoming_current_chain(curr_node_id, node_dict):
    curr_incoming_node_id_chain = _get_incoming_node_id_chains(curr_node_id, node_dict)[0]
    curr_incoming_word_chain = [node_dict[nid].token_word for nid in curr_incoming_node_id_chain]
    return curr_incoming_word_chain


def _get_incoming_candidate_chains(node_id_list_with_curr_token_word, node_dict):
    cand_incoming_word_chains = []
    for node_id_with_curr_word in node_id_list_with_curr_token_word:
        cand_node_id_chain_list = _get_incoming_node_id_chains(node_id_with_curr_word, node_dict)
        for cand_node_id_chain in cand_node_id_chain_list:
            cand_word_chain = [node_dict[nid].token_word for nid in cand_node_id_chain]
            cand_incoming_word_chains.append(cand_word_chain)
    return cand_incoming_word_chains


def _get_outgoing_node_id_chains(node_id: str, node_dict: Dict[str, Node]) -> List[List[str]]:

    outgoing_node_id_chains = __get_outgoing_node_id_chains(node_id, [[]], node_dict)
    return outgoing_node_id_chains


def __get_outgoing_node_id_chains(curr_node_id:str, curr_node_lists: List, node_dict:Dict[str, Node]) -> List[List[str]]:

    for node_list in curr_node_lists:
        node_list.append(curr_node_id)
    outgoing_node_ids = node_dict[curr_node_id].outgoing_node_ids
    for outgoing_node_id in outgoing_node_ids:
        return __get_outgoing_node_id_chains(outgoing_node_id, curr_node_lists, node_dict)

    return curr_node_lists


def _get_outgoing_current_chain(curr_node_id, node_dict):
    curr_outgoing_node_id_chain = _get_outgoing_node_id_chains(curr_node_id, node_dict)[0]
    curr_outgoing_word_chain = [node_dict[nid].token_word for nid in curr_outgoing_node_id_chain]
    return curr_outgoing_word_chain


def _get_outgoing_candidate_chains(node_id_list_with_curr_token_word, node_dict):
    cand_outgoing_word_chains = []
    for node_id_with_curr_word in node_id_list_with_curr_token_word:
        cand_node_id_chain_list = _get_outgoing_node_id_chains(node_id_with_curr_word, node_dict)
        for cand_node_id_chain in cand_node_id_chain_list:
            cand_word_chain = [node_dict[nid].token_word for nid in cand_node_id_chain]
            cand_outgoing_word_chains.append(cand_word_chain)
    return cand_outgoing_word_chains


def merge_graph_2_paraphrases(node_dict: Dict[str, Node]) -> Dict[str, Node]:

    single_node_token_words = []

    is_graph_changed = True
    while is_graph_changed is True:
        is_graph_changed = False
        if len(node_dict)%50 == 0:
            logger.info(f"- merging turn with {len(node_dict)} nodes")

        for curr_node_id, curr_node_obj in node_dict.items():
            curr_token_word = curr_node_obj.token_word
            if curr_token_word in single_node_token_words:
                continue
            node_id_list_with_curr_token_word = _get_node_id_list_with_token_word(curr_token_word, curr_node_id,
                                                                                  node_dict)
            if len(node_id_list_with_curr_token_word) < 1:
                single_node_token_words.append(curr_token_word)
            else:
                is_graph_changed = _changing_match(curr_node_obj, node_id_list_with_curr_token_word, node_dict,
                                                   "incoming")
                if is_graph_changed is True:
                    break

                is_graph_changed = _changing_match(curr_node_obj, node_id_list_with_curr_token_word, node_dict,
                                                   "outgoing")
                if is_graph_changed is True:
                    break
            if is_graph_changed:
                break

    return node_dict


def _changing_match(curr_node_obj, node_id_list_with_curr_token_word, node_dict, direction:str):
    curr_node_id = curr_node_obj.node_id
    if direction == "incoming":
        curr_word_chain = _get_incoming_current_chain(curr_node_id, node_dict)
        cand_word_chains = _get_incoming_candidate_chains(node_id_list_with_curr_token_word, node_dict)
    elif direction == "outgoing":
        curr_word_chain = _get_outgoing_current_chain(curr_node_id, node_dict)
        cand_word_chains = _get_outgoing_candidate_chains(node_id_list_with_curr_token_word, node_dict)
    else:
        raise ValueError
    
    is_graph_changed = False
    for node_id_with_curr_word, cand_word_chain in \
        zip(node_id_list_with_curr_token_word, cand_word_chains):
        if curr_word_chain == cand_word_chain:
            __merge_node(curr_node_obj, node_id_with_curr_word, node_dict)
            is_graph_changed = True
            break
    return is_graph_changed


def __merge_node(curr_node_obj, node_id_with_curr_word, node_dict):
    
    curr_node_id = curr_node_obj.node_id
    incoming_node_ids_for_cand = node_dict[node_id_with_curr_word].incoming_node_ids
    for incoming_node_id in incoming_node_ids_for_cand:
        if incoming_node_id not in curr_node_obj.incoming_node_ids:
            curr_node_obj.add_incoming_node_id(incoming_node_id)
        if curr_node_id not in node_dict[incoming_node_id].outgoing_node_ids:
            node_dict[incoming_node_id].outgoing_node_ids.append(curr_node_id)
        node_dict[incoming_node_id].del_outgoing_node_id(node_id_with_curr_word)

    outgoing_node_ids_for_cand = node_dict[node_id_with_curr_word].outgoing_node_ids
    for outgoing_node_id in outgoing_node_ids_for_cand:
        if outgoing_node_id not in curr_node_obj.outgoing_node_ids:
            curr_node_obj.add_outgoing_node_id(outgoing_node_id)
        if curr_node_id not in node_dict[outgoing_node_id].incoming_node_ids:
            node_dict[outgoing_node_id].add_incoming_node_id(curr_node_id)
        node_dict[outgoing_node_id].del_incoming_node_id(node_id_with_curr_word)
    
    for token in node_dict[node_id_with_curr_word].token_objects:
        curr_node_obj.token_objects.append(token)
    del node_dict[node_id_with_curr_word]


def build_initial_graph(sentence_list:List[List[str]]) -> Dict[str, Node]:
    
    token_dict = _generate_tokens(sentence_list)
    node_dict = _generate_nodes(token_dict)
    return node_dict


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
    output_fn = os.path.join(output_dir, os.path.splitext(os.path.basename(input_fn))[0] + ep + "_prp.graphml")
    
    tokenized_sentences = read_sentences(input_fn, config, end_points)
    initial_node_dict = build_initial_graph(tokenized_sentences)
    
    # make the paraphrases !
    logger.info(f"Initial graph with {len(initial_node_dict)} nodes built.")
    if len(initial_node_dict) > 1000:
        very = ""
        if len(initial_node_dict) > 2000:
            very = "very "
        logger.warning(f"! Generation of the paraphrase graphs with this initial size could be {very}slow.")
    node_dict_paraphrases = merge_graph_2_paraphrases(initial_node_dict)
    
    logger.info(f"Paraphrase graph with {len(node_dict_paraphrases)} nodes built.")
    write_graphml(node_dict_paraphrases, config, output_fn)
    logger.info(f"See output in '{output_fn}'.")

if __name__ == "__main__":
    main()

