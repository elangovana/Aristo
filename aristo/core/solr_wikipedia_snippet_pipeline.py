from aristo.core.solr_wikipedia_pipeline import SolrWikipediaPipeline
from aristo.core.text_analyser import TextAnalyser

__author__ = 'aparnaelangovan'


class SolrWikipediaSnippetPipeline(SolrWikipediaPipeline):
    def __init__(self, data, text_analyser=None, logger=None):
        super().__init__(data, text_analyser, logger)

    def run_pipeline(self):
        self.logger.info("running SolrWikepediaSnippetPipeline.run_pipeline")
        self._calc()

    def _calc(self):
        self.logger.info("running")
        q_index = self._data.x.columns.get_loc("question")
        id_index = 0
        for row in self._data.x.itertuples():
            question = row[q_index + 1]
            max_score = -1
            correct_answer = "-"
            passages = []
            # For each question answer combination, obtain relevant passages
            for choice in ["A", "B", "C", "D"]:
                choice_index = self._data.x.columns.get_loc(choice)
                choice_text = row[choice_index + 1]
                passages = passages + self._get_search_score_weighted_question_snippets(question, choice_text)

            # todo: some bad searches result in zero highlights
            if len(passages) > 0:
                #self._log_snippets(passages, message="Passages retrived")
                top_n=3
                top_n_passages = self._get_top_passages(passages,question, top_n=top_n)
                self._log_snippets(top_n_passages, message="Top {} Passages retrieved".format(top_n))

                # get top scoring answer from top passages
                max_score = -1
                correct_answer = "-"
                for choice in ["A", "B", "C", "D"]:
                    choice_index = self._data.x.columns.get_loc(choice)
                    choice_text = row[choice_index + 1]
                    score = self._get_matching_scores(top_n_passages,choice_text,1)[0]
                    self.logger.info("Answer {} scored  {}".format( choice_text, score))
                    if score > max_score:
                        max_score = score
                        correct_answer = choice

            self.predictions.loc[row[id_index]].answer = correct_answer
            self.predictions.loc[row[id_index]].score = max_score
            self.predictions.loc[row[id_index]].q_word_count = len(self._analyser.get_words_without_stopwords(question))

    def _log_snippets(self, passages, message="Passages retrieved"):
        self.logger.info("////////////// {} ///////////////".format(message))
        self.logger.info("///////////////////////////////////////////////// \n: {} ".format(
            "\n ///////////////////////////////////////////////// \n".join(passages)))

    def _get_search_score_weighted_question_snippets(self, question, answer_choice, textanalyser=None):
        """
        Returns relevant passages
            1. Obtain key words from the question & the answer by removing stop words
            2. Obtain top 3 pages matching the search results for the questions along with the matching snippets
            3. Search solr for the answer key words, but restrict the search to the top 3 pages from the question search.
               The highlight query includes question and answer
            4. Return highlights.

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

        # Key search keywords keywords
        exlude_words = self._get_science_stop_words()

        q_keywords = [word for word in self._analyser.get_words_without_stopwords(question) \
                      if word.lower() not in exlude_words]
        q_keywords = self._remove_duplicates_preserve_order(q_keywords)
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
        rsp = self._submit_search_request_by_query(q_query, url, limit=5)

        # Obtain top 3 pages to restrict answer search on the top pages
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        top_page_titles = "(" + ' \n\t '.join([d['title'] for d in rsp['response']['docs']]) + ")"
        self.logger.info(top_page_ids)
        self.logger.info("Top page titles \n\t {}".format(top_page_titles))
        fq = "id:" + top_page_ids

        snippets = []

        if len(a_keywords) > 0:
            # highlight question and answer
            hlqurl = url + "&hl.q=" + a_query + " " + q_query
            self.logger.info("Url used to search answer {}".format(hlqurl))
            rsp = self._submit_search_request_by_query(a_query, hlqurl, limit=2, fq=fq)
            # extract answer
            snippets = self._extract_snippets_from_solr_json_response(rsp)

        return snippets


    def _get_top_passages(self, passages, main_sentence, top_n):
        return [ data for (data, score) in self._analyser.get_top_n_similar_sentences_using_cosine(main_sentence,passages,top_n=top_n)]

    def _get_matching_scores(self, sentences, main_sentence, top_n):
        return [ score for (data, score) in self._analyser.get_top_n_similar_sentences_using_cosine(main_sentence,sentences,top_n=top_n)]
