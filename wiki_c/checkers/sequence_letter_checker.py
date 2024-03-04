from .checker import Checker
import re
import os
import subprocess

DIR_SEQ_LET_DESTINATION = 'sequence_letter_result'

PATTERN_SEQUENCE_TRIPLE_CONSONNES = "[b-df-hj-np-tvwxz]{9,}"

COMPILED = re.compile(PATTERN_SEQUENCE_TRIPLE_CONSONNES)

VOYELLES_TRIPLE = ["aaa", "eee", "uuu", "iii", "ooo", "yyy"]

DICO_ALLOWED_WORD = ""

with open("dict", "r") as dico:
    DICO_ALLOWED_WORD = dico.read()
    DICO_ALLOWED_WORD = [s for s in DICO_ALLOWED_WORD.splitlines() if s and "#" not in s]

class SequenceLetterChecker(Checker):
    def __init__(self, full=False):
        super(SequenceLetterChecker, self).__init__(DIR_SEQ_LET_DESTINATION, full)
        compteur = 0

    def parse(self, content):

        splitted_content = content.splitlines()

        for splitted_line in splitted_content:
            # suite de 3 consonnes
            for amatch in COMPILED.finditer(splitted_line):
                matched_suite = amatch.group(0)
                if matched_suite not in DICO_ALLOWED_WORD:
                    self.warnings += f"contient une suite de consonnes \"{matched_suite}\" dans la ligne \"{splitted_line}\"\n\n"

            # suite de 3 même voyelles
            for seq_voyelles_triple in VOYELLES_TRIPLE:
                if seq_voyelles_triple in splitted_line:
                    self.warnings += f"la séquence \"{seq_voyelles_triple}\" est présente dans la ligne \"{splitted_line}\"\n\n"

