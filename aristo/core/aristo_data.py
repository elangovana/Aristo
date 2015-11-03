
import pandas as pd

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
    def __init__(self, csv_file):
        self._file_path = csv_file
        self._dataframe = pd.read_csv(csv_file, delimiter="\t")
        self._dataframe.set_index("id", inplace=True)


    def summary(self):
        """
        Prints a summary of the the challenge data
        """
        print(self._dataframe.info())

    def get_x_columns(self):
        """
        Gets the x columns as a data frame
        :return: returns the x columns as a dataframe
        """
        return self._dataframe[['question', 'answerA', 'answerB', 'answerC', 'answerD']]

    def get_y_columns(self):
        """
        Gets the y columns as a data frame
        :return:returns the y columns as a dataframe
        """
        return self._dataframe[['correctAnswer']]
