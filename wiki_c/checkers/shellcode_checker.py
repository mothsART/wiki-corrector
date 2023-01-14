from .checker import Checker
import re
import os
import subprocess

DIR_SHELLCODE_DESTINATION = 'shellcode_result'

PATH_TEMP_FILE = "/tmp/shellcheck_file"

# le re.DOTALL permet que '.' match plusieurs lignes
# le ? permet de demander qu'on veut le moins de contenu qui match tout les caractères
pattern = re.compile(r"<[cf][oi][dl]e b?a?sh.*?>\n?(#!/.*?)</[cf][oi][dl]e>", re.DOTALL)

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
    def verify_script_shell_code(self, script_shell_code):
            first_occurence = script_shell_code.find('\n')
            if first_occurence == -1:
                return
            
            first_line = script_shell_code[:first_occurence]
            
            # un script shell débute avec shebang et fini par sh (pas python ou ruby)
            if first_line.startswith("#!/") and first_line.endswith("sh") and not first_line.endswith("zsh"):
                #print(shellcode_content)
                self.create_temp_file_to_run_shellcheck(script_shell_code)
                self.warnings += f"{self.run_shellcheck_and_return_output()}\n\n"
    
    def keep_only_shellcode(self, matched_balise_content, start_balise, end_balise):
        if not matched_balise_content:
            return
        for balise_found_content in matched_balise_content:
            # on ne prend que le code bash depuis le shebang jusqu'à la balise fermante
            match = re.search(start_balise + r'.*?(#!/.*?)' + end_balise, balise_found_content, re.DOTALL)
            if not match:
                continue
            self.verify_script_shell_code(match.group(1))
            
    
    def parse(self, content):
        #match = re.findall(r'<code>\n?#!/.*?</code>', content, re.DOTALL)
        #self.keep_only_shellcode(match, '<code>', '</code>')
        
        #match = re.findall(r'<code b?a?sh>\n?#!/.*?</code>', content, re.DOTALL)
        #self.keep_only_shellcode(match, '<code b?a?sh>', '</code>')
        
        for match in pattern.finditer(content):
            script_shell_code = match.group(1)
            #print(script_shell_code) # dans notre regex on a que un seul groupe
            self.verify_script_shell_code(script_shell_code) # parfait on a que ce qu'il y a dans le groupe
        
        #match = re.findall(r'<file b?a?sh.*?#!/.*?</file>', content, re.DOTALL)
        #self.keep_only_shellcode(match, r'<file b?a?sh>', '</file>')
