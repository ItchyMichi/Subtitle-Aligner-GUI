from typing import List, Tuple
from parser.subtitle_parser import SubtitleEvent

def auto_align(ai_events: List[SubtitleEvent], human_events: List[SubtitleEvent]) -> List[Tuple[int, int]]:
    length = min(len(ai_events), len(human_events))
    return [(i, i) for i in range(length)]

def refine_alignment_with_anchors(ai_events: List[SubtitleEvent], human_events: List[SubtitleEvent], anchors: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if anchors:
        return anchors
    return auto_align(ai_events, human_events)
