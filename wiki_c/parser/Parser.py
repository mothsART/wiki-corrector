from .BlockParser import BlockParser

class Parser:
    def __init__(self):
        pass

    def parse(self, content, parse_on_find_block):
        code_block = BlockParser(BlockParser.NAME_BLOCK_FILE)

        regex_code = code_block.get_pattern_regex()

        for match in regex_code.finditer(content):
            
            script_shell_code = match.group()
            
            try:
                code_block.parse(script_shell_code)

                # code_block.dump()
                # print(code_block.language_content())

                parse_on_find_block(code_block)
            except:
                pass
                # print("le contenu est :", script_shell_code)

            