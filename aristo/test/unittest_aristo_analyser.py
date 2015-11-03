import unittest
from aristo.core.aristo_analyser import (aristo_analyser)





class UnitTestAristoAnalyser(unittest.TestCase):
    def setUp(self):
        self.sut = aristo_analyser()
        self.data = "When athletes begin to exercise, their heart rates and respiration rates increase. "

    def test_should_tokenise_words(self):
        self.sut.aristo_tokenise_words(self.data)

    def test_should_get_named_entities(self):
            self.sut.aristo_get_named_entities(self.data)

    def test_should_get_most_common(self):
        print(self.sut.aristo_get_most_common_words(self.data, 50))



