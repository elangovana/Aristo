import unittest
from aristo.core.aristo_analyser import (AristoAnalyser)





class IntegrationTestAristoAnalyser(unittest.TestCase):
    def setUp(self):
        self.sut = AristoAnalyser()
        self.data = "When athletes begin to exercise, their heart rates and respiration rates increase. "

    def test_should_tokenise_words(self):
        self.sut.aristo_tokenise_words(self.data)

    def test_should_get_named_entities(self):
            self.sut.aristo_get_named_entities(self.data)

    def test_should_write_most_common_words_to_file(self):
        self.sut.aristo_write_most_common_words_to_file(self.data, 10 , "../../../temp.tsv")

    def test_should_write_most_common_nouns_to_file(self):
        self.sut.aristo_write_most_common_nouns_to_file(self.data, 10 , "../../../test_nouns.tsv")



