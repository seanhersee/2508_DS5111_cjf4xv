#!/usr/bin/env python3
"""
Receives transcripts from upstream pileline steps and passes the contents
through Gemini LLM to extract technical content and book recomendations.
"""

import sys
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environmental configurations from local workspace files
load_dotenv()

# Audit logging framework tracking pipeline telemetry
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))   # .../scripts/bin
REPO_SCRIPTS_DIR = os.path.dirname(SCRIPT_DIR)             # .../scripts
LOG_DIR = os.path.join(REPO_SCRIPTS_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'pipeline_audit.log')

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename= LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LLMStrategy (ABC): # pylint: disable=too-few-public-methods
    """The contract every enrichment must satisfy"""

    @abstractmethod
    def enrich(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Transforms raw transcript inputs into validated, structured enriched data
        using an LLM client."""
        return

class GeminiEnrichmentStrategy(LLMStrategy): # pylint: disable=too-few-public-methods
    """Implementation of the enrichment steps using Gemini"""

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logging.critical("GEMINI API Key Not Found.")
            sys.exit(1)

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception: # pylint: disable=broad-exception-caught
            logging.critical('Failed to initialize Gemini client')
            sys.exit(1)

        self.response_schema = types.Schema(
            type = types.Type.OBJECT,
            required = ['video_id', 'cleaned_text'],
            properties ={
                'video_id': types.Schema(type = types.Type.STRING),
                'cleaned_text': types.Schema(type = types.Type.STRING),
                'tech_terms': types.Schema(
                    type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                'book_names': types.Schema(
                    type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING))
                }
            )

    def enrich(self, payload: dict[str, Any]) -> dict[str, Any]:
        video_id = payload['video_id']
        raw_text = payload['raw_text']

        prompt =  f"""
        You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
        1. Strip all timestamps and duration codes.
        2. Extract technical architecture terms and books.
        """

        response = self.client.models.generate_content(
            model = 'gemini-2.5-flash',
            contents = [prompt,raw_text],
            config = types.GenerateContentConfig(
                response_mime_type = 'application/json',
                response_schema = self.response_schema))

        return json.loads(response.text)

class TranscriptEnricher: # pylint: disable=too-few-public-methods
    """Vendor-agnostic engine: streams JSONL records through an injected LLM strategy."""

    def __init__(self, strategy: LLMStrategy) -> None:
        self.strategy = strategy


    def run(self, stream) -> None:
        """Read JSONL records from `stream`, enrich each, write results to stdout."""
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)

            except Exception as e:  # pylint: disable=broad-exception-caught
                logging.error("Failed to parse incoming JSON payload row: %s", str(e))
                continue

            video_id = payload.get('video_id', 'unknown')

            try:
                logging.info('Running Enrichment for video: %s', video_id)

                enriched_result = self.strategy.enrich(payload)

                sys.stdout.write(json.dumps(enriched_result) + '\n')
                sys.stdout.flush()

            except Exception as e: # pylint: disable=broad-exception-caught
                logging.error(
                    'Failed processing video %s during enrichment: %s',
                    video_id,
                    str(e))


def main():
    """Assemble the enrichment pipeline and run it against stdin."""
    logging.info("LLM Enrichment Started.")

    strategy = GeminiEnrichmentStrategy()
    enricher = TranscriptEnricher(strategy)
    enricher.run(sys.stdin)

    logging.info("LLM Enrichment Complete.")


if __name__ == '__main__':
    main()
