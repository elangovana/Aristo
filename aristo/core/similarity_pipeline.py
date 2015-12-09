from aristo.core.text_analyser import TextAnalyser
import pandas as pd
import os

class SimilarityPipeline:
    def __init__(self, train_data, test_data, analyser=None):
        self._train_data = train_data
        self._test_data = test_data
        self._analyser = analyser
        self.predictions = pd.DataFrame("-", index=self._test_data.x.index.values, columns=['answer', "description", "train_question", "train_id","train_answer"])
        if analyser is None:
            self._analyser = TextAnalyser()

    def run_pipeline(self):
        self._calc()

    def print_summary(self):
        pass

    def score(self):
        pass


    def write_to_disk(self, directory):
        self.predictions.to_csv(os.path.join(directory, "predictions.csv"))
        self.predictions["answer"].to_csv(os.path.join(directory, "submission_predictions.csv"), header=["correctAnswer"])
        test_data =  self._test_data.x.join(self._test_data.y) if self._test_data.y is not None else self._test_data.x
        test_data.join(self.predictions, rsuffix="pred.").to_csv(os.path.join(directory, "test_data_with_predictions.csv"))

    def _calc(self):
        question_index = self._train_data.x.columns.get_loc("question")
        test_q_index = self._train_data.x.columns.get_loc("question")

        for test_row in self._test_data.x.itertuples():
            test_sentence = test_row[test_q_index + 1]
            train_tuples = self._train_data.x.itertuples()
            top_similar_train_row = \
                self._analyser.get_top_n_similar_sentences(test_sentence, train_tuples, 1,
                                                                  similarity_threshold= 0,
                                                                  sentence_extractor= lambda x: x[question_index + 1])
            if len( top_similar_train_row ) > 0:
                self._calculate_correct_answer(test_row, top_similar_train_row[0])


    def _calculate_correct_answer(self, test_row, top_similar_train_row):
        correct_answer_column_name = self._train_data.y.loc[top_similar_train_row[0], "answer"]
        correct_answer_column_index = self._train_data.x.columns.get_loc(correct_answer_column_name) + 1
        top_matching_answer = \
            self._analyser.get_top_n_similar_sentences(top_similar_train_row[correct_answer_column_index],
                                                              test_row[2:6], 1, 0)[0]
        self.predictions.loc[test_row[0]].description = top_matching_answer
        self.predictions.loc[test_row[0]].answer = ["A", "B", "C", "D"][test_row[2:6].index(top_matching_answer)]
        self.predictions.loc[test_row[0]].train_question=top_similar_train_row[self._train_data.x.columns.get_loc("question")+1]
        self.predictions.loc[test_row[0]].train_id=top_similar_train_row[0]
        self.predictions.loc[test_row[0]].train_answer=top_similar_train_row[correct_answer_column_index]
