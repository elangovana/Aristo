import os
from unittest.mock import Mock
import pandas as pd
import pytest
from aristo.core.aristo_data import AristoData
from aristo.core.solr_wikipedia_pipeline import SolrWikipediaPipeline

test_data = [

        ("1", 'Which is an example of an organism that has been selectively bred for a particular genetic trait?',
          "cats that eat mice", "cows that graze on grass", "pigs that form large herds",
          "chickens that lay large eggs", "D"),


         ("2", 'When do females begin producing their sex cells called eggs?',
          "when they reach sexual maturity", "before they are born", "before engaging in sexual activity",
          "at the beginning of their monthly cycle", "B")




]

def create_mock_aristo_data(data):
    mock_data = Mock(AristoData)
    mock_data.x = pd.DataFrame.from_records([data], index=["id"],
                                                  columns=("id", "question", "A", "B", "C", "D", "answer"))
    mock_data.y = mock_data.x[['answer']]
    mock_data.x = mock_data.x[["question", "A", "B", "C", "D"]]

    return mock_data


@pytest.mark.parametrize("data", test_data)
def test_solr_pipeline_should_calculate_correct_answer(data):
    (mock_data) = create_mock_aristo_data(data)
    sut = SolrWikipediaPipeline(mock_data)

    sut.run_pipeline()

    question_id = data[0]
    assert sut.predictions.loc[question_id, "answer"] == data[6]

