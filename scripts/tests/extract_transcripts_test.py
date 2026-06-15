import sys
import io
import json
import pytest
from youtube_transcript_api import YouTubeTranscriptApi

# Import the executable main entry point loop from your pipeline package directory
from bin.extract_transcripts import main

class MockTranscriptContainer:
    """Mimics the 2026 .to_raw_data() array output return schema"""
    def to_raw_data(self):
        return [
            {"start": 10.5, "text": "Automated container tracking loop text entry."}
        ]

def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    """
    Verifies that the main() entrypoint loop correctly processes video IDs via stdin
    and outputs structured JSON Lines objects via stdout without hitting the internet.
    """
    # 1. Mock the external third-party API fetch dependency
    def stubbed_fetch_route(self, video_id):
        return MockTranscriptContainer()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    # 2. Mock Standard Input (sys.stdin) to feed a fake video ID into your script
    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # 3. Trigger your script's main entry point execution loop directly
    main()

    # 4. Intercept the standard console terminal print buffers using capsys
    captured_output = capsys.readouterr()

    # Clean up trailing whitespace and isolate rows
    stdout_lines = captured_output.out.strip().split("\n")

    # 5. Execute structural validations against the emitted JSON Lines payload contract
    assert len(stdout_lines) == 1, "The pipeline loop should emit exactly one row per valid input ID."

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]


def test_extract_pipelien_error_handling(monkeypatch, capsys):
    """
    Verifies that the main loop handles exceptions without returning
    anything to stdout and logs the error.
    """

    def stubbed_fetch_raises(self, video_id):
        """
        Simulates an error in retrieving any video ID
        """
        raise Exception(f"Fetch Failure for Video: {video_id}")
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_raises)

    input_stream = io.StringIO("this_is_a_bad_video_id\n")
    monkeypatch.setattr(sys, "stdin", input_stream)

    #The Exception below should not be triggered
    try:
        main()
    except Exception:
        pytest.fail("Main Allowed an Exception to be returned to stdout")

    captured_output = capsys.readouterr()
    assert captured_output.out.strip() == "", ("Nothing should be printed to stdout when the fetch process fails")


def test_extract_in_batch_success(monkeypatch, capsys):
    """
    Verifies the main loop executes multiple video ID's in a batch and returns
    one JSON line per ID.
    """

    def stubbed_fetch_route(self, video_id):
        class DynamicMockTranscript:
            def to_raw_data(inner_self):
                return [{"start": 0.0, "text": f" Transcript for {video_id}"}]
        return DynamicMockTranscript()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)


    #Feed 2 Valid Video ID's
    input_stream = io.StringIO("test_string\ntester_1234\n")
    monkeypatch.setattr(sys, "stdin", input_stream)

    main()

    output = capsys.readouterr()
    stdout_lines = output.out.strip().split('\n')

    ##Confrim the correct Lines were Output
    first_line = json.loads(stdout_lines[0])
    second_line = json.loads(stdout_lines[1])

    assert first_line['video_id'] == 'test_string'
    assert second_line['video_id'] == 'tester_1234'

    assert 'test_string' in first_line['raw_text']
    assert 'tester_1234' in second_line['raw_text']
