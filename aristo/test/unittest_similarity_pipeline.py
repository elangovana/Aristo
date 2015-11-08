import pytest
from datetime import datetime, timedelta
from  unittest.mock import Mock
from aristo.core.aristo_data import AristoData
import pandas as pd
from aristo.core.similarity_pipeline import SimilarityPipeline

test_data = [
    (
        [("1", 'Which is an example of an organism that has been selectively bred for a particular genetic trait?',
          "cats that eat mice", "cows that graze on grass", "pigs that form large herds",
          "chickens that lay large eggs", "D"),
         ("2", 'When do females begin producing their sex cells called eggs?',
          "when they reach sexual maturity", "before they are born", "before engaging in sexual activity",
          "at the beginning of their monthly cycle", "B")
         ],

        ("1", 'Which is an example of an organism that has been selectively bred for a particular genetic trait?',
         "chickens that lay large eggs", "before they are born", "before engaging in sexual activity",
         "at the beginning of their monthly cycle")
        ,

        "A"

    )

]

def create_mock_train_test_aristo_data(train_data, test_question):
    mock_train_data = Mock(AristoData)
    mock_train_data.x = pd.DataFrame.from_records(train_data, index=["id"],
                                                  columns=("id", "question", "A", "B", "C", "D", "answer"))
    mock_train_data.y = mock_train_data.x[['answer']]
    mock_train_data.x = mock_train_data.x[["question", "A", "B", "C", "D"]]
    mock_test_data = Mock(AristoData)
    mock_test_data.x = pd.DataFrame.from_records([test_question], index=["id"],
                                                 columns=("id", "question", "A", "B", "C", "D"))
    return (mock_train_data, mock_test_data)

@pytest.mark.parametrize("train_data,test_question,expected_answer", test_data)
def test_should_predict_the_correct_answer(train_data, test_question, expected_answer):
    (mock_train_data, mock_test_data) = create_mock_train_test_aristo_data(train_data, test_question)
    sut = SimilarityPipeline(mock_train_data, mock_test_data)

    sut.run_pipeline()

    question_id = test_question[0]
    assert sut.predictions.loc[question_id, "answer"] == expected_answer




