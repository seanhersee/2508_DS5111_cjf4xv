#!/usr/bin/env python3
"""
Receives transcripts from upstream pileline steps and passes the contents
through Gemini LLM to extract techinical content and book reccomendations.
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
load_dotenv(dotenv_path="/home/ubuntu/2508_DS5111_cjf4xv/scripts/bin/.env")

# Audit logging framework tracking pipeline telemetry
logging.basicConfig(
    filename='./pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LLMStrategy (ABC): # pylint: disable=too-few-public-methods
    """The contract every encirchment must satisfy"""

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
            logging.critical("GEMENI API Key Not Found.")
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

def main():
    """
    Passes a Youtube Transcript to Gemini LLM to clena the text and extract relevant
    information.

    Gemini LLM is accessed via a stored API key. The text is cleaned of timestamps
    and duration markers, and technical concepts and book recommendations are
    extracted per the provided prompt. Any API access or LLM initialization
    errors are logged.
    """

    logging.info("LLM Enrichment Started.")


    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logging.critical("GEMENI API Key Not Found.")
        sys.exit(1)

    try:
        client = genai.Client(api_key=api_key)
    except Exception: # pylint: disable=broad-exception-caught
        logging.critical('Failed to initialize Gemini client')
        sys.exit(1)

    response_schema = types.Schema(
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

    # Stream processing framework reading line-by-line text inputs from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # ---------------------------------------------------------------------
        # Inbound String Stream Deserialization
        # Safely wrap your stream ingestion inside an isolated try-except block.
        # Parse the raw line string object into a key-value dictionary and
        # extract the target 'video_id' and 'raw_text' properties.
        # Log any malformed line tracks and continue processing the stream.
        # ---------------------------------------------------------------------
        try:
            payload=json.loads(line)
            video_id = payload['video_id']
            raw_text = payload['raw_text']
        except Exception as e: # pylint: disable=broad-exception-caught
            logging.error("Failed to parse incoming JSON payload row: %s", str(e))
            continue

        logging.info("Orchestrating Gemini enrichment for video: %s", video_id)

        prompt = f"""
        You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
        1. Strip all timestamps and duration codes.
        2. Extract technical architecture terms and books.
        """

        # ---------------------------------------------------------------------
        # Structured Model Invocation and Instant Stream Flushing
        # Call the 'gemini-2.5-flash' model via the unified SDK interface.
        # Inject the constructed prompt along with the raw text sequence payload.
        # Map the configuration block to use the structured JSON mime-type
        # and enforce your defined response schema parameters.
        # Write the resulting text explicitly to sys.stdout and flush immediately.
        # ---------------------------------------------------------------------
        try:
            response = client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = [prompt,raw_text],
                config = types.GenerateContentConfig(
                    response_mime_type = 'application/json',
                    response_schema = response_schema))
            sys.stdout.write(response.text + '\n')
            sys.stdout.flush()

        except Exception as e: # pylint: disable=broad-exception-caught
            logging.error("Failed processing video %s during LLM generation: %s", video_id, str(e))

    logging.info("Pipeline Step 2B finished.")

if __name__ == '__main__':
    main()
