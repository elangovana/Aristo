"""
Manages Aristo challenge data
"""
import pandas as pd



class AristoData:

    def __init__(self, csv_file):
        self._file_path = csv_file
        self._dataframe= pd.read_csv(csv_file, delimiter="\t")
        print(self._dataframe.shape)

    def parse(self):
        pass

