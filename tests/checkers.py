import unittest

from wiki_c.checkers.checker import DokuwikiTagInLine


class CheckerTests(unittest.TestCase):

    def test_inline(self):
        line = "installation via ''sudo apt install blabla'' marchera."
        tag_inline = DokuwikiTagInLine(line)
        self.assertTrue(tag_inline.is_in_all_tags('blabla'))

    def test_tags_in_line(self):
        line = "commande 1 : ''echo $PATH'', commande 2 : ''touch file''"
        tag_inline = DokuwikiTagInLine(line)
        self.assertEqual(
            ["''echo $PATH''", "''touch file''"],
            tag_inline.give_tags("''", "''")
        )
