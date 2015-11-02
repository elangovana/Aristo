
import unittest
from aristo.core.aristo_data import AristoData


class IntegrationTestAristoData(unittest.TestCase):

    def setUp(self):
        data_file_path="../../../inputdata/training_set.tsv"
        self._aristo_data = AristoData(data_file_path)

    def test_should_parse_data(self):
        pass

