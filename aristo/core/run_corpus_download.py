import os
import time
from aristo.core.aristo_data import AristoData
from aristo.core.knowledge_creator import KnowledgeCreator
from aristo.core.text_analyser import TextAnalyser


def download_corpus (data_csv):
    aristo_data = AristoData(data_csv, )
    sentence_list = [aristo_data.get_column_as_raw("A",join_rows_by=","), aristo_data.get_all_questions_as_raw() ,   aristo_data.get_column_as_raw("B",join_rows_by=",") , aristo_data.get_column_as_raw("C",join_rows_by=",") , aristo_data.get_column_as_raw("D",join_rows_by=",")]
    #sentence_list = [ aristo_data.get_all_questions_as_raw()]# aristo_data.get_column_as_raw("B",join_rows_by=",") , aristo_data.get_column_as_raw("C",join_rows_by=",") , aristo_data.get_column_as_raw("D",join_rows_by=",")]

    for sentence in sentence_list:
        kc = KnowledgeCreator()
        key_words=get_key_words(sentence)
        print(len(key_words))
        corpus_file=os.path.join(os.path.dirname(__file__),"../../../corpus/mediafile_{}.xml".format(time.strftime('%Y%m%d_%H%M%S')))
        for file in kc.download_corpus(key_words, corpus_file):
            print(file)



def get_key_words(text):
    analyser = TextAnalyser()
    key_words = set(analyser.get_words_without_stopwords(text))
    print(key_words)
    nn_phrases = [' '.join(p) for p in analyser.get_nn_chunks(text) if len(p) > 1]
    print(nn_phrases)
    key_words = key_words.union(nn_phrases)
    np_phrases = [' '.join(p) for p in analyser.get_np_chunks(text) if len(p) > 1]
    key_words = key_words.union (np_phrases)
    key_words = [w for w in key_words]
    return key_words

download_corpus(os.path.join(os.path.dirname(__file__),"../../../inputdata/training_set.tsv"))
download_corpus(os.path.join(os.path.dirname(__file__),"../../../inputdata/validation_set.tsv"))