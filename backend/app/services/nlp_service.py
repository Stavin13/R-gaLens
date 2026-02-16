import spacy
import re
import dateparser
import os
import requests
from transformers import pipeline
from huggingface_hub import InferenceClient
from app.core.config import settings
from app.utils.logger import logger

class NLPOrchestrator:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.use_api = self.hf_token is not None
        
        if self.use_api:
            logger.info("Using Hugging Face Inference API for NLP tasks.")
            self.client = InferenceClient(token=self.hf_token)
        else:
            logger.info("HF_TOKEN not found. Loading models locally (this will take time and RAM)...")
            # Load models locally if no API token is provided
            self.ner_pipeline = pipeline("ner", model=settings.NER_MODEL, aggregation_strategy="simple", framework="pt")
            self.zero_shot = pipeline("zero-shot-classification", model=settings.ZERO_SHOT_MODEL, framework="pt")
            self.summarizer = pipeline("summarization", model=settings.SUMMARIZATION_MODEL, framework="pt")
        
        # Always load SpaCy locally (it's small and fast)
        self.nlp = spacy.load(settings.SPACY_MODEL)
        self.musicology_entities = ["Mārga", "Rāga", "Tāla", "Gāndharva", "Sāman", "Nāṭyaśāstra", "Saṃgīta"]
        self.event_labels = ["founded", "published", "performed", "recorded", "born", "died", "composed"]

    def process_document(self, text: str, metadata: dict = None) -> dict:
        logger.info(f"Orchestrating NLP processing for {len(text)} characters...")
        doc = self.nlp(text)
        
        # 1. Entity Extraction
        entities = self._extract_entities(text)
        
        # 2. Date Extraction & Decade Detection
        dates_found = self._extract_dates(text)
        decade = self._detect_decade(dates_found)
        
        # 3. Event Detection
        events = self._detect_events(text, doc)
        
        # 4. Summarization
        summary = self._generate_summary(text)
        
        return {
            "entities": entities,
            "events": events,
            "dates": dates_found,
            "summary": summary,
            "decade": decade,
            "topics": []
        }

    def _extract_entities(self, text: str) -> list:
        if self.use_api:
            try:
                results = self.client.token_classification(text, model=settings.NER_MODEL)
                entities = [{"text": r["word"], "label": r["entity_group"]} for r in results]
            except Exception as e:
                logger.error(f"HF API NER failed: {e}")
                entities = []
        else:
            results = self.ner_pipeline(text)
            entities = [{"text": r["word"], "label": r["entity_group"]} for r in results]
        
        # Add regex-based musicology terms
        for term in self.musicology_entities:
            if re.search(rf"\b{term}\b", text, re.I):
                entities.append({"text": term, "label": "MUSICOLOGY_TERM"})
        return entities

    def _detect_events(self, text: str, doc) -> list:
        # Scan ALL sentences in the document
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text) > 40]
        
        events = []
        if not sentences: return events

        # Filter sentences that contain either an event label OR a musicology term
        # This makes scanning a 200-page document efficient
        relevant_keywords = self.event_labels + self.musicology_entities
        sentences_to_process = []
        
        for sent in sentences:
            if any(kw.lower() in sent.lower() for kw in relevant_keywords):
                sentences_to_process.append(sent)

        logger.info(f"Filtered {len(sentences)} total sentences down to {len(sentences_to_process)} relevant candidates.")

        if self.use_api:
            try:
                # Use HF API for relevant sentences
                for sent in sentences_to_process[:50]: # Still limit a bit to avoid API usage exhaustion
                    res = self.client.post(json={"inputs": sent, "parameters": {"candidate_labels": self.event_labels}}, model=settings.ZERO_SHOT_MODEL)
                    import json
                    data = json.loads(res)
                    if data["scores"][0] > 0.7:
                        events.append({"sentence": sent, "type": data["labels"][0], "confidence": data["scores"][0]})
            except Exception as e:
                logger.error(f"HF API Zero-shot failed: {e}")
        else:
            # Process relevant sentences locally in batches
            if sentences_to_process:
                # Process in batches for better GPU/MPS efficiency
                batch_size = 10
                for i in range(0, len(sentences_to_process), batch_size):
                    batch = sentences_to_process[i:i + batch_size]
                    results = self.zero_shot(batch, candidate_labels=self.event_labels, framework="pt")
                    for res in results:
                        if res["scores"][0] > 0.7:
                            events.append({
                                "sentence": res["sequence"],
                                "type": res["labels"][0],
                                "confidence": res["scores"][0]
                            })
        
        return events

    def _generate_summary(self, text: str) -> str:
        if self.use_api:
            try:
                summary = self.client.summarization(text, model=settings.SUMMARIZATION_MODEL)
                return summary["summary_text"]
            except Exception as e:
                logger.error(f"HF API Summarization failed: {e}")
                return text[:200] + "..."
        else:
            summary = self.summarizer(text[:1000], max_length=150, min_length=30)
            return summary[0]["summary_text"]

    # Helper methods for dates remain the same...
    def _extract_dates(self, text: str) -> list:
        date_patterns = [r"\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}", r"\d{4}s", r"\b1[89]\d{2}\b"]
        found = []
        for pattern in date_patterns:
            for m in re.finditer(pattern, text):
                ds = m.group()
                parsed = dateparser.parse(ds)
                found.append({"raw": ds, "parsed": parsed.isoformat() if parsed else None})
        return found

    def _detect_decade(self, dates: list) -> int:
        years = [int(d["parsed"][:4]) for d in dates if d["parsed"]]
        if years:
            decades = [(y // 10) * 10 for y in years]
            return max(set(decades), key=decades.count)
        return None

nlp_orchestrator = NLPOrchestrator()
