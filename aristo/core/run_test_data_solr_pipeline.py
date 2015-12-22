import logging
from aristo.core.aristo_data import AristoData
from aristo.core.similarity_pipeline import SimilarityPipeline
from aristo.core.solr_wikipedia_pipeline import SolrWikipediaPipeline
from aristo.core.text_analyser import TextAnalyser
import os
import time

def setup_log(dir):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

# create a file handler

    handler = logging.FileHandler(os.path.join(dir, "log.log"))
    handler.setLevel(logging.INFO)

# create a logging format

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #handler.setFormatter(formatter)

# add the handlers to the logger

    logger.addHandler(handler)
    return logger

def run_test_data(data_csv):
    out_dir=os.path.join(os.path.dirname(__file__),"../../../outputdata/test_{}".format(time.strftime('%Y%m%d_%H%M%S')))
    os.makedirs(out_dir)
    logger = setup_log(out_dir)
    aristo_data = AristoData(data_csv)

    aristo_data.print_summary()
    pipeline = SolrWikipediaPipeline(data=aristo_data, logger = logger)
    pipeline.run_pipeline()


    pipeline.write_to_disk((out_dir))
    print(pipeline.score())
    # analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")
    #  analyser.aristo_write_most_common_nouns_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../noun_frequencies.csv")




run_test_data(os.path.join(os.path.dirname(__file__),"../../../inputdata/validation_set.tsv"))
