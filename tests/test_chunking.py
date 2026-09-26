import unittest
from src.chunker import split_into_sentences, create_meaningful_chunks, chunk_structured_document
from src.similarity_checker import load_model

class TestChunking(unittest.TestCase):

    def setUp(self):
        """
        Setup that runs before each test case. Loads the pre-trained model.
        """
        self.model = load_model()
        self.similarity_threshold = 0.7

        # Sample text for testing
        self.sample_text = "This is the introduction. This section provides an overview. Here are the details."

    def test_split_into_sentences(self):
        """
        Test if the text is correctly split into sentences.
        """
        sentences = split_into_sentences(self.sample_text)
        self.assertEqual(len(sentences), 3)

    def test_create_meaningful_chunks(self):
        """
        Test the chunking process to ensure it correctly groups sentences based on similarity.
        """
        sentences = [
            "This is the first sentence.",
            "This is the second sentence which is similar to the first.",
            "This is an entirely different third sentence."
        ]

        chunks = create_meaningful_chunks(sentences, self.model, self.similarity_threshold)
        self.assertGreaterEqual(len(chunks), 1)

    def test_chunk_structured_document(self):
        """
        Test the end-to-end chunking process on a structured document.
        """
        chunks = chunk_structured_document(self.sample_text, self.similarity_threshold)
        self.assertIsNotNone(chunks)
        self.assertGreater(len(chunks), 0)

    def test_chunk_with_empty_text(self):
        """
        Test the chunking process with empty input to ensure graceful handling.
        """
        chunks = chunk_structured_document("", self.similarity_threshold)
        self.assertEqual(chunks, [])

if __name__ == '__main__':
    unittest.main()
