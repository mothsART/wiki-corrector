import unittest

from wiki_c.checkers.checker import DokuwikiTagInLine

from wiki_c.checkers.dokuwiki_checker import DokuwikiWikipediaTag


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

    def test_detect_wikipedia_tag(self):
        line = "voici un lien [[https://fr.wikipedia.org/wiki/​Scalable_Vector_Graphics|format SVG]] et un autre : https://fr.wikipedia.org/wiki/Linux"
        w = DokuwikiWikipediaTag(1, line)
        self.assertEqual(
            '1 url wikipedia : "https://fr.wikipedia.org/wiki/..." à remplacer par [[wpfr>nom_page]]\n1 url wikipedia : "https://fr.wikipedia.org/wiki/..." à remplacer par [[wpfr>nom_page]]\n',
            w.detect()
        )
