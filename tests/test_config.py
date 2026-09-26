import unittest
from src.config.config import settings

class TestConfig(unittest.TestCase):

    def test_settings_loaded(self):
        """
        Test that global settings are initialized correctly.
        """
        self.assertIsNotNone(settings.EMBEDDING_MODEL)
        self.assertIsInstance(settings.VECTOR_DIM, int)
        self.assertGreater(settings.VECTOR_DIM, 0)
        self.assertIsInstance(settings.TOP_K, int)

if __name__ == '__main__':
    unittest.main()