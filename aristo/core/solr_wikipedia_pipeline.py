from urllib.request import urlopen
import pandas as pd
import os
import requests
import simplejson
from aristo.core.text_analyser import TextAnalyser





class SolrWikipediaPipeline:
    pass

    def __init__(self, data, text_analyser=None):
        self._data = data
        self.predictions = pd.DataFrame("-", index=self._data.x.index.values, columns=['answer'])
        if text_analyser is None:
            self._analyser = TextAnalyser()

    def run_pipeline(self):
        self._calc()



    def print_summary(self):
        pass

    def score(self):
        if self._data.y is  None:
            return -1
        df = self._data.x.join(self._data.y)
        df= df.join(self.predictions, rsuffix="pred")

        correct_answers = df[df.answer == df.answerpred]
        return len(correct_answers.index)/len(df.index)



    def write_to_disk(self, directory):
        self.predictions.to_csv(os.path.join(directory, "predictions.csv"))
        self.predictions["answer"].to_csv(os.path.join(directory, "submission_predictions.csv"), header=["correctAnswer"])
        test_data = self._data.x.join(self._data.y) if self._data.y is not None else self._data.x
        test_data.join(self.predictions, rsuffix="pred").to_csv(os.path.join(directory, "data_with_predictions.csv"))

    def _calc(self):
        q_index = self._data.x.columns.get_loc("question")
        id_index =0
        for row in self._data.x.itertuples():
            question = row[q_index + 1]
            max_score = 0.0
            correct_answer = "-"
            for choice in ["A", "B", "C", "D"]:
                choice_index = self._data.x.columns.get_loc(choice)
                choice_text = row[choice_index + 1]
                score = self._get_search_score(question, choice_text)
                if score > max_score:
                    max_score=score
                    correct_answer=choice
            self.predictions.loc[row[id_index]].answer = correct_answer

    def _get_search_score(self, question, answer_choice):
        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)

        url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        query = ' '.join(q_keywords) + " " + ' '.join(a_keywords)
        data = {'limit': 5, 'query': query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, simplejson.dumps(data), headers=headers)

        print(query)

        rsp = simplejson.loads(r.text)
        return rsp['response']['docs'][0]['score']

    @staticmethod
    def _get_words_from_distribution(words_distribution):
        return [str(wc[0]) for wc in words_distribution]