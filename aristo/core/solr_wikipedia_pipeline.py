from urllib.request import urlopen
import pandas as pd
import os
import requests
import simplejson
from aristo.core.text_analyser import TextAnalyser

import logging


class SolrWikipediaPipeline:
    pass

    def __init__(self, data, text_analyser=None, logger=None):
        self._data = data
        self.logger = logger or logging.getLogger(__name__)

        self.predictions = pd.DataFrame("-", index=self._data.x.index.values,
                                        columns=['answer', "question_key", "A_Key", "B_Key", "C_Key", "D_key", "score",
                                                 "A_score", "B_score", "C_score", "D_score"])
        if text_analyser is None:
            self._analyser = TextAnalyser()

    def run_pipeline(self):
        self._calc()
        # self._calc_new()

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

            for score_method in [self._get_score_answer_search_within_top_question_search_pages]: #[self._get_score_answer_search_within_top_question_search_pages]:

                # for score_method in [self._get_search_score, self._get_score_answer_search_within_top_question_search_pages, self._get_search_score_weighted_answer]:
                predicted_answers = []
                for choice in ["A", "B", "C", "D"]:
                    choice_index = self._data.x.columns.get_loc(choice)
                    choice_text = row[choice_index + 1]
                    score = score_method(question, choice_text)
                    if score > max_score:
                        max_score = score
                        correct_answer = choice
                predicted_answers += correct_answer
            self.predictions.loc[row[id_index]].answer = max(set(predicted_answers), key=predicted_answers.count)
            self.predictions.loc[row[id_index]].score = max_score

    def _calc_new(self):
        self.logger.info("running _calc_new")
        q_index = self._data.x.columns.get_loc("question")
        id_index = 0
        for row in self._data.x.itertuples():
            question = row[q_index + 1]
            correct_answer = "-"
            score_method = self._extract_answer_question_snippets  # self._extract_answer_question_snippets
            indicies = [self._data.x.columns.get_loc(x) + 1 for x in ["A", "B", "C", "D"]]

            answers = [row[i] for i in indicies]

            correct_answer_text = score_method(question, answers)
            correct_answer_index = answers.index(correct_answer_text)
            self.predictions.loc[row[id_index]].answer = ["A", "B", "C", "D"][correct_answer_index]

    def _get_search_score(self, question, answer_choice):
        self.logger.info("running _get_search_score")
        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)

        url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        query = ' '.join(q_keywords) + " " + ' '.join(a_keywords)
        data = {'limit': 3, 'query': query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, simplejson.dumps(data), headers=headers)

        print(query)

        rsp = simplejson.loads(r.text)
        matching_docs = rsp['response']['docs']
        score = sum([d['score'] for d in matching_docs]) / len(matching_docs) if (len(matching_docs) > 0) else 0
        print(score)
        return score

    def _get_score_answer_search_within_top_question_search_pages_using_span(self, question, answer_choice):
        self.logger.info("running _get_score_answer_search_within_top_question_search_pages_using_span")

        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
        q_query = ' '.join(q_keywords)
        qa_query = ' '.join(a_keywords)

        url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        n = len(q_keywords)
        q_query = "{}n({})".format(n, q_query)
        data = {'limit': 3, 'query': q_query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url + "&defType=edismax&&qf=title%5E100000+text", simplejson.dumps(data), headers=headers)
        rsp = simplejson.loads(r.text)
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"

        url = url + "&fq=id%3A+" + top_page_ids

        if len(a_keywords) == 0: return 0
        n = 2 * len(a_keywords)
        qa_query = "{}w({})".format(n, qa_query)
        data = {'limit': 10, 'query': qa_query}
        self.logger.info(q_query + ":" + qa_query)
        r = requests.post(url, simplejson.dumps(data), headers=headers)

        rsp = simplejson.loads(r.text)

        matching_docs = rsp['response']['docs']
        score = sum([d['score'] for d in matching_docs]) / len(matching_docs) if (len(matching_docs) > 0) else 0
        print(score)
        return score

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

        exlude_words = SolrWikipediaPipeline._get_science_stop_words()

        q_keywords = [word for word in self._analyser.get_words_without_stopwords(question) \
                      if word.lower() not in exlude_words]
        q_keywords = SolrWikipediaPipeline.remove_duplicates_preserve_order(q_keywords)
        a_keywords = [word for word in self._analyser.get_words_without_stopwords(answer_choice) \
                      if word.lower() not in exlude_words and word.lower() not in q_keywords]
        q_query = ' '.join(q_keywords)
        a_query = ' '.join( a_keywords)

        # submit the question keywords to solr to obtain top 3 documents
        if None is url:
            url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        self.logger.info("question: " + question)
        self.logger.info(answer_choice)
        is_short_q = (len(q_keywords) < 3)
        search_query = ' '.join(["{}^1000".format(qw) for qw in q_keywords]) + " " + a_query if is_short_q else q_query
        self.logger.info("Search query {}".format(search_query))
        rsp =self._submit_search_request_by_query( q_query,url,limit=3)

        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        top_page_titles = "(" + ' \n\t '.join([d['title'] for d in rsp['response']['docs']]) + ")"
        self.logger.info(top_page_ids)
        self.logger.info("Top page titles \n\t {}".format(top_page_titles))

        fq = "id:" + top_page_ids
        self.logger.info("Url used to search answer {}".format(url))
        rsp = self._submit_search_request_by_query( a_query,url,limit=2, fq=fq)

        # Return the average score the solr results for the answer
        matching_docs = rsp['response']['docs']
        score = sum([d['score'] for d in matching_docs]) / len(matching_docs) if (len(matching_docs) > 0) else 0
        self.logger.info(score)
        return score

    def _get_score_average_search_within_top_question_top_answer_search_pages(self, question, answer_choice):
        return (self._get_score_answer_search_within_top_question_search_pages(question,
                                                                               answer_choice) + self._get_search_score_weighted_answer(
            question, answer_choice) + self._get_search_score(question, answer_choice)) / 3

    def _get_score_answer_search_within_top_question_search_pages_boost_title(self, question, answer_choice):
        """
        Calculates the score of the answer as follows
            1. Obtain key words from the question & the answer by removing stop words
            2. Obtain top 3 pages matching the search results for the questions, with boost on title
            3. Search solr for the answer key words, but restrict the search to the top 3 pages from the question search
            4. Return the average score for the answer search

        :param question: question to search
        :param answer_choice: answer
        :return:score of the answer
        """
        return self._get_score_answer_search_within_top_question_search_pages(question, answer_choice,
                                                                              "http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json" + "&defType=edismax&&qf=title%5E100000+text")

    def _get_search_score_weighted_question_snippets(self, question, answer_choice, textanalyser=None):
        """
        Calculates the score of the answer as follows
            1. Obtain key words from the question & the answer by removing stop words
            2. Obtain top 3 pages matching the search results for the questions along with the matching snippets
            3. Search solr for the answer key words, but restrict the search to the top 3 pages from the question search
            4. Return the average score for the answer search

        :type textanalyser: TextAnalyser
        :param question: The question string
        :param answer_choice: The answer string
        :return: the score of the answer
        """
        # Init
        if textanalyser is None:
            textanalyser = TextAnalyser()
        url = 'http://localhost:8983/solr/wikipedia/select?fl=title%2Cid%2C+score&wt=json&hl=true&hl.tag.pre=&hl.tag.post='

        self.logger.info("------------------------------------------------")
        self.logger.info("running _get_search_score_weighted_question_snippets")
        self.logger.info("------------------------------------------------")
        self.logger.info("question : " + question)
        self.logger.info("answer choice : {} ".format(answer_choice))

        #Key search keywords keywords
        exlude_words = SolrWikipediaPipeline._get_science_stop_words()

        q_keywords = [word for word in self._analyser.get_words_without_stopwords(question) \
                      if word.lower() not in exlude_words]
        q_keywords = SolrWikipediaPipeline.remove_duplicates_preserve_order(q_keywords)
        a_keywords = [word for word in self._analyser.get_words_without_stopwords(answer_choice) \
                      if word.lower() not in exlude_words and word.lower() not in q_keywords]
        q_query = ' '.join(q_keywords)
        a_query = ' '.join(a_keywords)

        self.logger.info("Search query question keywords : {} ".format(q_keywords))
        self.logger.info("Search query answer keywords : {} ".format(a_keywords))

        # Search question, if length of question too short, include answer
        is_short_q = (len(q_keywords) < 3)
        search_query = ' '.join(["{}^1000".format(qw) for qw in q_keywords]) + " " + a_query if is_short_q else q_query
        self.logger.info("Search query {}".format(search_query))
        rsp =self._submit_search_request_by_query( q_query,url,limit=3)

        #Obtain top 3 pages to restrict answer search on the top pages
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        top_page_titles = "(" + ' \n\t '.join([d['title'] for d in rsp['response']['docs']]) + ")"
        self.logger.info(top_page_ids)
        self.logger.info("Top page titles \n\t {}".format(top_page_titles))
        fq = "id:" + top_page_ids



        snippets =[]

        if len(a_keywords) > 0:
             #highlight question and answer
             hlqurl = url + "&hl.q=" + a_query + " " + q_query
             self.logger.info("Url used to search answer {}".format(hlqurl))
             rsp = self._submit_search_request_by_query( a_query,hlqurl,limit=2, fq=fq)
             #extract answer
             snippets = self._extract_snippets_from_search_response(rsp)
             self.logger.info("Top snippets \n ---------------- \n: {} ".format("\n ---------------- \n".join(snippets)))

        # Get the similarity score
        if len(snippets) == 0:
            score =0
        else :
            score = textanalyser.get_top_n_similar_sentences(answer_choice, snippets)[1]

        self.logger.info("Score: \n : {} ".format(score))


        return score

    def _extract_answer_question_snippets(self, question, answer_choices, textanalyser=None):
        self.logger.info("running _extract_answer_question_snippets")
        """
        Calculates the score of the answer as follows
            1. Obtain key words from the question & the answer by removing stop words
            2. Obtain top 3 pages matching the search results for the questions along with the matching snippets
            3. Search solr for the answer key words, but restrict the search to the top 3 pages from the question search
            4. Return the average score for the answer search

        :type textanalyser: TextAnalyser
        :param question: The question string
        :param answer_choices: a list of choices
        :return: the score of the answer
        """
        # Get keywords from question and answer
        self.logger.info("------------------------------------------------")
        self.logger.info("------------------------------------------------")
        self.logger.info("question : " + question)
        self.logger.info("answer choices : {} ".format(answer_choices))
        q_keywords = self._analyser.get_words_without_stopwords(question)
        if textanalyser == None:
            textanalyser = TextAnalyser()

        # Get the top snippet for the question, taking into account the answer
        max_question_score = -1

        self.logger.info("------------------------------------------------")
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
        url = 'http://localhost:8983/solr/ck12/select?fl=title%2Cid%2C+score&wt=json&hl=true&hl.tag.pre=&hhl.tag.post='
        search_key = q_keywords + a_keywords
        self.logger.info("Searching : {}".format(search_key))
        rsp = self._submit_search_request(search_key, url)

        snippets = self._extract_snippets_from_search_response(rsp)
        self.logger.info(
            "\t All snippets for q & a {} search :\n\n \t*{}".format(search_key, "\n\t*".join(snippets)))
        (top_snippet, score) = textanalyser.get_top_n_similar_sentences_using_cosine(question, snippets)
        if (max_question_score <= score):
            top_q_snippet = top_snippet
            max_question_score = score
        self.logger.info(
            "Top snippet matching question answer score for q & a combination: {} \n\t\t\t{} ".format(score,
                                                                                                      top_snippet))

        max_answer_score = -1
        top_answer = "-"
        for answer_choice in answer_choices:

            self.logger.info("_______________________________________________________")
            score = textanalyser.cosine_similiarity_score(top_q_snippet, answer_choice)
            self.logger.info(
                "Answer {} score {} matching against snippet \n\t  {} ".format(answer_choice, score, top_q_snippet))
            if (max_answer_score <= score):
                max_answer_score = score
                top_answer = answer_choice

        self.logger.info("-----------------**************---------------")
        self.logger.info("Top question snippet : {}".format(top_q_snippet))
        self.logger.info("Top  answer : {} ".format(top_answer))

        return top_answer

    def _extract_answer_question_relative(self, question, answer_choices, textanalyser=None):
        """
        Calculates the score of the answer as follows
            1. Obtain key words from the question & the answer by removing stop words
            2. Obtain top 3 pages matching the search results for the questions along with the matching snippets
            3. Search solr for the answer key words, but restrict the search to the top 3 pages from the question search
            4. Return the average score for the answer search

        :type textanalyser: TextAnalyser
        :param question: The question string
        :param answer_choices: a list of choices
        :return: the score of the answer
        """
        # Get keywords from question and answer
        self.logger.info("------------")
        self.logger.info("question : " + question)
        self.logger.info("answer choices : " + " ".join(answer_choices))
        q_keywords = self._analyser.get_words_without_stopwords(question)
        if textanalyser == None:
            textanalyser = TextAnalyser()

        # Get the top snippet for the question, taking into account the answer
        max_question_score = -1
        page_scores = []
        for answer_choice in answer_choices:
            a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
            url = 'http://localhost:8983/solr/wikipedia/select?fl=title%2Cid%2C+score&wt=json&hl=true&hl.tag.pre=&hhl.tag.post='
            rsp = self._submit_search_request(q_keywords + a_keywords, url)

            page_scores = page_scores + self._extract_top_n_page_and_score_from_search_response(rsp)

        top_pages = sorted(page_scores, key=lambda x: x[1], reverse=True)
        self.logger.info("top_pages:")
        self.logger.info(top_pages)
        self.logger.info(top_pages[:4])
        top_pages = top_pages[:3]
        max_answer_score = -1
        top_answer = "-"
        for answer_choice in answer_choices:
            top_page_ids = "(" + ' OR '.join([pageid for (pageid, score, title) in top_pages]) + ")"
            answerurl = url + "&fq=id%3A+" + top_page_ids
            print(answerurl)
            a_keywords = self._analyser.get_words(answer_choice)
            rsp = self._submit_search_request(a_keywords, answerurl, limit=1)


            # Return the average score the solr results for the answer
            matching_docs = rsp['response']['docs']
            score = sum([d['score'] for d in matching_docs]) / len(matching_docs) if (len(matching_docs) > 0) else 0
            self.logger.info("answer :" + answer_choice + "score:" + str(score))
            if (max_answer_score <= score):
                max_answer_score = score
                top_answer = answer_choice
        self.logger.info(top_answer)
        return top_answer

    def _extract_snippets_from_search_response(self, rsp):
        snippets = []
        for d in rsp['response']['docs']:
            snippets = snippets + rsp['highlighting'][d['id']]["text"]

        return snippets

    def _submit_search_request(self, keywords, url, limit=3):
        keywords =' '.join( [word.replace(":", " ") for word in keywords])

        return self._submit_search_request_by_query(keywords,url,limit)

    def _submit_search_request_by_query(self, query, url, limit=3, fq =""):

        data = {'limit': limit, 'query': query, 'filter':fq}
        headers = {'Content-Type': 'application/json'}
        self.logger.info(data)
        r = requests.post(url, simplejson.dumps(data), headers=headers)
        if r.status_code != 200:
            raise RuntimeError(r.text)

        rsp = simplejson.loads(r.text)
        return rsp

    def _get_search_score_weighted_answer(self, question, answer_choice):
        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
        p_query = ' '.join(a_keywords)
        s_query = ' '.join(q_keywords)

        url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        data = {'limit': 3, 'query': p_query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url + "&defType=edismax&&qf=title%5E100000+text", simplejson.dumps(data), headers=headers)
        rsp = simplejson.loads(r.text)
        if len(rsp['response']['docs']) == 0: return 0
        top_page_id = rsp['response']['docs'][0]['id']

        url = url + "&fq=id%3A+" + top_page_id

        data = {'limit': 5, 'query': s_query + " " + p_query}
        print(data)
        r = requests.post(url, simplejson.dumps(data), headers=headers)
        if r.status_code != 200:
            raise RuntimeError(r.text)

        rsp = simplejson.loads(r.text)

        score = rsp['response']['docs'][0]['score'] if (len(rsp['response']['docs']) > 0) else 0

        print(score)
        return score

    @staticmethod
    def _get_words_from_distribution(words_distribution):
        return [str(wc[0]) for wc in words_distribution]

    @staticmethod
    def _get_science_stop_words():
        return ["following","follow","using", "true", "explanation", "explain", "explained", "explains","example", "past", "would", "examples",
                "way", "called", "describes", "describe", "used", "use", "must", "several", "many",  "likely","includes","include","much"
                "most", "also", "shows", "show", "best", "illustrate", "illustrated", "illustrates", "statement","statements","tell","us","done","certain","call","good","another","other","correct","correctly","suggests","suggest","suggestion","greatest","great","believed","consider","considered"]

    def _extract_top_n_page_and_score_from_search_response(self, rsp):
        result = []
        for d in rsp['response']['docs']:
            result = result + [(d['id'], d['score'], d['title'])]
        print(result)
        return result

    @staticmethod
    def remove_duplicates_preserve_order(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]