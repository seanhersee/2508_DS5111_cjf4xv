#!/usr/bin/env python3
import sys
import os
import json
import logging
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

def main():
    logging.info("Pipeline Step 2B (Gemini Enrichment) started.")
    
    # -------------------------------------------------------------------------
    # TODO 1: API Environment Validation and Client Initialization
    # Extract the necessary credential key token from the local environment.
    # If the token is missing, log a critical failure and terminate the system.
    # Otherwise, instantiate the official Google GenAI Client utility.
    # -------------------------------------------------------------------------
    # === YOUR CODE HERE ===
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logging.critical("GEMENI API Key Npt Found.")
        sys.exit(1)

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        logging.critical('Failed to initialize Gemini client')
        sys.exit(1)

    # ======================

    # -------------------------------------------------------------------------
    # TODO 2: Structured Output Response Schema Definition
    # To prevent the LLM from returning unpredictable formats that would crash
    # downstream applications, define a strict "Data Contract" using a JSON 
    # Schema layout. 
    # 
    # Enforce a response type of "OBJECT" that guarantees the presence of:
    #   - video_id: (STRING, Required)
    #   - cleaned_text: (STRING, Required)
    #   - tech_terms: (ARRAY of STRINGS)
    #   - book_names: (ARRAY of STRINGS)
    # -------------------------------------------------------------------------
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        required=["video_id", "cleaned_text"],
        properties={
            "video_id":     types.Schema(type=types.Type.STRING),
            "cleaned_text": types.Schema(type=types.Type.STRING),
            "tech_terms":   types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
            "book_names":   types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
        }
    )

    # Stream processing framework reading line-by-line text inputs from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        # ---------------------------------------------------------------------
        # TODO 3: Inbound String Stream Deserialization
        # Safely wrap your stream ingestion inside an isolated try-except block.
        # Parse the raw line string object into a key-value dictionary and 
        # extract the target 'video_id' and 'raw_text' properties. 
        # Log any malformed line tracks and continue processing the stream.
        # ---------------------------------------------------------------------
        try:
            payload=json.loads(line)
            video_id = payload['video_id']
            raw_text = payload['raw_text']
        except Exception as e:
            logging.error(f"Failed to parse incoming JSON payload row: {str(e)}")
            continue

        logging.info(f"Orchestrating Gemini enrichment for video: {video_id}")
        
        prompt = f"""
        You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
        1. Strip all timestamps and duration codes.
        2. Extract technical architecture terms and books.
        """

        # ---------------------------------------------------------------------
        # TODO 4: Structured Model Invocation and Instant Stream Flushing
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

        except Exception as e:
            logging.error(f"Failed processing video {video_id} during LLM generation: {str(e)}")

    logging.info("Pipeline Step 2B finished.")

if __name__ == '__main__':
    main()
