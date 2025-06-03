from typing import List, Tuple
from parser.subtitle_parser import SubtitleEvent, save_subtitles

def generate_retimed_subtitles(ai_events: List[SubtitleEvent], human_events: List[SubtitleEvent], alignment: List[Tuple[int, int]], output_path: str) -> None:
    output_events: List[SubtitleEvent] = []
    for out_index, (ai_idx, human_idx) in enumerate(alignment, start=1):
        if ai_idx < len(ai_events) and human_idx < len(human_events):
            ai_event = ai_events[ai_idx]
            human_event = human_events[human_idx]
            output_events.append(
                SubtitleEvent(
                    index=out_index,
                    start=human_event.start,
                    end=human_event.end,
                    text=ai_event.text,
                )
            )
    save_subtitles(output_events, output_path)
