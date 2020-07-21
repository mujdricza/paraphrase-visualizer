#!/usr/bin/env python3.8

"""
Representation of a token in a sentence.


"""

from typing import List, Dict

class Token:

    def __init__(self,
        sentence_idx: int,
        token_idx: int,
        token_word: str,
        is_start_token: bool,
        is_end_token: bool) -> None:

        self.__sentence_idx = sentence_idx
        self.__token_idx = token_idx
        self.__token_word = token_word
        self.__is_start_token = is_start_token
        self.__is_end_token = is_end_token

        self.__node_id = None

    
    
    @property
    def node_id(self):
        """Id of the node."""
        return self.__node_id
    
    @node_id.setter
    def node_id(self, node_id):
        if self.__node_id is not None:
            raise ValueError
        self.__node_id = node_id

    @property
    def sentence_idx(self):
        """Sentence index within the input sentence collection (only readable)"""
        return self.__sentence_idx

    @property
    def token_idx(self):
        """Token index within the sentence (only readable)"""
        return self.__token_idx

    @property
    def token_word(self):
        """Token (only readable)"""
        return self.__token_word

    @property
    def is_start_token(self):
        """Whether the token is the first one in the sentence (only readable)"""
        return self.__is_start_token

    @property
    def is_end_token(self):
        """Whether the token is the last one in the sentence (only readable)"""
        return self.__is_end_token


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        f = "F" if self.is_start_token else ""
        l = "L" if self.is_end_token else ""
        fl = "M" if len(f + l) < 1 else f"{f}{l}"
        return f"{self.token_word} ({self.sentence_idx}/{self.token_idx} {fl}) -> Node={self.node_id}"


    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True
        if not isinstance(other, type(self)):  # isinstance is including base classes
            return False

        return (self.sentence_idx, self.token_idx) \
               != (other.sentence_idx, other.token_idx)

    def __hash__(self):
        return hash(type(self), self.sentence_idx, self.token_idx)
