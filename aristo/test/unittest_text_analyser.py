import unittest
from aristo.core.text_analyser import (TextAnalyser)
import pandas

class UnitTestTextAnalyser(unittest.TestCase):
    def setUp(self):
        self.sut = TextAnalyser()
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

    def test_should_get_top_n_similar_sentences(self):
        similar_sentences = []
        sentences_to_search = [
            "In the eighteenth mak, it was qweqwe qeqweq to regard man as mjkjk",
            "In the 8909 century, it was often wqew to regard man as clowork wyyywuquw",
            "My friend is anna"]
        for sentence in self.sut.aristo_get_top_n_similar_sentences(
                "In the eighteenth century it was often convenient to regard man as a clockwork automaton.",
                sentences_to_search, 1):
            similar_sentences.append(sentence)
        self.assertEqual(sentences_to_search[1], similar_sentences[0])


    def test_should_get_top_n_similar_sentences_given_sentence_extractor(self):
        actual_similar_sentences = []
        sentences_to_search =pandas.DataFrame.from_records( [
            ( "In the eighteenth mak, it  it was often convenient to regard  man as clock", 1),
            ( "In the 8909 century, it was often wqew to regard man as clowork wyyywuquw", 2),
            ( "My friend is anna", 3)], columns=("question", "sno"))

        for sentence in self.sut.aristo_get_top_n_similar_sentences(
                "In the eighteenth century it was often convenient to regard man as a clockwork automaton.",
                sentences_to_search.itertuples(), 1,0,lambda tup:tup[1]):
            actual_similar_sentences.append(sentence)

        self.assertEqual([tuple(x) for x in sentences_to_search.to_records()][0], actual_similar_sentences[0])


