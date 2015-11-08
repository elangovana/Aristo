import unittest
from aristo.core.aristo_data import AristoData
import os

class IntegrationTestAristoData(unittest.TestCase):
    def setUp(self):
        data_file_path = os.path.join(os.path.dirname(__file__), "../../../inputdata/training_set.tsv")
        print(os.path.abspath(data_file_path))
        self._aristo_data = AristoData(data_file_path)

    def test_should_print_summary(self):
        self._aristo_data.print_summary()

    def test_should_get_x(self):
        self.assertEqual(len(self._aristo_data.x.columns), 5,
                         "The expected number of columns does not match the actual")

    def test_should_get_y_columns(self):
        self.assertEqual(len(self._aristo_data.y.columns), 1,
                         "The expected number of columns does not match the actual")

    def test_should_get_all_questions_as_raw(self):
        self.assertTrue(type(self._aristo_data.get_all_questions_as_raw()) is str)
