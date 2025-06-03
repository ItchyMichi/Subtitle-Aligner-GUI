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
