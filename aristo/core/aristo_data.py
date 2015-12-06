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
    def __init__(self, csv_file, rows_to_include = None):
        self._file_path = csv_file
        self._dataframe = pd.read_csv(csv_file, delimiter="\t")
        # self._dataframe = self._dataframe[rows_to_exclude]
        self._dataframe = AristoData.exclude_rows(self._dataframe, rows_to_include)
        self._dataframe.set_index("id", inplace=True)
        self.x = self._dataframe[['question', 'answerA', 'answerB', 'answerC', 'answerD']]
        self.x.columns = ['question','A','B','C','D']
        try:
            self.y = self._dataframe[['correctAnswer']]
            self.y.columns =["answer"]
        except KeyError as ky:
            print(ky)
            self.y = None

    def print_summary(self):
        """
        Prints a summary of the the challenge data
        """
        print(self.x.info())
        if (self.y is not None):
            print(self.y.info())

    def get_all_questions_as_raw(self):
        return self.get_column_as_raw('question')

    def get_all_questions_answers_as_list(self):
            return self.x['question'].values.tolist() + self.x['A'].values.tolist() + self.x['B'].values.tolist() \
                   +self.x['C'].values.tolist() + self.x['D'].values.tolist()



    @staticmethod
    def exclude_rows(dataframe, rows_to_include):
        if rows_to_include is None:
            return dataframe

        return dataframe.iloc[rows_to_include]

    def get_column_as_raw(self, column_name, join_rows_by="."):
        with StringIO() as all_questions:
            (self.x[column_name] + join_rows_by) .to_csv(all_questions, index=False, header=False)
            all_str_questions = all_questions.getvalue()
        return all_str_questions

