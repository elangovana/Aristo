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
        self.predictions = pd.DataFrame("-", index=self._data.x.index.values, columns=['answer', "question_key", "A_Key","B_Key","C_Key" , "D_key", "score", "A_score", "B_score", "C_score", "D_score"])
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
            max_score = -1
            correct_answer = "-"
            for score_method in [self._get_score_answer_search_within_top_question_search_pages]:

            #for score_method in [self._get_search_score, self._get_score_answer_search_within_top_question_search_pages, self._get_search_score_weighted_answer]:
                predicted_answers = []
                for choice in ["A", "B", "C", "D"]:
                    choice_index = self._data.x.columns.get_loc(choice)
                    choice_text = row[choice_index + 1]
                    score = score_method(question, choice_text)
                    if score > max_score:
                        max_score=score
                        correct_answer=choice
                predicted_answers += correct_answer
            self.predictions.loc[row[id_index]].answer = max(set(predicted_answers), key=predicted_answers.count)
            self.predictions.loc[row[id_index]].score = max_score

    def _get_search_score(self, question, answer_choice):
        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)

        url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        query = ' '.join(q_keywords) + " " + ' '.join(a_keywords)
        data = {'limit': 3, 'query': query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, simplejson.dumps(data), headers=headers)

        print(query)

        rsp = simplejson.loads(r.text)
        matching_docs =  rsp['response']['docs']
        score = sum([ d['score'] for d in matching_docs])/len(matching_docs) if (len(matching_docs) > 0) else 0
        print(score)
        return score

    def _get_score_answer_search_within_top_question_search_pages_using_span(self, question, answer_choice):

        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
        q_query = ' '.join(q_keywords)
        qa_query = ' '.join(a_keywords)

        url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        n =  len(q_keywords)
        q_query = "{}w({})".format(n,q_query)
        data = {'limit': 3, 'query': q_query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url + "&defType=edismax&&qf=title%5E100000+text", simplejson.dumps(data), headers=headers)
        rsp = simplejson.loads(r.text)
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs'] ]) + ")"

        url =  url + "&fq=id%3A+" + top_page_ids

        if len(a_keywords )==0 : return 0
        n =  2*len(a_keywords)
        qa_query = "{}w({})".format(n,qa_query)
        data = {'limit': 10, 'query': qa_query}
        print(q_query + ":" + qa_query)
        r = requests.post(url, simplejson.dumps(data), headers=headers)

        rsp = simplejson.loads(r.text)

        matching_docs =  rsp['response']['docs']
        score = sum([ d['score'] for d in matching_docs])/len(matching_docs) if (len(matching_docs) > 0) else 0
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
        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
        q_query = ' '.join(q_keywords)
        a_query = ' '.join(a_keywords)

        # submit the question keywords to solr to obtain top 3 documents
        if None is url:
            url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        data = {'limit': 3, 'query': q_query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url , simplejson.dumps(data), headers=headers)
        rsp = simplejson.loads(r.text)

        # Submit the answer keywords to solr, but restricting the search to the top 3 pages for the question search
        print(data)
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs'] ]) + ")"
        print(top_page_ids)
        url =  url + "&fq=id%3A+" + top_page_ids
        data = {'limit': 10, 'query': a_query + " "  + q_query}
        r = requests.post(url, simplejson.dumps(data), headers=headers)
        rsp = simplejson.loads(r.text)
        print(data)

        # Return the average score the solr results for the answer
        matching_docs =  rsp['response']['docs']
        score = sum([ d['score'] for d in matching_docs])/len(matching_docs) if (len(matching_docs) > 0) else 0
        print(score)
        return score

    def _get_score_average_search_within_top_question_top_answer_search_pages(self, question, answer_choice):
        return (self._get_score_answer_search_within_top_question_search_pages(question,answer_choice) + self._get_search_score_weighted_answer(question,answer_choice) +self._get_search_score(question,answer_choice))/3


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
        return self._get_score_answer_search_within_top_question_search_pages(question,answer_choice, "http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json" + "&defType=edismax&&qf=title%5E100000+text")

    def _get_search_score_weighted_question_snippets(self, question, answer_choice, textanalyser = None):
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
        # Get keywords from question and answer
        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
        q_query = ' '.join(q_keywords)
        a_query = ' '.join(a_keywords)
        print("--------")
        url = 'http://localhost:8983/solr/wikipedia/select?fl=title%2Cid%2C+score&wt=json&hl=true&hl.simple.pre=&hl.simple.post='
        data = {'limit': 3, 'query': q_query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url , simplejson.dumps(data), headers=headers)
        print(q_query + ":" +  a_query)
        rsp = simplejson.loads(r.text)

        #search the answer within the top 3 pages
        top_page_ids = "(" + ' OR '.join([d['id'] for d in rsp['response']['docs'] ]) + ")"
        print(top_page_ids)
        url =  url + "&fq=id%3A+" + top_page_ids
        data = {'limit': 10, 'query': a_query}
        r = requests.post(url, simplejson.dumps(data), headers=headers)

        if textanalyser == None :
            textanalyser = TextAnalyser()
        snippets = []
        for d in rsp['response']['docs']:
            snippets = snippets + rsp['highlighting'][d['id']]["text"]

        score = textanalyser.get_top_n_similar_sentences(a_query + " "+ q_query,snippets)[1]

        print(score)
        return score

    def _get_search_score_weighted_answer(self, question, answer_choice):
        q_keywords = self._analyser.get_words_without_stopwords(question)
        a_keywords = self._analyser.get_words_without_stopwords(answer_choice)
        p_query = ' '.join(a_keywords)
        s_query = ' '.join(q_keywords)

        url = 'http://localhost:8983/solr/wikipedia/select?fl=*%2Cscore&wt=json'
        data = {'limit': 3, 'query': p_query}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url +"&defType=edismax&&qf=title%5E100000+text", simplejson.dumps(data), headers=headers)
        rsp = simplejson.loads(r.text)
        if len(rsp['response']['docs']) == 0 : return 0
        top_page_id = rsp['response']['docs'][0]['id']

        url =  url + "&fq=id%3A+" + top_page_id

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