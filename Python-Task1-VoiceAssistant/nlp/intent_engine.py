"""
Intent Detection Engine for Intelligent Python Voice Assistant.
Uses lightweight Vector Space Model (TF-IDF + Cosine Similarity) for natural language understanding and integrates entity extraction.
"""

import json
import os
from typing import Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.logger import get_logger
from config import Config
from nlp.entity_extractor import EntityExtractor

logger = get_logger("IntentEngine")

class IntentClassifier:
    """Classifies spoken or typed text into defined action intents with entity extraction."""

    def __init__(self, intents_path: Optional[str] = None):
        self.intents_path = intents_path or str(Config.INTENTS_FILE)
        self.patterns = []
        self.intent_labels = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        self.tfidf_matrix = None
        self.is_trained = False

        self.load_intents_and_train()

    def load_intents_and_train(self) -> bool:
        """Loads patterns from intents.json and fits TF-IDF vectorizer."""
        if not os.path.exists(self.intents_path):
            logger.error(f"Intents configuration file not found at: {self.intents_path}")
            return False

        try:
            with open(self.intents_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.patterns = []
            self.intent_labels = []

            for intent_entry in data.get("intents", []):
                intent_name = intent_entry.get("intent")
                for pattern in intent_entry.get("patterns", []):
                    self.patterns.append(pattern)
                    self.intent_labels.append(intent_name)

            if self.patterns:
                self.tfidf_matrix = self.vectorizer.fit_transform(self.patterns)
                self.is_trained = True
                logger.info(f"Intent Classifier trained successfully on {len(self.patterns)} patterns across {len(set(self.intent_labels))} intents.")
                return True
            else:
                logger.warning("No patterns found in intents file.")
                return False
        except Exception as e:
            logger.error(f"Error training Intent Classifier: {e}")
            return False

    def predict(self, text: str, threshold: Optional[float] = None) -> Tuple[str, float]:
        """
        Predicts intent for input text.
        Returns tuple of (intent_name, confidence_score).
        Backward-compatible interface for Phase 1 & 2.
        """
        result = self.predict_intent(text, threshold=threshold)
        return result["intent"], result["confidence"]

    def predict_intent(self, text: str, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Predicts intent and extracts entities for input text.
        Returns structured dictionary containing intent, confidence, entities, and raw text.
        """
        conf_threshold = threshold if threshold is not None else Config.NLU_CONFIDENCE_THRESHOLD

        if not text or not text.strip():
            return {
                "intent": "empty",
                "confidence": 0.0,
                "entities": {},
                "raw_text": text or ""
            }

        if not self.is_trained:
            logger.warning("Classifier is not trained. Defaulting to unknown intent.")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "raw_text": text
            }

        try:
            clean_text = text.strip()
            query_vector = self.vectorizer.transform([clean_text])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]

            max_idx = similarities.argmax()
            max_score = float(similarities[max_idx])

            if max_score >= conf_threshold:
                predicted_intent = self.intent_labels[max_idx]
                entities = EntityExtractor.extract_entities(clean_text, predicted_intent)
                logger.debug(f"Input: '{clean_text}' -> Intent: '{predicted_intent}' (confidence: {max_score:.2f}, entities: {entities})")
                return {
                    "intent": predicted_intent,
                    "confidence": max_score,
                    "entities": entities,
                    "raw_text": clean_text
                }
            else:
                logger.info(f"Input: '{clean_text}' below confidence threshold ({max_score:.2f} < {conf_threshold:.2f})")
                return {
                    "intent": "unknown",
                    "confidence": max_score,
                    "entities": {},
                    "raw_text": clean_text
                }
        except Exception as e:
            logger.error(f"Prediction error for text '{text}': {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "raw_text": text
            }
