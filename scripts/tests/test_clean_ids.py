import sys
import os
import platform
import io
import pytest
from bin.clean_ids import main, is_valid_youtube_id

def test_script_execution(monkeypatch, capsys):
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
    fake_input = io.StringIO("thisshouldfail\n-23pass8901\nerrorhere\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == "-23pass8901\n"

def test_all_bad_inputs(monkeypatch, capsys):
    fake_input = io.StringIO("thisshouldfail\nerrorhere\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""

def test_char_length(monkeypatch, capsys):
    assert is_valid_youtube_id("kwtlyowir_") is False #10 Chars
    assert is_valid_youtube_id("kwtlyowir_t") is True #11 Chars
    assert is_valid_youtube_id("kwtlyowir_te") is False #12 Chars

def test_os():
    os_version = platform.version()
    assert "Ubuntu" in os_version

def test_python_version():
    major_version = sys.version_info.major
    minor_version = sys.version_info.minor
    assert major_version >=3
    assert minor_version >=.9


@pytest.mark.xfail(reason="Special Chars Should Fail.")
def test_digits_only_should_fail():
    assert is_valid_youtube_id("!@#$%^&*()=") is False


@pytest.mark.skip(reason="Playlist ID support not built.")
def test_playlist_id():
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
    assert is_valid_youtube_id(video_id) is expected
