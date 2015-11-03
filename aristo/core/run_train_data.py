from aristo.core.aristo_data import AristoData
from aristo.core.aristo_analyser import aristo_analyser


def run_train_data(train_data_csv):
    aristo_data = AristoData(train_data_csv)
    analyser = aristo_analyser()
    analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")


run_train_data("../../../inputdata/training_set.tsv")
