import logging
from aristo.core.aristo_data import AristoData
from aristo.core.setup_logger import setup_log
from aristo.core.similarity_pipeline import SimilarityPipeline
from aristo.core.solr_wikipedia_all_answer_then_question_pipeline import SolrWikipediaAllAnswerThenQuestionPipeline
from aristo.core.solr_wikipedia_pipeline import SolrWikipediaPipeline
from aristo.core.solr_wikipedia_snippet_pipeline import SolrWikipediaSnippetPipeline
from aristo.core.text_analyser import TextAnalyser
import os
import time

def run_test_data(data_csv):
    out_dir=os.path.join(os.path.dirname(__file__),"../../../outputdata/test_{}".format(time.strftime('%Y%m%d_%H%M%S')))
    os.makedirs(out_dir)
    logger = setup_log(out_dir)
    aristo_data = AristoData(data_csv)

    aristo_data.print_summary()
    pipeline = SolrWikipediaAllAnswerThenQuestionPipeline(data=aristo_data, logger = logger)
    pipeline.run_pipeline()


    pipeline.write_to_disk((out_dir))
    print(pipeline.score())
    # analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")
    #  analyser.aristo_write_most_common_nouns_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../noun_frequencies.csv")




run_test_data(os.path.join(os.path.dirname(__file__),"../../../inputdata/validation_set.tsv"))
