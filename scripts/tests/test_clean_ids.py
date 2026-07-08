"""
Test suite to verify the clean_ids.py process is working
as expected.

Uses Monkeypatch to feed a set of tests through stdin
to the clean_ids.py script. These tests verify that youtube
video ids meet required criteria.
"""
import sys
import platform
import io
import pytest
from bin.clean_ids import main, is_valid_youtube_id

def test_script_execution(monkeypatch, capsys):
    """
    Passes a valid string through stdin using monkeypatch
    and verifies that the string is echoed back through stdout.
    """

    # 1. Simulate the standard input data
    # We use io.StringIO to make a string act like a readable stream/file
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)

    # 2. Run the script's main logic
    main()

    # 3. Capture the printed output
    captured = capsys.readouterr()

    # 4. Assert that the data was modified correctly
    assert captured.out == "kcFsuxaJ1es\n"

def test_good_bad_alternating(monkeypatch, capsys):
    """
    Passes two valid ids and one invalidto stdin using monkeypatch. Verifies
    that only the valid ids are returned to stdout.
    """

    fake_input = io.StringIO("thisshouldfail\n-23pass8901\nerrorhere\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == "-23pass8901\n"

def test_all_bad_inputs(monkeypatch, capsys):
    """
    Passes all invalid inputs to stdin using monkeypatch, confirming
    that no id strings are returned to stdout.
    """
    fake_input = io.StringIO("thisshouldfail\nerrorhere\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""

def test_char_length():
    """
    Passes three stings of varying length to stdin using monkeypatch,
    confirming that only the string that meets the 11 char length is
    returned to stdout.
    """
    assert is_valid_youtube_id("kwtlyowir_") is False #10 Chars
    assert is_valid_youtube_id("kwtlyowir_t") is True #11 Chars
    assert is_valid_youtube_id("kwtlyowir_te") is False #12 Chars

def test_os():
    """
    Verifies that the user is on the Ubuntu system.
    """
    os_version = platform.version()
    assert "Ubuntu" in os_version

def test_python_version():
    """
    Verifies that the user is on python 3.9 or later.
    """
    major_version = sys.version_info.major
    minor_version = sys.version_info.minor
    assert major_version >=3
    assert minor_version >=.9


@pytest.mark.xfail(reason="Special Chars Should Fail.")
def test_digits_only_should_fail():
    """
    Test confirming that a string of only 11 special characters fails.
    """
    assert is_valid_youtube_id("!@#$%^&*()=") is False


@pytest.mark.skip(reason="Playlist ID support not built.")
def test_playlist_id():
    """
    Test confirming that a string meeting the criteria for a playlist fails.
    This test is set as a skip for a future feature.
    """
    assert is_valid_youtube_id("PLbpi6ZahtOH6Ar_3GPy3worksPLbpi6Z") is False

@pytest.mark.parametrize("video_id, expected", [
    ("kcFsuxaJ1es", True),   # valid
    ("dQw4w9WgXcQ", True),   # valid
    ("asd123",      False),  # short
    ("!!invalid!!",  False),  # special chars
    ("kwtlyowir_te", False),  # 12 chars
    ("kwtlyowir_",  False),  # 10 chars
    ("___--------", True),   # underscores and hyphens
])
def test_valid_youtube_id_parametrized(video_id, expected):
    """
    Test that runs multiple strings through stdin using a
    parameterize pytest function, confirming that the results
    match expected values.
    """
    assert is_valid_youtube_id(video_id) is expected
