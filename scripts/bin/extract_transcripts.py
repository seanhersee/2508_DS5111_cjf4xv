#!/usr/bin/env python3
"""
Extracts transcripts for provided Youtbue IDs.

This script reads Youtube video IDs provoed through stdin, extracts the transcripts
from the Youtube Transcript API, and returns a JSON payload of the transcript
per video. This is returned to stdout.
"""


import sys
import os
import json
import logging

# Add the import statement so we have access to the load_dotenv function from dotenv
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# use the loaded dotenv function to conditionally load the credentials from .env
load_dotenv()

# Direct logging statements to a shared audit log asset
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))   # .../scripts/bin
REPO_SCRIPTS_DIR = os.path.dirname(SCRIPT_DIR)             # .../scripts
LOG_DIR = os.path.join(REPO_SCRIPTS_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'pipeline_audit.log')

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """
    Main function which extracts and return the transcript for each video ID.

    Configures the Youtube API client using a Webshare proxy. Fore each video ID,
    the transcript is extracted from the Youtube API and combined into a
    timestamped string, which is then written to a JSON payload and emmitted. Any
    errors in proxy setup or fetching of transcipts are logged.
    """
    logging.info("Pipeline Step 2A (Raw Extraction) started.")

    # Ingest routing keys from the local shell environment
    proxy_user = os.getenv("WEBSHARE_USER")
    proxy_pass = os.getenv("WEBSHARE_PASSWORD")

    if proxy_user and proxy_pass:
        logging.info(
            "Proxy credentials detected. Routing traffic via Webshare Residential network.")
        # Use YouTubeTranscriptApi with a keyword argument proxy_config.
        # Use WebshareProxyConfig to create the proxy using the username and password
        ytt_api = YouTubeTranscriptApi(
                proxy_config=WebshareProxyConfig(
                    proxy_username=proxy_user,
                    proxy_password=proxy_pass)
        )
    else:
        logging.warning("No proxy credentials found. Running with direct raw local IP routing.")
        ytt_api = YouTubeTranscriptApi()

    # Process streaming IDs line-by-line from stdin
    for line in sys.stdin:
        video_id = line.strip()
        if not video_id:
            continue

        logging.info("Processing transcript extraction for video: %s", video_id)

        try:
            # Execute the modern 2026 instance lookup method
            fetched_transcript = ytt_api.fetch(video_id)
            transcript_list = fetched_transcript.to_raw_data()

            # Stitch chunks with timestamp codes preserved for the staging file
            raw_text = " ".join([f"[{item['start']}] {item['text']}" for item in transcript_list])

            # Pack into a simple intermediary JSON object and emit to stdout
            # Create a variable called payload
            #    Store a dict object with video_id and raw_text as keys, with the appropriate values
            #    Then use sys.stdout to write that to console
            #    Finally, flush the stdout
            payload ={'video_id':video_id, 'raw_text':raw_text}
            sys.stdout.write(json.dumps(payload) + "\n")
            sys.stdout.flush()

        except Exception as e: # pylint: disable=broad-exception-caught
            logging.error("Failed to fetch YouTube transcript for %s: %s", video_id, e)
            continue

    logging.info("Pipeline Step 2A finished.")

if __name__ == '__main__':
    main()
