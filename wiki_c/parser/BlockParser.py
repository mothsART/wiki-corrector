import re

class BlockParser:
    def __init__(self, nameBlock):
        self.nameBlock = nameBlock
        self.listAttributes = []
        self.content = ""
        self.regex_pattern_block = re.compile(f"<{nameBlock}(.*?)</{nameBlock}>", re.DOTALL)
    

    NAME_BLOCK_CODE = "code"

    NAME_BLOCK_FILE = "file"

    def get_pattern_regex(self):
        return self.regex_pattern_block
    

    """Rend un string correspondant au language du contenu : ["bash", "sh", "python"]"""
    def language_content(self):
        # if len(self.listAttributes) == 0:
        #     return "unknow"

        KNOW_PROGRAMMING_LANGUAGES = ["sh", "bash", "python"]

        for language in KNOW_PROGRAMMING_LANGUAGES:
            if language in self.listAttributes:
                return language

        shellbang = self.get_shellbang()
        
        if shellbang:
            splitted = shellbang.split(" ")
            
            part1 = splitted[0]
            
            dernierIndexSlash = part1.rfind("/")

            progName = part1[dernierIndexSlash + 1::]

            if progName == "env":
                if len(splitted) > 1:
                    progName = splitted[1].strip()
            
            for language in KNOW_PROGRAMMING_LANGUAGES:
                if language == progName:
                    return language

        return "unknow"
    
    def dump(self):
        print(self.nameBlock, self.listAttributes, '"' + self.content + '"', '"' + self.language_content() + '"')
        shellbang = self.get_shellbang()
        if shellbang:
            print("shellbang ", '"' + self.get_shellbang()  + '"')

    def get_content(self):
        return self.content
    
    def get_shellbang(self):

        if len(self.content) == 0:
            return None
        
        firstLine = self.content.split("\n")[0].strip()

        # print(f"le shellbang est \"{firstLine}\"")

        if firstLine.startswith("#!/"):
            return firstLine
        
        return None


    def parse(self, content):

        if self.nameBlock != self.NAME_BLOCK_CODE and self.nameBlock != self.NAME_BLOCK_FILE:
            raise Exception("[NameBlock] il faut assigner une valeur à la propriété \"NameBlock\"")
        
        content = content.strip()

        lexStart = "<" + self.nameBlock

        if not content.startswith(lexStart):
            raise Exception(f"La chaîne en entrée ne commence pas par \"{lexStart}\".")

        lexEnd = f"</{self.nameBlock}>"

        if not content.endswith(lexEnd):
            raise Exception(f"La chaîne en entrée ne se termine pas par \"{lexEnd}\".")
        
        lines = content.split("\n")

        firstLine = lines[0]

        indexFirstEnd = firstLine.index(">")

        # print(f"l'index de fin du block {self.nameBlock} est : ", indexFirstEnd)

        sequenceAttributes = firstLine[len(lexStart): indexFirstEnd]

        sequenceAttributes = sequenceAttributes.strip()

        self.listAttributes = sequenceAttributes.split(" ")

        contentLastIndex = len(content) - len(lexEnd)

        self.content = content[indexFirstEnd + 1: contentLastIndex]

        # le contenu doit débuter par le hashtag du shellbang
        # si le premier caractère est un saut de ligne, on l'enlève
        if len(self.content) > 0 and self.content[0] == '\n':
            self.content = self.content[1:] 
        