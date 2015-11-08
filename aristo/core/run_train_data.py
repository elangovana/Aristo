from aristo.core.aristo_data import AristoData
from aristo.core.text_analyser import TextAnalyser


def run_train_data(train_data_csv):
    aristo_data = AristoData(train_data_csv)
    analyser = TextAnalyser()
    # analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")
    #  analyser.aristo_write_most_common_nouns_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../noun_frequencies.csv")

    for main_sentence  in aristo_data.x["question"].values.tolist():
        print("-----------")
        print(main_sentence)
        for sentence in analyser.aristo_get_top_n_similar_sentences(main_sentence,
                                                              aristo_data.x[aristo_data.x.question != main_sentence]["question"].values.tolist(), 1, .25):
            print(sentence)


run_train_data("../../../inputdata/training_set.tsv")
