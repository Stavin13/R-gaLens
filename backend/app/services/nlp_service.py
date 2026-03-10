import spacy
import re
import dateparser
import os
import json
from openai import OpenAI
from groq import Groq
from app.core.config import settings
from app.utils.logger import logger

class NLPOrchestrator:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.groq_key = settings.GROQ_API_KEY
        
        if not self.api_key and not self.groq_key:
            logger.warning("Neither OPENROUTER_API_KEY nor GROQ_API_KEY found. LLM features will fail.")
        
        # OpenRouter Client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        ) if self.api_key else None
        
        # Groq Client
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
        
        # Always load SpaCy locally for text segmentation
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
        except Exception as e:
            logger.error(f"Failed to load SpaCy model {settings.SPACY_MODEL}: {e}")
            # Fallback to a simple split if spacy fails
            self.nlp = None

        self.musicology_entities = ["Mārga", "Rāga", "Tāla", "Gāndharva", "Sāman", "Nāṭyaśāstra", "Saṃgīta", "Prabandha", "Desi", "Vaadya"]
        self.primary_terms = ["Marga", "Raagas", "Taala", "Prabandha", "Desi", "Vaadya"]
        self.event_labels = ["founded", "published", "performed", "recorded", "born", "died", "composed"]

    def _call_llm(self, prompt: str, system_prompt: str = "You are a musicology research assistant.") -> str:
        """Calls LLM providers with fallback logic."""
        providers = []
        
        # Add Groq to the top of the list if available (fast and separate quota)
        if self.groq_client:
            providers.append(("groq", settings.GROQ_MODEL))
            
        # Add OpenRouter models
        if self.client:
            providers.append(("openrouter", settings.OPENROUTER_MAIN_MODEL))
            providers.append(("openrouter", settings.OPENROUTER_FALLBACK_MODEL))
        
        for provider, model in providers:
            try:
                logger.info(f"Calling {provider} model: {model}")
                
                if provider == "groq":
                    response = self.groq_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.choices[0].message.content
                
                elif provider == "openrouter":
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        extra_headers={
                            "HTTP-Referer": "https://github.com/Stavin13/R-gaLens",
                            "X-Title": "Musicology Research Assistant",
                        }
                    )
                    return response.choices[0].message.content
                    
            except Exception as e:
                logger.error(f"Error calling {provider} model {model}: {e}")
                continue
        
        logger.error("All LLM providers failed.")
        return ""

    def process_document(self, text: str, metadata: dict = None) -> dict:
        logger.info(f"Orchestrating NLP processing for {len(text)} characters using Smart Chunking...")
        
        # 1. Date Extraction (keeping regex-based as it's reliable and cheap)
        dates_found = self._extract_dates(text)
        decade = self._detect_decade(dates_found)
        
        # 2. Smart Chunking: Extract context only around primary terms
        snippets = []
        context_window = 1200 # Chars around the match
        
        for term in self.primary_terms:
            # Find up to 2 context matches per primary term
            matches = list(re.finditer(rf"\b{term}\b", text, re.I))
            for match in matches[:2]:
                start = max(0, match.start() - context_window // 2)
                end = min(len(text), match.end() + context_window // 2)
                snippet = text[start:end].strip()
                snippets.append(f"--- Context regarding {term} ---\n...{snippet}...")

        # If no primary terms matched, fallback to first 3000 chars for a general summary
        if not snippets:
            logger.info("No primary terms matched. Using doc header for summary.")
            analysis_text = text[:3000]
        else:
            # Join snippets, cap at 7000 chars to be token-safe
            analysis_text = "\n\n".join(snippets)[:7000]
            logger.info(f"Extracted {len(snippets)} relevant snippets for focused analysis.")
        
        prompt = f"""
        Analyze the following segments from a musicology academic document.
        
        Focus specifically on these key terms: {', '.join(self.primary_terms)}.
        
        Tasks:
        1. Provide a concise summary (3-5 sentences) of how these terms are framed in these specific contexts.
        2. Extract key musicology entities (e.g., Rāga, Tāla, specific instruments or schools).
        3. Identify any historical or musical events (e.g., performances, years, publications).
        
        Format your response as strictly valid JSON:
        {{
            "summary": "...",
            "entities": [{{ "text": "...", "label": "..." }}],
            "events": [{{ "sentence": "...", "type": "...", "confidence": 0.9 }}]
        }}
        
        Text Segments:
        {analysis_text}
        """
        
        llm_response = self._call_llm(prompt, system_prompt="You are an expert musicologist. Output ONLY valid JSON.")
        
        try:
            # Extract JSON block
            json_match = re.search(r"(\{.*\})", llm_response, re.DOTALL)
            if json_match:
                clean_json = json_match.group(1).strip()
                result = json.loads(clean_json)
            else:
                result = {"summary": "No JSON block found", "entities": [], "events": []}
        except Exception as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw LLM response: {llm_response}")
            result = {"summary": "Error parsing response", "entities": [], "events": []}

        # Add regex-based musicology terms as a safety net
        found_entities = result.get("entities", [])
        for term in self.musicology_entities:
            if re.search(rf"\b{term}\b", text, re.I):
                if not any(e["text"].lower() == term.lower() for e in found_entities):
                    found_entities.append({"text": term, "label": "MUSICOLOGY_TERM"})
        
        return {
            "entities": found_entities,
            "events": result.get("events", []),
            "dates": dates_found,
            "summary": result.get("summary", ""),
            "decade": decade,
            "topics": []
        }

    def synthesize_research(self, term: str, start_year: int, end_year: int, decade_data: dict) -> dict:
        """
        Rigorous academic synthesis of research across decades.
        decade_data: { "1930s": ["summary1", ...], "1940s": [...] }
        """
        logger.info(f"Synthesizing rigorous research for term: {term} ({start_year}-{end_year})")
        
        # Prepare the structured decade data string
        structured_decade_data = ""
        for decade, summaries in sorted(decade_data.items()):
            structured_decade_data += f"\n### Decade: {decade}\n"
            for i, s in enumerate(summaries):
                structured_decade_data += f"Extract {i+1}: {s}\n"

        prompt = f"""
        You are a rigorous academic research analyst.

        You are analyzing academic documents discussing the concept "{term}".

        The documents are grouped by decade from {start_year} to {end_year}.

        Your task:

        For EACH decade, analyze ONLY the provided material and produce:

        1. what_spoken:
           - The dominant framing or definition of "{term}" in that decade.
           - How it was primarily interpreted or positioned.

        2. what_discussed:
           - Major themes.
           - Recurring arguments.
           - Methodological approaches.
           - Debates or disagreements (if present).

        3. new_discussion:
           - Clearly identifiable new interpretations.
           - Novel methodologies.
           - Conceptual shifts.
           - If no significant novelty is supported by evidence, write:
             "No significant new development identified."

        Rules:
        - Use ONLY the provided documents.
        - Do NOT invent information.
        - Do NOT assume trends without evidence.
        - If a decade has limited data, write:
          "Insufficient evidence for strong conclusion."
        - Return strictly valid JSON.
        - Do not include commentary outside JSON.

        Return exactly in this format:

        {{
          "concept": "{term}",
          "decades": [
            {{
              "decade": "...",
              "what_spoken": ["..."],
              "what_discussed": ["..."],
              "new_discussion": ["..."]
            }}
          ]
        }}

        Documents:
        {structured_decade_data}
        """

        llm_response = self._call_llm(prompt, system_prompt="You are a senior academic researcher. Output ONLY valid JSON.")
        
        try:
            clean_json = re.sub(r"```json\s*|\s*```", "", llm_response).strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Failed to parse Synthesis JSON: {e}")
            return {"error": "Failed to parse synthesis", "raw": llm_response}

    # Regex-based extraction remains as it's useful and fast
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
