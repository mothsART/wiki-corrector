from .checker import Checker

import re
import os
import subprocess

DIR_SHELLCODE_DESTINATION = 'shellcode_result'

PATH_TEMP_FILE = "/tmp/shellcheck_file"

# TODO faire en sorte que ça puisse aussi récupérer quand la balise est <code bash> ou <code sh>
# pour l'instant ça ressort 67 fichiers et c'est beaucoup (il doit y avoir de faux positif) !
# j'ai 97 fichiers, je ne sais pas si c'est bon, review pour faux positif !
class ShellCodeChecker(Checker):
    def __init__(self, full=False):
        super(ShellCodeChecker, self).__init__(DIR_SHELLCODE_DESTINATION, full)
    
    
    def create_temp_file_to_run_shellcheck(self,content_to_put_in_file):
        with open(PATH_TEMP_FILE,"w") as f:
            f.write(content_to_put_in_file)
    
    def run_shellcheck_and_return_output(self):
        capt = subprocess.run(["shellcheck",PATH_TEMP_FILE], capture_output=True, text=True)
        return capt.stdout
    
    # surtout pour factoriser ;)
    def keep_only_shellcode_then_run_checker(self, matched_balise_content, balise_ouvrante, balise_fermante):
        if matched_balise_content:
            for balise_found_content in matched_balise_content:
                # on ne prend que le code bash depuis le shebang jusqu'à la balise fermante
                match = re.search(balise_ouvrante + r'.*?(#!/.*?)' + balise_fermante, balise_found_content, re.DOTALL)
                if match:
                    shellcode_content = match.group(1)
                    # un script shell débute avec shebang et fini par sh (pas python ou ruby)
                    if shellcode_content.startswith("#!/") and shellcode_content.partition('\n')[0].endswith("sh"):
                        #print(shellcode_content)
                        self.create_temp_file_to_run_shellcheck(shellcode_content)
                        self.warnings += f"{self.run_shellcheck_and_return_output()}\n\n"

    def parse(self, content):
        # le re.DOTALL permet que '.' match plusieurs lignes
        # le ? permet de demander qu'on veut le moins de contenu qui match tout les caractères
        match = re.findall(r'<code>\n?#!/.*?</code>', content, re.DOTALL)
        self.keep_only_shellcode_then_run_checker(match, '<code>', '</code>')
        
        match = re.findall(r'<file b?a?sh.*?#!/.*?</file>', content, re.DOTALL)
        self.keep_only_shellcode_then_run_checker(match, r'<file b?a?sh>', '</file>')
        
