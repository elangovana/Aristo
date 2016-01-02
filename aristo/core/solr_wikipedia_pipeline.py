from urllib.request import urlopen
import pandas as pd
import os
import requests
import simplejson
from aristo.core.text_analyser import TextAnalyser

import logging


class SolrWikipediaPipeline:
    """
    Default scoring pipeline
    """

    def __init__(self, data, text_analyser=None, logger=None):
        self._data = data
        self.logger = logger or logging.getLogger(__name__)

        self.predictions = pd.DataFrame("-", index=self._data.x.index.values,
                                        columns=['answer', "question_key", "A_Key", "B_Key", "C_Key", "D_key", "score",
                                                 "A_score", "B_score", "C_score", "D_score", "q_word_count"])
        if text_analyser is None:
            self._analyser = TextAnalyser()

    def run_pipeline(self):
        self._calc()


    def print_summary(self):
        pass

    def score(self):
        if self._data.y is None:
            return -1
        df = self._data.x.join(self._data.y)
        df = df.join(self.predictions, rsuffix="pred")

        correct_answers = df[df.answer == df.answerpred]
        score = len(correct_answers.index) / len(df.index)
        self.logger.info("Score :  " + str(score))
        return score

    def write_to_disk(self, directory):
        self.predictions.to_csv(os.path.join(directory, "predictions.csv"))
        self.predictions["answer"].to_csv(os.path.join(directory, "submission_predictions.csv"),
                                          header=["correctAnswer"])
        test_data = self._data.x.join(self._data.y) if self._data.y is not None else self._data.x
        test_data.join(self.predictions, rsuffix="pred").to_csv(os.path.join(directory, "data_with_predictions.csv"))

    def _calc(self):
        self.logger.info("running _calc")
        q_index = self._data.x.columns.get_loc("question")
        id_index = 0
        for row in self._data.x.itertuples():
            question = row[q_index + 1]
            max_score = -1
            correct_answer = "-"
            self.logger.info("running question id {}".format(row[0]))
            for choice in ["A", "B", "C", "D"]:
                choice_index = self._data.x.columns.get_loc(choice)
                choice_text = row[choice_index + 1]
                score = self._get_score_answer_search_within_top_question_search_pages(question, choice_text)
                if score > max_score:
                    max_score = score
                    correct_answer = choice
            self.predictions.loc[row[id_index]].answer = correct_answer
            self.predictions.loc[row[id_index]].score = max_score
            self.predictions.loc[row[id_index]].q_word_count = len(self._analyser.get_words_without_stopwords(question))

    def _get_score_answer_search_within_top_question_search_pages(self, question, answer_choice, url=None):
        """
        Calculates the score of the answer as follows
            1. Obtain key words from the question & the answer by removing stop words
            2. Obtain top 3 pages matching the search results for the questions
            3. Search solr for the answer key words, but restrict the search to the top 3 pages from the question search
            4. Return the average score for the answer search

        :param url: solr url
        :param question: The question string
        :param answer_choice: The answer string
        :return: the score of the answer
        """
        # Get keywords from question and answer
        self.logger.info("running _get_score_answer_search_within_top_question_search_pages")
        self.logger.info("------------")

        exlude_words = self._get_science_stop_words()

        q_keywords = [word for word in self._analyser.get_words_without_stopwords(question) \
                      if word.lower() not in exlude_words]
        q_keywords = self._remove_duplicates_preserve_order(q_keywords)
        a_keywords = [word for word in self._analyser.get_words_without_stopwords(answer_choice) \
                      if word.lower() not in exlude_words and word.lower() not in q_keywords]
        q_query = ' '.join(q_keywords)
        a_query = ' '.join(a_keywords)

        # submit the question keywords to solr to obtain top 3 documents
        if None is url:
            url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        self.logger.info("question: " + question)
        self.logger.info(answer_choice)
        is_short_q = (len(q_keywords) < 3)
        search_query = ' '.join(["{}^1000".format(qw) for qw in q_keywords]) + " " + a_query if is_short_q else q_query
        self.logger.info("Search query {}".format(search_query))
        rsp = self._submit_search_request_by_query(q_query, url, limit=5)

        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        top_page_titles = "(" + ' \n\t '.join([d['title'] for d in rsp['response']['docs']]) + ")"
        self.logger.info(top_page_ids)
        self.logger.info("Top page titles \n\t {}".format(top_page_titles))

        fq = "id:" + top_page_ids
        self.logger.info("Url used to search answer {}".format(url))
        rsp = self._submit_search_request_by_query(a_query, url, limit=3, fq=fq)

        # Return the average score the solr results for the answer
        matching_docs = rsp['response']['docs']
        score = sum([d['score'] for d in matching_docs]) / len(matching_docs) if (len(matching_docs) > 0) else 0
        self.logger.info(score)
        return score

    def _extract_snippets_from_solr_json_response(self, rsp):
        snippets = []
        for d in rsp['response']['docs']:
            snippets = snippets + rsp['highlighting'][d['id']]["text"]

        return snippets

    def _submit_search_request(self, keywords, url, limit=3):
        keywords = ' '.join([word.replace(":", " ") for word in keywords])

        return self._submit_search_request_by_query(keywords, url, limit)

    def _submit_search_request_by_query(self, query, url, limit=3, fq=""):

        data = {'limit': limit, 'query': query, 'filter': fq}
        headers = {'Content-Type': 'application/json'}
        self.logger.info(data)
        r = requests.post(url, simplejson.dumps(data), headers=headers)
        if r.status_code != 200:
            raise RuntimeError(r.text)

        rsp = simplejson.loads(r.text)
        return rsp

    def _get_science_stop_words(self):
        return ["following", "follow", "using", "true", "explanation", "explain", "explained", "explains", "example",
                "past", "would", "examples",
                "way", "called", "describes", "describe", "used", "use", "must", "several", "many", "likely",
                "includes", "include", "much"
                                       "most", "also", "shows", "show", "best", "illustrate", "illustrated",
                "illustrates", "statement", "statements", "tell", "us", "done", "certain", "call", "good", "another",
                "other", "correct", "correctly", "suggests", "suggest", "suggestion", "greatest", "great", "believed",
                "consider", "considered"]

    def _remove_duplicates_preserve_order(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]
