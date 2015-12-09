from aristo.core.aristo_data import AristoData
from aristo.core.similarity_pipeline import SimilarityPipeline
from aristo.core.solr_wikipedia_pipeline import SolrWikipediaPipeline
from aristo.core.text_analyser import TextAnalyser
import os
import time

def run_train_data(train_data_csv):
    #aristo_train_data = AristoData(train_data_csv, range(0,500))
    aristo_train_data = AristoData(train_data_csv)
    aristo_train_data.print_summary()
    pipeline = SolrWikipediaPipeline(data=aristo_train_data)
    pipeline.run_pipeline()
    out_dir=os.path.join(os.path.dirname(__file__),"../../../outputdata/train_{}".format(time.strftime('%Y%m%d_%H%M%S')))

    os.makedirs(out_dir)
    pipeline.write_to_disk((out_dir))
    print(pipeline.score())
    # analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")
    #  analyser.aristo_write_most_common_nouns_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../noun_frequencies.csv")




run_train_data(os.path.join(os.path.dirname(__file__),"../../../inputdata/training_set.tsv"))
