import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from generator.output_generator import generate_retimed_subtitles
from parser.subtitle_parser import SubtitleEvent, load_subtitles


def build_ai_events():
    return [
        SubtitleEvent(0.0, 2.0, "Hello"),
        SubtitleEvent(2.0, 5.0, "How are you?"),
        SubtitleEvent(5.0, 7.0, "Goodbye"),
    ]


def build_human_events():
    return [
        SubtitleEvent(0.0, 0.0, "Hello"),
        SubtitleEvent(0.0, 0.0, "How are you?"),
        SubtitleEvent(0.0, 0.0, "Goodbye"),
    ]


def test_generate_retimed_subtitles_basic(tmp_path: Path):
    ai_events = build_ai_events()
    human_events = build_human_events()
    # (human_index, ai_index)
    alignment = [(0, 0), (1, 1), (2, 2)]
    out_file = tmp_path / "out.txt"

    generate_retimed_subtitles(ai_events, human_events, alignment, str(out_file))

    result = load_subtitles(out_file)
    assert result == ai_events  # texts already match


def test_generate_retimed_subtitles_merge(tmp_path: Path):
    ai_events = build_ai_events()
    human_events = build_human_events()
    # human event 0 aligns to ai events 0 and 1 -> merged
    alignment = [(0, 0), (0, 1), (1, 2)]
    out_file = tmp_path / "merge.txt"

    generate_retimed_subtitles(ai_events, human_events, alignment, str(out_file))

    result = load_subtitles(out_file)
    assert len(result) == 2
    assert result[0].start == 0.0 and result[0].end == 5.0
    assert result[0].text == "Hello"
    assert result[1].start == 5.0 and result[1].end == 7.0
    assert result[1].text == "How are you?"
