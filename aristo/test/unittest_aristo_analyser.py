import unittest
from aristo.core.aristo_analyser import (AristoAnalyser)


class UnitTestAristoAnalyser(unittest.TestCase):
    def setUp(self):
        self.sut = AristoAnalyser()
        self.data = "When athletes begin to exercise, their heart rates and respiration rates increase. "

    def test_should_tokenise_words(self):
        self.sut.aristo_tokenise_words(self.data)

    def test_should_get_named_entities(self):
        self.sut.aristo_get_named_entities(self.data)

    def test_should_get_most_common_words(self):
        print(self.sut.aristo_get_most_common_words(self.data, 50))

    def test_should_get_most_common_nouns(self):
        print(self.sut.aristo_get_most_common_nouns(self.data, 50))

    def test_should_get_similar_sentences(self):
        similar_sentences = []
        for sentence in self.sut.aristo_get_similar_sentences(
                "In the eighteenth century it was often convenient to regard man as a clockwork automaton.",
                ["In the eighteenth century, it was often convenient to regard man as clockwork automata",
                 "My friend is anna"], .5):
            similar_sentences.append(sentence)
        self.assertEqual(1, len(similar_sentences))
