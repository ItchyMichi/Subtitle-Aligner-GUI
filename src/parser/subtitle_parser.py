from dataclasses import dataclass
from typing import List
import os


@dataclass
class SubtitleEvent:
    index: int
    start: float  # seconds
    end: float    # seconds
    text: str



def _parse_timestamp(ts: str) -> float:
    ts = ts.replace(',', '.')
    hms, ms = ts.split('.') if '.' in ts else (ts, '0')
    h, m, s = [int(x) for x in hms.split(':')]
    return h * 3600 + m * 60 + s + int(ms) / (1000 if len(ms) > 2 else 1)


def _format_timestamp(seconds: float, as_vtt: bool = False) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    sep = '.' if as_vtt else ','
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def load_subtitles(path: str) -> List[SubtitleEvent]:
    ext = os.path.splitext(path)[1].lower()
    events: List[SubtitleEvent] = []
    with open(path, encoding='utf-8') as f:
        raw_lines = [line.rstrip('\n') for line in f]

    i = 0
    idx = 1
    if ext == '.vtt' and raw_lines and raw_lines[0].startswith('WEBVTT'):
        i = 1

    while i < len(raw_lines):
        line = raw_lines[i].strip()
        if not line:
            i += 1
            continue

        if ext == '.srt' and line.isdigit():
            i += 1
            if i >= len(raw_lines):
                break
            line = raw_lines[i].strip()

        times = line
        parts = times.split('-->')
        if len(parts) != 2:
            raise ValueError(f"Invalid timestamp line: {times}")
        start_ts, end_ts = [t.strip() for t in parts]
        i += 1
        text_lines = []
        while i < len(raw_lines) and raw_lines[i].strip() != '':
            text_lines.append(raw_lines[i].rstrip('\n').strip())
            i += 1
        text = '\n'.join(text_lines)
        start = _parse_timestamp(start_ts)
        end = _parse_timestamp(end_ts)
        events.append(SubtitleEvent(idx, start, end, text))
        idx += 1
        while i < len(raw_lines) and raw_lines[i].strip() == '':
            i += 1
    return events


def save_subtitles(events: List[SubtitleEvent], path: str) -> None:
    ext = os.path.splitext(path)[1].lower()
    as_vtt = ext == '.vtt'
    lines = []
    if as_vtt:
        lines.append('WEBVTT')
    for ev in events:
        if not as_vtt:
            lines.append(str(ev.index))
        start = _format_timestamp(ev.start, as_vtt)
        end = _format_timestamp(ev.end, as_vtt)
        lines.append(f"{start} --> {end}")
        lines.append(ev.text)
        lines.append('')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

