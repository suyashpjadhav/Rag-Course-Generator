import unittest
from src.ingestion.loaders import load_manual_transcript

class TestIngestion(unittest.TestCase):

    def test_load_manual_transcript(self):
        """
        Test manual transcript text loading.
        """
        sample_text = "This is a test transcript for unit testing."
        doc = load_manual_transcript(sample_text)
        self.assertIsNotNone(doc)
        self.assertEqual(doc.page_content, sample_text)

if __name__ == '__main__':
    unittest.main()
