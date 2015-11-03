import nltk
from nltk.tokenize import PunktSentenceTokenizer
import csv

class aristo_analyser:

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
        with open(file,'w') as out:
            csv_out=csv.writer(out)
            csv_out.writerow(['name','num'])
            for row in self.aristo_get_most_common_words(data, top_n_most_common):
                csv_out.writerow(row)