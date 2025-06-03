from dataclasses import dataclass
from typing import List

@dataclass
class SubtitleEvent:
    start: float
    end: float
    text: str


def load_subtitles(path: str) -> List[SubtitleEvent]:
    """Load subtitles from a simple tab-separated format."""
    events = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 3:
                continue
            start, end, text = parts[0], parts[1], '\t'.join(parts[2:])
            events.append(SubtitleEvent(float(start), float(end), text))
    return events


def save_subtitles(events: List[SubtitleEvent], path: str) -> None:
    """Save subtitles to a simple tab-separated format."""
    with open(path, 'w', encoding='utf-8') as f:
        for ev in events:
            f.write(f"{ev.start}\t{ev.end}\t{ev.text}\n")
import os
import pysubs2

@dataclass
class SubtitleEvent:
    index: int
    start: float  # seconds
    end: float    # seconds
    text: str

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
