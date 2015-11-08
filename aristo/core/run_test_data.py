from aristo.core.aristo_data import AristoData
from aristo.core.similarity_pipeline import SimilarityPipeline
from aristo.core.text_analyser import TextAnalyser
import os
import time

def run_test_data(train_data_csv, test_data_csv):
    aristo_train_data = AristoData(train_data_csv)
    aristo_test_data = AristoData(test_data_csv, rows_to_include= range(1,10))
    aristo_test_data.print_summary()
    aristo_train_data.print_summary()
    pipeline = SimilarityPipeline(train_data=aristo_train_data, test_data=aristo_test_data)
    pipeline.run_pipeline()

    out_dir=os.path.join(os.path.dirname(__file__),"../../../outputdata/{}_{}".format("run_test_data", time.strftime('%Y%m%d_%H%M%S')))

    os.makedirs(out_dir)
    pipeline.write_to_disk((out_dir))
    # analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")
    #  analyser.aristo_write_most_common_nouns_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../noun_frequencies.csv")




run_test_data(os.path.join(os.path.dirname(__file__),"../../../inputdata/training_set.tsv"), os.path.join(os.path.dirname(__file__),"../../../inputdata/validation_set.tsv"))
