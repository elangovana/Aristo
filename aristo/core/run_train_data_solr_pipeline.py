import os
import time

from aristo.core.aristo_data import AristoData
from aristo.core.setup_logger import setup_log
from aristo.core.solr_wikipedia_all_answer_then_question_pipeline import SolrWikipediaAllAnswerThenQuestionPipeline
from aristo.core.solr_wikipedia_snippet_pipeline import SolrWikipediaSnippetPipeline


def run_train_data(train_data_csv):
    out_dir=os.path.join(os.path.dirname(__file__),"../../../outputdata/train_{}".format(time.strftime('%Y%m%d_%H%M%S')))
    os.makedirs(out_dir)
    logger = setup_log(out_dir)
    #aristo_train_data = AristoData(train_data_csv, range(0,500))
    aristo_train_data = AristoData(train_data_csv)
    aristo_train_data.print_summary()
    pipeline = SolrWikipediaAllAnswerThenQuestionPipeline(data=aristo_train_data, logger = logger)
    pipeline.run_pipeline()



    pipeline.write_to_disk((out_dir))
    print(pipeline.score())
    # analyser.aristo_write_most_common_words_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../word_frequencies.csv")
    #  analyser.aristo_write_most_common_nouns_to_file(aristo_data.get_all_questions_as_raw(), 1000,"../../../noun_frequencies.csv")




run_train_data(os.path.join(os.path.dirname(__file__),"../../../inputdata/training_set.tsv"))
