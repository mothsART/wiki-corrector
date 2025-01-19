from .BlockParser import BlockParser

class Parser:
    def __init__(self):
        pass

    def parse(self, content):
        code_block = BlockParser(BlockParser.NAME_BLOCK_FILE)

        regex_code = code_block.get_pattern_regex()

        for match in regex_code.finditer(content):
            
            script_shell_code = match.group()
            
            try:
                # print(script_shell_code)
                code_block.parse(script_shell_code)

                if code_block.language_content() == "bash":
                    code_block.dump()
            except:
                print("le contenu est :", script_shell_code)

            