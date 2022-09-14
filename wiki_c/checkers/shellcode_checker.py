from .checker import Checker

import re
import os
import subprocess

DIR_SHELLCODE_DESTINATION = 'shellcode_result'

PATH_TEMP_FILE = "/tmp/shellcheck_file"

# TODO faire en sorte que ça puisse aussi récupérer quand la balise est <code bash> ou <code sh>
# il y a des faux positif puisque qu'on prend tant qu'il y a un shebang (cas avec d'autres langage à éviter)
class ShellCodeChecker(Checker):
    def __init__(self, full=False):
        super(ShellCodeChecker, self).__init__(DIR_SHELLCODE_DESTINATION, full)
    
    
    def create_temp_file_to_run_shellcheck(self,content_to_put_in_file):
        with open(PATH_TEMP_FILE,"w") as f:
            f.write(content_to_put_in_file)
    
    def run_shellcheck_and_return_output(self):
        capt = subprocess.run(["shellcheck",PATH_TEMP_FILE], capture_output=True, text=True)
        return capt.stdout

    def parse(self, content):
        # le re.DOTALL permet que '.' match plusieurs lignes
        # le ? permet de demander qu'on veut le moins de contenu qui match tout les caractères
        match = re.findall(r'<code>.*?#!/.*?</code>', content, re.DOTALL)
        if match:
            for balise_found_content in match:
                balise_found_content = re.sub(r'^<code>[\n\t ]*#', '#', balise_found_content, re.DOTALL)
                balise_found_content = balise_found_content.replace('<code>', '')
                balise_found_content = balise_found_content.replace(r"</code>",'')
                if balise_found_content.startswith('#!/'):
                    self.create_temp_file_to_run_shellcheck(balise_found_content)
                    self.warnings += f"{self.run_shellcheck_and_return_output()}\n\n"
