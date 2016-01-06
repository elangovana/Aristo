from aristo.core.solr_wikipedia_pipeline import SolrWikipediaPipeline
from aristo.core.text_analyser import TextAnalyser

__author__ = 'aparnaelangovan'


class SolrWikipediaAllAnswerThenQuestionPipeline(SolrWikipediaPipeline):
    def __init__(self, data, text_analyser=None, logger=None):
        super().__init__(data, text_analyser, logger)

    def run_pipeline(self):
        self.logger.info("running SolrWikipediaAllAnswerThenQuestionPipeline.run_pipeline")
        self._calc()

    def _calc(self):
        self.logger.info("running")
        q_index = self._data.x.columns.get_loc("question")
        id_index = 0
        for row in self._data.x.itertuples():
            question = row[q_index + 1]

            self.logger.info("running question id {}".format(row[0]))

            answer_choices = {}

            for choice in ["A", "B", "C", "D"]:
                choice_index = self._data.x.columns.get_loc(choice)
                choice_text = row[choice_index + 1]
                answer_choices[choice] = choice_text

            (correct_answer, score) =  self._get_score_answer_search_within_top_question_search_pages_with_all(question,  answer_choices)


            self.predictions.loc[row[id_index]].answer = correct_answer
            self.predictions.loc[row[id_index]].score = score
            self.predictions.loc[row[id_index]].q_word_count = len(self._analyser.get_words_without_stopwords(question))

    def _log_snippets(self, passages, message="Passages retrieved"):
        self.logger.info("////////////// {} ///////////////".format(message))
        self.logger.info("///////////////////////////////////////////////// \n: {} ".format(
            "\n ///////////////////////////////////////////////// \n".join(passages)))

    def _get_score_answer_search_within_top_question_search_pages_with_all(self, question, answer_choices_dictionary, url=None):
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
        self.logger.info("question: " + question)

        exlude_words = self._get_science_stop_words()

        q_keywords = [word for word in self._analyser.get_words_without_stopwords(question) \
                      if word.lower() not in exlude_words]
        q_keywords = self._remove_duplicates_preserve_order(q_keywords)

        q_query = ' '.join(q_keywords)

        answer_choices = ""
        for answer_choice in answer_choices_dictionary.keys():
            answer_choices = answer_choices + " " + answer_choices_dictionary[answer_choice]



        answer_choices_keywords = [word for word in self._analyser.get_words_without_stopwords(answer_choices) \
                      if word.lower() not in exlude_words and  word.lower() not in q_keywords]
        answer_choices_keywords = self._remove_duplicates_preserve_order(answer_choices_keywords)

        answer_choices_query =  q_query + " " + ' '.join(answer_choices_keywords)

        # submit the question keywords to solr to obtain top 3 documents
        if None is url:
            url = 'http://localhost:8983/solr/ck12/select?fl=title%2Cid%2C+score&wt=json'


        #get top   pages with answers
        fq=""
        #if len(q_keywords) < 5:
        rsp = self._submit_search_request_by_query(answer_choices_query, url, limit=50)
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        fq = "id:" + top_page_ids

        search_query =  q_query
        self.logger.info("Search query {}".format(search_query))
        rsp = self._submit_search_request_by_query(q_query, url, limit=5, fq=fq)

        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        top_page_titles = "(" + ' \n\t '.join([d['title'] for d in rsp['response']['docs']]) + ")"
        self.logger.info(top_page_ids)
        self.logger.info("Top page titles \n\t {}".format(top_page_titles))
        fq = "id:" + top_page_ids
        self.logger.info("Url used to search answer {}".format(url))

        correct_answer = "-"
        max_score = -1
        # For each question answer combination, obtain relevant passages
        for key in answer_choices_dictionary.keys():
            answer_choice = answer_choices_dictionary[key]
            a_keywords = [word for word in self._analyser.get_words_without_stopwords(answer_choice) \
                      if word.lower() not in exlude_words and word.lower() not in q_keywords]
            a_query = ' '.join(a_keywords)

            rsp = self._submit_search_request_by_query(a_query, url, limit=2, fq=fq)

            # Return the average score the solr results for the answer
            matching_docs = rsp['response']['docs']
            score = sum([d['score'] for d in matching_docs]) / len(matching_docs) if (len(matching_docs) > 0) else 0

            self.logger.info("Answer {} scored  {}".format( answer_choice, score))
            if score > max_score:
                max_score = score
                correct_answer = key

        self.logger.info("Question {} \n Correct Answer {}. {} scored  {}".format( question, correct_answer,answer_choices_dictionary[correct_answer] , max_score))
        return (correct_answer, max_score )


    def _get_top_passages(self, passages, main_sentence, top_n):
        return [ data for (data, score) in self._analyser.get_top_n_similar_sentences_using_cosine(main_sentence,passages,top_n=top_n)]

    def _get_matching_scores(self, sentences, main_sentence, top_n):
        return [ score for (data, score) in self._analyser.get_top_n_similar_sentences_using_cosine(main_sentence,sentences,top_n=top_n)]
