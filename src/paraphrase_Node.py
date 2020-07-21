#!/usr/bin/env python 3.8

"""
Representation of a node in the paraphrase graph.

"""

from typing import List, Dict

from paraphrase_Token import Token


class Node:

    def __init__(self,
        node_id: str,
        node_token: Token
        ) -> None:

        self.__node_id = node_id
        self.__token_word = node_token.token_word
        self.__token_objects = [node_token]
        self.__incoming_node_ids = []
        self.__outgoing_node_ids = []

    @property
    def node_id(self):
        return self.__node_id

    @property
    def token_word(self):
        return self.__token_word

    @property
    def token_objects(self):
        return self.__token_objects

    @property
    def incoming_node_ids(self):
        return self.__incoming_node_ids

    @property
    def outgoing_node_ids(self):
        return self.__outgoing_node_ids


    def add_token_object(self, token_object):
        assert token_object not in self.token_objects, \
            f"Token {token_object} is already associated with this node!"
        return self.token_objects.append(token_object)

    def del_token_object(self, token_object):
        assert token_object in self.token_objects, \
            f"Token {token_object} is not associated with this node!"
        self.token_objects.remove(token_object)

    def add_incoming_node_id(self, node_id):
        assert node_id not in self.incoming_node_ids, \
            f"Node with id = {node_id} is already linked to this node with incoming relation!"
        return self.incoming_node_ids.append(node_id)

    def del_incoming_node_id(self, node_id):
        assert node_id in self.incoming_node_ids, \
            f"Node with id = {node_id} is not linked to this node with incoming relation!"
        self.incoming_node_ids.remove(node_id)

    def add_outgoing_node_id(self, node_id):
        assert node_id not in self.outgoing_node_ids, \
            f"Node with id = {node_id} is already linked to this node with outgoing relation!"
        return self.outgoing_node_ids.append(node_id)

    def del_outgoing_node_id(self, node_id):
        assert node_id in self.outgoing_node_ids, \
            f"Node with id = {node_id} is not linked to this node with outgoing relation!"
        self.outgoing_node_ids.remove(node_id)
    
    def has_start_token(self):
        for token_obj in self.token_objects:
            if token_obj.is_start_token:
                return True
        return False
    
    def has_end_token(self):
        for token_obj in self.token_objects:
            if token_obj.is_end_token:
                return True
        return False

    def __str__(self):  # print(); usually human-readable; if not implemented --> __repr__
        return self.__repr__()

    def __repr__(self):  # direct representation; usually more technical

        return f"{self.node_id} (W={self.token_word}; T={self.token_objects}; " \
               f"I={self.incoming_node_ids}; O={self.outgoing_node_ids}"


    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True
        if not isinstance(other, type(self)):  # isinstance is including base classes
            return False

        return (self.node_id, self.token_word) \
               != (other.node_id, other.token_word)

    def __hash__(self):
        return hash(type(self), self.node_id, self.token_word)
    
