import os
import requests


class KnowledgeCreator:
    def download_corpus(self, article_key_words, output_file, batch_size=0):
        """
        Downloads data from the internet by searching the article key words in Wikipedia
        :rtype : returns a list of filennames to which the output is saved
        :param output_file: the output file to which the downloaded articles are saved to
        :param article_key_words: an ienumerable collection  of key words to search the internet
        """

        url = 'https://en.wikipedia.org/w/api.php'
        params = {}
        params['format'] = "xml"
        params['action'] = "query"
        params['export'] = ""
        params['redirects'] = ""
        params['exportnowrap'] = ""
        n = 30 if batch_size == 0 else batch_size
        article_key_words_batch = [article_key_words[i:i+n] for i in range(0, len(article_key_words), n)]
        i = 0;
        for words in article_key_words_batch:
            i = i +1
            params['titles'] = '|'.join(words)
            r = requests.post(url, data=params)
            out_file =os.path.join( os.path.dirname(output_file), os.path.splitext(output_file)[0] + "_" + str(i) + os.path.splitext(output_file)[1])
            print(words)
            with open(out_file , 'w') as out:
                out.write(r.text)
            yield out_file
