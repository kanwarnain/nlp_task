import pickle
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from extract_faq import extract_all_faqs


class FAQProcessor:
  """Simple FAQ processor using FAISS for vector search"""

  def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
    self.model_name = model_name
    self.model = SentenceTransformer(self.model_name)
    self.faqs: List[Dict] = []
    self.embeddings: np.ndarray = None
    self.index: faiss.IndexFlatIP = None  # Inner product for cosine similarity
    self.is_indexed = False

  def load_faqs(self, faq_directory: str = "shell-retail/faq/") -> None:
    """Load and process FAQs from HTML files"""
    print(f"Loading FAQs from {faq_directory}...")
    raw_faqs = extract_all_faqs(faq_directory)

    # Convert to our format
    self.faqs = []
    for faq in raw_faqs:
      self.faqs.append({"question": faq["title"], "answer": faq["content"], "filename": faq["filename"]})

    print(f"Loaded {len(self.faqs)} FAQs")

  def build_index(self) -> None:
    """Build FAISS index from FAQ embeddings"""
    if not self.faqs:
      raise ValueError("No FAQs loaded. Call load_faqs() first.")

    print("Generating embeddings...")
    # Combine question and answer for better retrieval
    texts = [f"{faq['question']} {faq['answer']}" for faq in self.faqs]

    # Generate embeddings
    embeddings = self.model.encode(texts, show_progress_bar=True)

    # Normalize for cosine similarity
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    self.embeddings = embeddings.astype(np.float32)

    # Build FAISS index
    dimension = self.embeddings.shape[1]
    self.index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors = cosine similarity
    self.index.add(self.embeddings)

    self.is_indexed = True
    print(f"Built FAISS index with {len(self.faqs)} FAQs")

  def search(self, query: str, top_k: int = 3) -> List[Dict]:
    """Search for relevant FAQs"""
    if not self.is_indexed:
      raise ValueError("Index not built. Call build_index() first.")

    # Generate query embedding
    query_embedding = self.model.encode([query])
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    query_embedding = query_embedding.astype(np.float32)

    # Search
    scores, indices = self.index.search(query_embedding, top_k)

    # Format results
    results = []
    for score, idx in zip(scores[0], indices[0]):
      if idx < len(self.faqs):  # Valid index
        result = self.faqs[idx].copy()
        result["score"] = float(score)
        results.append(result)

    return results

  def save_index(self, filepath: str = "faq_index.pkl") -> None:
    """Save the processor state"""
    data = {"faqs": self.faqs, "embeddings": self.embeddings, "model_name": self.model_name}

    with open(filepath, "wb") as f:
      pickle.dump(data, f)

    # Save FAISS index separately
    if self.index:
      faiss.write_index(self.index, filepath.replace(".pkl", ".faiss"))

    print(f"Saved index to {filepath}")

  def load_index(self, filepath: str = "faq_index.pkl") -> None:
    """Load the processor state"""
    with open(filepath, "rb") as f:
      data = pickle.load(f)

    self.faqs = data["faqs"]
    self.embeddings = data["embeddings"]

    # Load FAISS index
    index_path = filepath.replace(".pkl", ".faiss")
    if Path(index_path).exists():
      self.index = faiss.read_index(index_path)
      self.is_indexed = True

    print(f"Loaded index from {filepath}")


if __name__ == "__main__":
  processor = FAQProcessor()
  processor.load_faqs()
  processor.build_index()
  processor.save_index()

  # Test search
  results = processor.search("How do I download the Shell app?")
  print("\nSearch results:")
  for i, result in enumerate(results, 1):
    print(f"{i}. {result['question']} (Score: {result['score']:.3f})")
    print(f"   {result['answer'][:100]}...")
