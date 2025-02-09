from .checker import Checker
from ..parser.Parser import Parser
import os
import subprocess

DIR_SHELLCODE_DESTINATION = 'shellcode_result'

# Vous pouvez trouver la liste des erreurs
# sur le site de shellcheck
# https://www.shellcheck.net/wiki/

class ShellCodeChecker(Checker):
    def __init__(self, full=False):
        super(ShellCodeChecker, self).__init__(DIR_SHELLCODE_DESTINATION, full)
        compteur = 0
    
    # le programme shellcode n'accepte que les scripts bash et shell
    SHELLCODE_ACCEPTED_LANGUAGE_NAMES = ("bash", "sh")

    PATH_TEMP_FILE = "/tmp/shellcheck_file"

    def create_temp_file_to_run_shellcheck(self,content_to_put_in_file):
        with open(self.PATH_TEMP_FILE,"w") as f:
            f.write(content_to_put_in_file)
    
    def run_shellcheck_and_return_output(self):
        capt = subprocess.run(["shellcheck", self.PATH_TEMP_FILE], capture_output=True, text=True)
        return capt.stdout
    
    def parse_on_find_block(self, code_block_obj):
        
        shellbang = code_block_obj.get_shellbang()

        if shellbang is None:
            return

        name_language = code_block_obj.language_content()
        
        if name_language not in self.SHELLCODE_ACCEPTED_LANGUAGE_NAMES:
            # print("non pris en compte : ", name_language)
            return
                
        self.create_temp_file_to_run_shellcheck(code_block_obj.get_content())

        result = self.run_shellcheck_and_return_output()

        # print(result)

        self.warnings += f"{result}\n\n"
    
    def parse(self, content):
        self.warnings = ""

        my_parse = Parser()

        my_parse.parse(content, self.parse_on_find_block)
