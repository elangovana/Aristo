from aristo.core.aristo_data import AristoData
from aristo.core.aristo_analyser import AristoAnalyser


def run_train_data(train_data_csv):
    aristo_data = AristoData(train_data_csv)
    analyser = AristoAnalyser()
    # analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")
    #  analyser.aristo_write_most_common_nouns_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../noun_frequencies.csv")

    for main_sentence  in aristo_data.get_x_columns()["question"].values.tolist():
        print("-----------")
        print(main_sentence)
        for sentence in analyser.aristo_get_similar_sentences(main_sentence,
                                                              aristo_data.get_x_columns()[aristo_data.get_x_columns().question != main_sentence]["question"].values.tolist(), .25):
            print(sentence)


run_train_data("../../../inputdata/training_set.tsv")
