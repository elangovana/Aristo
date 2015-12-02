import os
import time
from aristo.core.aristo_data import AristoData
from aristo.core.knowledge_creator import KnowledgeCreator
from aristo.core.text_analyser import TextAnalyser


def download_corpus (data_csv):
    aristo_data = AristoData(data_csv)
    corpus_file=os.path.join(os.path.dirname(__file__),"../../../corpus/mediafile_{}.xml".format(time.strftime('%Y%m%d_%H%M%S')))
    analyser = TextAnalyser()
    word_counts= analyser.aristo_get_most_common_words(aristo_data.get_all_questions_as_raw(), 1000000)
    words = [str(wc[0]) for wc in word_counts]
    print(len(words))
    print((words))
    kc = KnowledgeCreator()
    for file in kc.download_corpus(words, corpus_file):
        print(file)



download_corpus(os.path.join(os.path.dirname(__file__),"../../../inputdata/training_set.tsv"))