import os
import requests
import simplejson


class KnowledgeCreator:
    def download_corpus_by_titles(self, titles, output_file, batch_size=0):
        """
        Downloads data from the internet by searching the article key words in Wikipedia
        :rtype : returns a list of filennames to which the output is saved
        :param output_file: the output file to which the downloaded articles are saved to
        :param titles: an ienumerable collection  of key words to search the internet
        """

        url = 'https://en.wikipedia.org/w/api.php'
        params = {}
        params['format'] = "xml"
        params['action'] = "query"
        params['export'] = ""
        params['redirects'] = ""
        params['exportnowrap'] = ""
        n = 30 if batch_size == 0 else batch_size
        titles_batch = [titles[i:i+n] for i in range(0, len(titles), n)]
        i = 0;
        for titles in titles_batch:
            i = i +1
            params['titles'] = '|'.join(titles)
            r = requests.post(url, data=params)
            out_file =os.path.join( os.path.dirname(output_file), os.path.splitext(output_file)[0] + "_" + str(i) + os.path.splitext(output_file)[1])
            print(titles)
            with open(out_file , 'w') as out:
                out.write(r.text)
            print(out_file)


    def get_titles_containing_word(self, word, out_file):
        url = 'https://en.wikipedia.org/w/api.php'
        params = {}
        params['format'] = "json"
        params['action'] = "query"
        params['list'] = "search"
        params['srsearch'] =word
        params['srlimit'] = 50
        params['srprop']="score"
        params["sroffset"] = 0
        maxIteraions = 50
        i=0;
        while (True) :
            #retrieve matching titles
            r = requests.post(url, data=params)
            rsp = simplejson.loads(r.text)
            total = rsp["query"]["searchinfo"]["totalhits"]
            titles =[]
            for title in rsp["query"]["search"]:
                titles = titles + [title["title"]]
            #download articles with titles
            outdir_file =os.path.join( os.path.dirname(out_file), os.path.splitext(out_file)[0]  + "_" + str(total) + "_" + str(i) + os.path.splitext(out_file)[1])

            self.download_corpus_by_titles(titles,outdir_file)
            #check if complete
            i=i+1
            has_more_items =  "continue" in rsp
            if not has_more_items:
                break
            else:
                params["sroffset"] = rsp["continue"]["sroffset"]
            if i > maxIteraions:
                break

    def download_wikipedia_articles(self, words, output_file):
        words = set(words)
        print(words)
        print(len(words))
        for word in words:
            out_file =os.path.join( os.path.dirname(output_file), os.path.splitext(output_file)[0] + "_" + word + os.path.splitext(output_file)[1])
            self.get_titles_containing_word(word, out_file)
