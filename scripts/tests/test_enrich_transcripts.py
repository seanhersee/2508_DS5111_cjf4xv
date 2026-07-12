"""
Test Suite for the enrich_transcripts.py file.

Verifies the enrichment step of the pipeline by
mocking the Gemini API. Tests run without live calls or
API credentials.
"""

import sys
import io
import json
from typing import Any
from google.genai.models import Models
from bin.enrich_transcripts import main, TranscriptEnricher, LLMStrategy

# 1. Build a dummy container mimicking the Gemini SDK response hierarchy
class MockGeminiResponse: # pylint: disable=too-few-public-methods
    """
    Placeholder for Gemeni response text.

    """
    def __init__(self, text_payload):
        self.text = text_payload

def test_enrich_transcripts_streaming_pipeline(monkeypatch, capsys):
    """
    Verifies that main() reads mock lines from stdin, calls the Gemini client structure,
    and streams verified JSON objects out to stdout without making live API network requests.
    """
    # 2. Mock out the core GenAI Client methods
    def mock_generate_content(self, model, contents, config=None):  # pylint: disable=unused-argument
        # Return a pre-baked, schema-compliant JSON string mimicking the model output
        mock_data = {
            "video_id": "ds5111_v001",
            "cleaned_text": "Welcome to class. Today we are testing mock frameworks.",
            "tech_terms": ["mock frameworks"],
            "book_names": []
        }
        return MockGeminiResponse(json.dumps(mock_data))

    # Corrected Module Target: Patch the actual Models service class inside the SDK
    monkeypatch.setattr(Models, "generate_content", mock_generate_content)

    # 3. Simulate your stream input pipeline using an in-memory text buffer
    mock_input_row = {"video_id": "ds5111_v001", "raw_text":
       "00:01 Welcome to class. Today we are testing mock frameworks."}
    mock_stdin = io.StringIO(json.dumps(mock_input_row) + "\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    # 4. Trigger the main pipeline script execution loop
    main()

    # 5. Intercept the standard console text buffers
    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    # 6. Execute data integrity validation assertions
    assert len(stdout_lines) == 1
    parsed_output = json.loads(stdout_lines[0])
    assert parsed_output["video_id"] == "ds5111_v001"
    assert "mock frameworks" in parsed_output["tech_terms"]


class MockLLMStrategy (LLMStrategy): # pylint: disable=too-few-public-methods
    """Test double: returns fixed schema-shaped data, no network."""

    def enrich (self, payload: dict[str, Any]) -> dict[str, Any]:
        """ Should echo the video_id and return the fetched data"""
        return {
            'video_id': payload.get('video_id', 'mock_vid_id_1'),
            'cleaned_text': 'Here is a mock transcript that has been cleaned.',
            'tech_terms': ['mock_test', 'LLMStrategy_tester'],
            'book_names': ['extracted and cleaned book names']}

def test_orchestrator_processes_stream_without_network(capsys):
    """Verifies TranscriptEnricher streams, processes, and flushes valid JSONL records."""

    # 1. build an in-memory input stream (one JSONL line, mirrors mock_transcripts.jsonl)
    stream = io.StringIO(
        json.dumps({"video_id": "ds5111_v001", "raw_text": "00:01 ..."}) + "\n" +
        json.dumps({"video_id": "ds5111_v002", "raw_text": "00:10 ..."}) + "\n")

    # 2. inject the fake into the real engine — this is the seam your refactor created
    enricher = TranscriptEnricher(MockLLMStrategy())

    # 3. run the real orchestration logic against the fake
    enricher.run(stream)

    # 4. capture stdout, parse, assert
    captured = capsys.readouterr()
    records = captured.out.strip().split('\n')

    assert len(records) == 2 #Should match the number of records fed in

    record_1 = json.loads(records[0])
    assert record_1['video_id'] == 'ds5111_v001' #Should match the first id fed in
    assert record_1['cleaned_text'] == 'Here is a mock transcript that has been cleaned.' #Confirms
    #cleaned_text was returned and has the correct string.
    assert 'mock_test' in record_1['tech_terms'] #confrims tech_terms is
    #returned and has the correct results
    assert 'extracted and cleaned book names' in record_1['book_names'] #confirms book_names
    #is returned and has the correct items
