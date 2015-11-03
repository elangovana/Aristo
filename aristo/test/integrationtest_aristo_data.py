import unittest
from aristo.core.aristo_data import AristoData


class IntegrationTestAristoData(unittest.TestCase):
    def setUp(self):
        data_file_path = "../../../inputdata/training_set.tsv"
        self._aristo_data = AristoData(data_file_path)

    def test_should_print_summary(self):
        self._aristo_data.print_summary()

    def test_should_get_x_columns(self):
        self.assertEqual(len(self._aristo_data.get_x_columns().columns), 5,
                         "The expected number of columns does not match the actual")

    def test_should_get_y_columns(self):
        self.assertEqual(len(self._aristo_data.get_y_columns().columns), 1,
                         "The expected number of columns does not match the actual")

    def test_should_get_all_questions_as_raw(self):
        self.assertTrue(type(self._aristo_data.get_all_questions_as_raw()) is str)
