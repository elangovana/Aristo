from aristo.core.text_analyser import TextAnalyser
import pandas as pd


class SimilarityPipeline:
    def __init__(self, train_data, test_data, analyser=None):
        self._train_data = train_data
        self._test_data = test_data
        self._analyser = analyser
        self.predictions = pd.DataFrame("-", index=self._test_data.x.index.values, columns=['answer', "description"])
        if analyser is None:
            self._analyser = TextAnalyser()

    def run_pipeline(self):
        self._calc()

    def print_summary(self):
        pass

    def score(self):
        pass

    def write_to_disk(self, directory):
        pass

    def _calc(self):
        question_index = self._train_data.x.columns.get_loc("question")
        test_q_index = self._train_data.x.columns.get_loc("question")
        train_tuples = self._train_data.x.itertuples()
        for test_row in self._test_data.x.itertuples():
            test_sentence = test_row[test_q_index + 1]
            top_similar_train_row = \
                self._analyser.aristo_get_top_n_similar_sentences(test_sentence, train_tuples, 1,
                                                                  .25,
                                                                  lambda x: x[question_index + 1])[0]
            correct_answer_column_name = self._train_data.y.loc[top_similar_train_row[0], "answer"]
            correct_answer_column_index = self._train_data.x.columns.get_loc(correct_answer_column_name) + 1
            top_matching_answer = \
                self._analyser.aristo_get_top_n_similar_sentences(top_similar_train_row[correct_answer_column_index],
                                                                  test_row[2:5], 1, .25)[0]
            self.predictions.loc[test_row[0]].description = top_matching_answer
            self.predictions.loc[test_row[0]].answer = ["A", "B", "C", "D"][test_row[2:5].index(top_matching_answer)]
