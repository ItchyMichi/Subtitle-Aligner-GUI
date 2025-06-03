from dataclasses import dataclass
from typing import List
import os

import pysubs2


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
        lines = [line.strip() for line in f.readlines() if line.strip()]
    i = 0
    idx = 1
    if ext == '.vtt' and lines and lines[0].startswith('WEBVTT'):
        lines = lines[1:]
    while i < len(lines):
        if ext == '.srt':
            # skip numeric counter
            if lines[i].isdigit():
                i += 1
        times = lines[i]
        text = lines[i + 1]
        start_ts, end_ts = [t.strip() for t in times.split('-->')]
        start = _parse_timestamp(start_ts)
        end = _parse_timestamp(end_ts)
        events.append(SubtitleEvent(idx, start, end, text))
        idx += 1
        i += 2
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

def load_subtitles(path: str) -> List[SubtitleEvent]:
    """Read .srt or .vtt from `path` using pysubs2 and convert to List[SubtitleEvent]."""
    subs = pysubs2.load(path)
    events: List[SubtitleEvent] = []
    for idx, line in enumerate(subs, start=1):
        events.append(
            SubtitleEvent(
                index=idx,
                start=line.start / 1000.0,
                end=line.end / 1000.0,
                text=line.text,
            )
        )
    return events

def save_subtitles(events: List[SubtitleEvent], path: str) -> None:
    """Write `events` in SRT or VTT format based on path extension."""
    subs = pysubs2.SSAFile()
    for ev in events:
        subs.events.append(
            pysubs2.SSAEvent(start=int(ev.start * 1000), end=int(ev.end * 1000), text=ev.text)
        )

    ext = os.path.splitext(path)[1].lower()
    fmt = "srt" if ext == ".srt" else "vtt"
    subs.save(path, format_=fmt)
