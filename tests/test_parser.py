import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from parser.subtitle_parser import SubtitleEvent, load_subtitles, save_subtitles


def create_srt_file(tmp_path: Path) -> Path:
    content = """1
00:00:01,000 --> 00:00:02,000
Hello

2
00:00:02,500 --> 00:00:04,000
World
"""
    p = tmp_path / "sample.srt"
    p.write_text(content, encoding="utf-8")
    return p


def create_vtt_file(tmp_path: Path) -> Path:
    content = """WEBVTT

00:00:01.000 --> 00:00:02.000
Hello

00:00:02.500 --> 00:00:04.000
World
"""
    p = tmp_path / "sample.vtt"
    p.write_text(content, encoding="utf-8")
    return p


def create_multiline_srt_file(tmp_path: Path) -> Path:
    content = """1
00:00:01,000 --> 00:00:03,000
Hello
World

2
00:00:04,000 --> 00:00:05,000
End
"""
    p = tmp_path / "multi.srt"
    p.write_text(content, encoding="utf-8")
    return p


def create_bom_srt_file(tmp_path: Path) -> Path:
    """Create an SRT file that begins with a UTF-8 BOM."""
    content = "\ufeff1\n00:00:01,000 --> 00:00:02,000\nHello\n\n2\n00:00:02,500 --> 00:00:04,000\nWorld"
    p = tmp_path / "bom.srt"
    p.write_text(content, encoding="utf-8")
    return p


def test_load_subtitles_srt(tmp_path):
    path = create_srt_file(tmp_path)
    events = load_subtitles(str(path))
    assert events == [
        SubtitleEvent(1, 1.0, 2.0, "Hello"),
        SubtitleEvent(2, 2.5, 4.0, "World"),
    ]


def test_load_subtitles_vtt(tmp_path):
    path = create_vtt_file(tmp_path)
    events = load_subtitles(str(path))
    assert events == [
        SubtitleEvent(1, 1.0, 2.0, "Hello"),
        SubtitleEvent(2, 2.5, 4.0, "World"),
    ]


def test_save_subtitles_roundtrip_srt(tmp_path):
    events = [
        SubtitleEvent(1, 0.0, 1.0, "A"),
        SubtitleEvent(2, 1.5, 2.0, "B"),
    ]
    path = tmp_path / "out.srt"
    save_subtitles(events, str(path))
    loaded = load_subtitles(str(path))
    assert loaded == events


def test_save_subtitles_roundtrip_vtt(tmp_path):
    events = [
        SubtitleEvent(1, 0.0, 1.0, "A"),
        SubtitleEvent(2, 1.5, 2.0, "B"),
    ]
    path = tmp_path / "out.vtt"
    save_subtitles(events, str(path))
    loaded = load_subtitles(str(path))
    assert loaded == events


def test_load_multiline_subtitles(tmp_path):
    path = create_multiline_srt_file(tmp_path)
    events = load_subtitles(str(path))
    assert events == [
        SubtitleEvent(1, 1.0, 3.0, "Hello\nWorld"),
        SubtitleEvent(2, 4.0, 5.0, "End"),
    ]


def test_load_subtitles_with_bom(tmp_path):
    path = create_bom_srt_file(tmp_path)
    events = load_subtitles(str(path))
    assert events == [
        SubtitleEvent(1, 1.0, 2.0, "Hello"),
        SubtitleEvent(2, 2.5, 4.0, "World"),
    ]
