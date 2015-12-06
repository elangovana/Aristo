import unittest
import pytest
from aristo.core.text_analyser import (TextAnalyser)
import pandas


class UnitTestTextAnalyser(unittest.TestCase):
    def setUp(self):
        self.sut = TextAnalyser()
        self.data = "When athletes begin to exercise, their heart rates and respiration rates increase. "
        # self.data="A teacher builds a model of a hydrogen atom. A red golf ball is used for a proton, and a green golf ball is used for an electron. Which is not accurate concerning the model?"

    def test_should_tokenise_words(self):
        self.sut.get_words(self.data)

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
        sentences_to_search = pandas.DataFrame.from_records([
            ("In the eighteenth mak, it  it was often convenient to regard  man as clock", 1),
            ("In the 8909 century, it was often wqew to regard man as clowork wyyywuquw", 2),
            ("My friend is anna", 3)], columns=("question", "sno"))

        for sentence in self.sut.aristo_get_top_n_similar_sentences(
                "In the eighteenth century it was often convenient to regard man as a clockwork automaton.",
                sentences_to_search.itertuples(), 1, 0, lambda tup: tup[1]):
            actual_similar_sentences.append(sentence)

        self.assertEqual([tuple(x) for x in sentences_to_search.to_records()][0], actual_similar_sentences[0])


test_np_data = [
    ("When athletes begin to exercise, their heart rates and respiration rates increase. ",
     [["athletes"], ["heart", "rates"], ["respiration", "rates"]]),
    (
        "A teacher builds a model of a hydrogen atom. \
        A red golf ball is used for a proton, and a green golf ball is used for an electron. \
        Which is not accurate concerning the model",
        [["teacher"], ["model"], ["hydrogen", "atom"], ["red", "golf", "ball"], ["proton"], ["green","golf", "ball"],["electron"],
         ["Which"],["model"]]),

    ("tectonic plate antartica", [["tectonic", "plate", "antartica"]]),
    ("Which substance should a student apply to the skin if he or she gets splashed with an acid",[])

]


test_nn_data = [
    ("When athletes begin to exercise, their heart rates and respiration rates increase. ",
     [["athletes"], ["heart", "rates"], ["respiration", "rates"]]),
    (
        "A teacher builds a model of a hydrogen atom. \
        A red golf ball is used for a proton, and a green golf ball is used for an electron. \
        Which is not accurate concerning the model",
        [["teacher"], ["model"], ["hydrogen", "atom"], [ "golf", "ball"], ["proton"], ["golf", "ball"],["electron"],
         ["Which"],["model"]]),

    ("tectonic plate antartica", [["plate", "antartica"]]),
     ("tectonic plate. antartica", [["plate"], ["antartica"]]),

     ("Scientists Stanley Miller and Harold Urey sealed water, methane, ammonia, and hydrogen in a flask, to simulate Earth's early environment",
      [["Stanley", "Miller"]])


]

@pytest.mark.parametrize("data, expected_answer", test_np_data)
def test_should_get_np_chunks(data, expected_answer):
    sut = TextAnalyser()
    actual = sut.get_np_chunks(data)
    print(actual)
    assert actual == expected_answer

@pytest.mark.parametrize("data, expected_answer", test_nn_data)
def test_should_get_nn_chunks(data, expected_answer):
    sut = TextAnalyser()
    actual = sut.get_nn_chunks(data)
    print(actual)
    assert actual == expected_answer