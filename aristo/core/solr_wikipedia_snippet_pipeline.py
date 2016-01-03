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
            self.logger.info("--------------------------Question Id: {}------------------------------".format(row[0]))
            question = row[q_index + 1]

            answer_choices_dict = {}
            for choice in ["A", "B", "C", "D"]:
                choice_index = self._data.x.columns.get_loc(choice)
                choice_text = row[choice_index + 1]
                answer_choices_dict[choice] = choice_text

            passages = self._get_snippets_answer_search_within_top_question_search_pages_with_all(question, answer_choices_dict)

            self._log_snippets(passages, message="Passages retrieved")

            # get top scoring answer from top passages
            max_score = -1
            correct_answer = "A"
            if len(passages) > 0:
                for choice in answer_choices_dict.keys():
                    choice_text = answer_choices_dict[choice]
                    score = self._get_matching_scores(passages,question + " " + choice_text,1)[0]
                    self.logger.info("Answer {} scored  {}".format( choice_text, score))
                    if score > max_score:
                        max_score = score
                        correct_answer = choice
            self.logger.info("Question : {}".format( question))
            self.logger.info("Correct answer : {}, {}, score:{}".format(correct_answer, answer_choices_dict[correct_answer], max_score))
            self.predictions.loc[row[id_index]].answer = correct_answer
            self.predictions.loc[row[id_index]].score = max_score
            self.predictions.loc[row[id_index]].q_word_count = len(self._analyser.get_words_without_stopwords(question))

    def _log_snippets(self, passages, message="Passages retrieved"):
        self.logger.info("////////////// {} ///////////////".format(message))
        self.logger.info("///////////////////////////////////////////////// \n: {} ".format(
            "\n ///////////////////////////////////////////////// \n".join(passages)))



    def _get_snippets_answer_search_within_top_question_search_pages_with_all(self, question, answer_choices_dictionary, url=None):
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

        if None is url:
            url = 'http://localhost:8983/solr/wikipedia/select?fl=title%2Cid%2C+score&wt=json'

        # Get scope, include all answers and questions in the search and get a long list of pages
        rsp = self._submit_search_request_by_query(answer_choices_query, url, limit=50)
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        fq = "id:" + top_page_ids

        # Shortlist the previous long list based on just the question keywords
        #hlqurl = url + "&hl=true&hl.tag.pre=&hl.tag.post=&hl.q=" + q_query
        self.logger.info("Search query {}".format(q_query))
        rsp = self._submit_search_request_by_query(q_query, url, limit=5, fq=fq)

        top_page_titles = "(" + ' \n\t '.join([d['title'] for d in rsp['response']['docs']]) + ")"
        self.logger.info("Top page titles \n\t {}".format(top_page_titles))

        snippets = self._extract_snippets_from_solr_json_response(rsp)

        # top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs']]) + ")"
        # fq = "id:" + top_page_ids
        # snippets = []
        # for key in answer_choices_dictionary.keys():
        #     answer_choice = answer_choices_dictionary[key]
        #     a_keywords = [word for word in self._analyser.get_words_without_stopwords(answer_choice) \
        #               if word.lower() not in exlude_words and word.lower() not in q_keywords]
        #     if len(a_keywords) == 0 : continue
        #     a_query = ' '.join(a_keywords)
        #     hlqurl = url + "&hl=true&hl.tag.pre=&hl.tag.post=&hl.q=" + q_query + " " +a_query
        #     rsp = self._submit_search_request_by_query(a_query, hlqurl, limit=2, fq=fq)
        #
        #     snippets = snippets + self._extract_snippets_from_solr_json_response(rsp)


        snippets = self.clean_snippets(snippets)

        return snippets


    def clean_snippets(self, snippets):
        import re
        result =[]
        for snippet in snippets:
            # result = result + [re.sub('\[|\]|\(|\)|{|}|=|&|:|\||<|>', ' ', snippet)]
            result.append(re.sub('[\|]' , ' ', snippet))
        return result

    def _get_top_passages(self, passages, main_sentence, top_n):
        return [ data for (data, score) in self._analyser.get_top_n_similar_sentences_using_cosine(main_sentence,passages,top_n=top_n)]

    def _get_matching_scores(self, sentences, main_sentence, top_n):
        return [ score for (data, score) in self._analyser.get_top_n_similar_sentences_using_cosine(main_sentence,sentences,top_n=top_n)]
