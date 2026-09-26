import sys, os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.ingestion import load_pdf
from src.embedding_store.vectorstore import get_embeddings_model

class TestVectorStore(unittest.TestCase):

    def test_embeddings_model_initialization(self):
        """
        Test vector store embedding model initialization.
        """
        embeddings = get_embeddings_model()
        self.assertIsNotNone(embeddings)

if __name__ == "__main__":
    unittest.main()
