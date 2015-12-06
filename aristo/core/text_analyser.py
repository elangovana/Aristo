import nltk
from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import WordPunctTokenizer
import csv

import nltk.tokenize.punkt
import nltk.stem.snowball
import string
from operator import itemgetter, attrgetter


class TextAnalyser:
    """
    Analyses text using NLTK toolkit
    """

    def aristo_get_named_entities(self, text):
        """
        Parses the texts to obtain named entities
        :param text: The text to parse
        :return:returns a named entity treexw
        """
        custom_sent_tokenizer = PunktSentenceTokenizer(text)
        tokenized = custom_sent_tokenizer.tokenize(text)
        for i in tokenized[5:]:
            words = nltk.word_tokenize(i)
            tagged = nltk.pos_tag(words)
            namedEnt = nltk.ne_chunk(tagged, binary=False)
            return ((namedEnt))

    def get_words(self, text):
        words = nltk.word_tokenize(text)
        return words

    def get_words_without_punctuation(self, text):
        tokenizer = WordPunctTokenizer()
        tokens = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(text)]
        return tokens


    def get_words_without_stopwords(self, text):
        stopwords = nltk.corpus.stopwords.words('english')
        stopwords.extend(string.punctuation)
        stopwords.append('')
        tokenizer = WordPunctTokenizer()
        tokens = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(text) \
                  if token.lower().strip(string.punctuation) not in stopwords]
        return tokens

    def get_np_chunks(self, text):
        words = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(words)
        chunkgram = r"""Chunk: {(<JJ>*<NN.*>)+}"""
        chunk_parser = nltk.RegexpParser(chunkgram)
        chunked = chunk_parser.parse(tagged)
        return [l for l in self._get_leaves(chunked, "Chunk")]

    def get_nn_chunks(self, text):
        words = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(words)
        chunkgram = r"""Chunk: {(<NN.*>)+}"""
        chunk_parser = nltk.RegexpParser(chunkgram)
        chunked = chunk_parser.parse(tagged)
        return [l for l in self._get_leaves(chunked, "Chunk")]


    def _get_leaves(self, tree, node_type):
        for subtree in tree.subtrees(filter = lambda t: t.label() ==node_type):
            term = [w for (w,t) in subtree.leaves()]
            yield term


    def get_terms(self,leaves):
        for leaf in leaves:
            term = [ w for w,t in leaf]
            yield term


    def aristo_get_most_common_words(self, data, top_n_most_common):
        words = self.get_words(data)
        words = [word.lower() for word in words]
        fdist = nltk.FreqDist(words)
        return fdist.most_common(top_n_most_common)

    def aristo_write_most_common_words_to_file(self, data, top_n_most_common, file):
        TextAnalyser._write_tuple_to_file(self.aristo_get_most_common_words(data, top_n_most_common), file)

    @staticmethod
    def _write_tuple_to_file(list_of_tuples, file):
        with open(file, 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['name', 'num'])
            for row in list_of_tuples:
                csv_out.writerow(row)

    def aristo_get_most_common_nouns(self, data, top_n):
        words = self.get_words(data)
        tagged_words = nltk.pos_tag(words)
        words = [word.lower() for (word, tag) in tagged_words if tag in ('NN', "NNS", "VB", "VBP", "ADJ", "ADV")]
        fdist = nltk.FreqDist(words)
        return fdist.most_common(top_n)

    def aristo_write_most_common_nouns_to_file(self, data, top_n_most_common, file):
        TextAnalyser._write_tuple_to_file(self.aristo_get_most_common_nouns(data, top_n_most_common), file)

    def aristo_get_similar_sentences(self, main_sentence, list_of_sentences, similarity_score_threshold):
        for sentence in list_of_sentences:
            if TextAnalyser._get_similarity_score(main_sentence, sentence) >= similarity_score_threshold:
                yield sentence

    @staticmethod
    def _get_similarity_score(a, b):
        stopwords = nltk.corpus.stopwords.words('english')
        stopwords.extend(string.punctuation)
        stopwords.append('')
        tokenizer = WordPunctTokenizer()
        """Check if a and b are matches."""
        tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a) \
                    if token.lower().strip(string.punctuation) not in stopwords]

        tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b) \
                    if token.lower().strip(string.punctuation) not in stopwords]

        # Calculate Jaccard similarity
        ratio = 0
        if len(set(tokens_a).union(tokens_b)) > 0:
            ratio = len(set(tokens_a).intersection(tokens_b)) / float(len(set(tokens_a).union(tokens_b)))
        return (ratio)

    def aristo_get_top_n_similar_sentences(self, main_sentence, iteratable_collection, top_n=1,
                                           similarity_threshold=0.0, sentence_extractor=lambda x: x):
        """
        This gets the top n sentences most similar to the main sentence.
        :param sentence_extractor:  an optional expression that extracts the sentence from the row
        :param main_sentence: The sentence which needs to compared.
        :param iteratable_collection: A iterable collection against which the main sentence will be compared against.
        :param top_n: The number of top N sentences to return
        :return: Returns a list of tuples containing the top N most similar sentences along with the score. E.g [(data_row, score)]
        """
        item_sim_scores = []
        for item in iteratable_collection:
            item_sim_scores.append(
                (item, TextAnalyser._get_similarity_score(main_sentence, sentence_extractor(item))))

        item_sim_scores = [(item, score) for (item, score) in item_sim_scores if
                           score >= similarity_threshold]

        top_n = top_n if len(item_sim_scores) >= top_n else len(item_sim_scores)
        item_sim_scores = [] if top_n == 0 else \
            sorted(item_sim_scores, key=lambda tup: tup[1], reverse=True)[0:top_n][0]

        return item_sim_scores
