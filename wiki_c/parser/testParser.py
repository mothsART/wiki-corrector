#!/usr/bin/env python3.8

from BlockParser import BlockParser

# c = BlockParser(BlockParser.NAME_BLOCK_CODE)
# c.parse('<code bash>echo "test"</code>')
# c.dump()


# c = BlockParser(BlockParser.NAME_BLOCK_CODE)
# c.parse('<code bash monfic.sh>echo "test"</code>')
# c.dump()

c = BlockParser(BlockParser.NAME_BLOCK_CODE)
c.parse(r'''<code>
#!/usr/bin/env bash
echo "test"

</code>
''')
c.dump()
