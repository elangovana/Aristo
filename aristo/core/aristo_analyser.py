import nltk
from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import WordPunctTokenizer
import csv

import nltk.tokenize.punkt
import nltk.stem.snowball
import string

class AristoAnalyser:
    def aristo_get_named_entities(self, text):
        custom_sent_tokenizer = PunktSentenceTokenizer(text)
        tokenized = custom_sent_tokenizer.tokenize(text)
        for i in tokenized[5:]:
            words = nltk.word_tokenize(i)
            tagged = nltk.pos_tag(words)
            namedEnt = nltk.ne_chunk(tagged, binary=False)
            return ((namedEnt))

    def aristo_tokenise_words(self, text):
        words = nltk.word_tokenize(text)
        return words

    def aristo_get_most_common_words(self, data, top_n_most_common):
        words = self.aristo_tokenise_words(data)
        words = [word.lower() for word in words]
        fdist = nltk.FreqDist(words)
        return fdist.most_common(top_n_most_common)

    def aristo_write_most_common_words_to_file(self, data, top_n_most_common, file):
        AristoAnalyser._write_tuple_to_file(self.aristo_get_most_common_words(data, top_n_most_common), file)

    @staticmethod
    def _write_tuple_to_file(list_of_tuples, file):
        with open(file, 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['name', 'num'])
            for row in list_of_tuples:
                csv_out.writerow(row)

    def aristo_get_most_common_nouns(self, data, top_n):
        words = self.aristo_tokenise_words(data)
        tagged_words = nltk.pos_tag(words)
        print(tagged_words)
        words = [word.lower() for (word, tag) in tagged_words if tag in ('NN', "NNS", "VB", "VBP")]
        fdist = nltk.FreqDist(words)
        return fdist.most_common(top_n)

    def aristo_write_most_common_nouns_to_file(self, data, top_n_most_common, file):
        AristoAnalyser._write_tuple_to_file(self.aristo_get_most_common_nouns(data, top_n_most_common), file)

    def aristo_get_similar_sentences(self, main_sentence, list_of_sentences, similarity_threshold):
        for sentence in list_of_sentences:
            if AristoAnalyser._is_ci_token_stopword_set_match(main_sentence, sentence, similarity_threshold) :
                yield sentence


    @staticmethod
    def _is_ci_token_stopword_set_match(a, b, threshold=0.5):
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
        ratio = len(set(tokens_a).intersection(tokens_b)) / float(len(set(tokens_a).union(tokens_b)))
        return (ratio >= threshold)