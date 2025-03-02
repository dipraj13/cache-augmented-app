from sentence_transformers import SentenceTransformer
import numpy as np
import re

class CacheHandler:
    def __init__(self):
        self.documents = []
        self.conversation_cache = {}
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.current_document = None  # Track most recent document
        
    def add_document(self, text):
        self.documents.append({
            "text": text,
            "embedding": self.model.encode(text),
            "summary": self._generate_summary(text)  # Precompute summary
        })
        print(self.documents[0]["embedding"])
        self.current_document = self.documents[-1]
        
    def _generate_summary(self, text, max_length=500):
        # Simple extractive summary for demonstration
        sentences = text.split('. ')
        return '. '.join(sentences[:5]) + '...' if len(sentences) > 5 else text

    def get_document_context(self, prompt):
        # Check for summary request patterns
        if self._is_summary_request(prompt):
            
            return self.current_document["text"] if self.current_document else None
        
        # Fallback to similarity search
        prompt_embed = self.model.encode(prompt)
        similarities = [
            (doc["text"], np.dot(prompt_embed, doc["embedding"]))
            for doc in self.documents
        ]
        most_similar = max(similarities, key=lambda x: x[1], default=None)
        return most_similar[0] if most_similar and most_similar[1] > 0.3 else None

    def _is_summary_request(self, prompt):
        # Match common summary request patterns
        patterns = [
            r"what (is|does) (this|the) document",
            r"summar(y|ize)",
            r"what ('s|is) this (about|regarding)",
            r"overview of (the|this) doc"
        ]
        return any(re.search(p, prompt.lower()) for p in patterns)