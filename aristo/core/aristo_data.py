import pandas as pd
from io import StringIO

"""
Class Aristo challenge data.  This class expects a tsv file with the following columns. The co

'id'
'question'
[correctAnswer] <- This is a column only required for training set
'answerA'
'answerB'
'answerC'
'answerD'

"""


class AristoData:
    def __init__(self, csv_file, rows_to_exclude = None):
        self._file_path = csv_file
        self._dataframe = pd.read_csv(csv_file, delimiter="\t")
        # self._dataframe = self._dataframe[rows_to_exclude]
        self._dataframe.set_index("id", inplace=True)
        self.x = self._dataframe[['question', 'answerA', 'answerB', 'answerC', 'answerD']]
        self.x.columns = ['question','A','B','C','D']
        self.y = self._dataframe[['correctAnswer']]
        self.y.columns =["answer"]

    def print_summary(self):
        """
        Prints a summary of the the challenge data
        """
        print(self._dataframe.info())

    def get_all_questions_as_raw(self):
        with StringIO() as all_questions:
            self._dataframe[['question']].to_csv(all_questions)
            all_str_questions = all_questions.getvalue()
        return all_str_questions
