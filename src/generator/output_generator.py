"""Utilities for writing aligned subtitles."""

from typing import List, Tuple, Dict
from parser.subtitle_parser import SubtitleEvent, save_subtitles


def _split_durations(start: float, end: float, lengths: List[int]) -> List[Tuple[float, float]]:
    """Split a time span proportionally among lengths."""
    duration = end - start
    if duration < 0:
        duration = 0
    total_length = sum(lengths)
    if total_length == 0:
        # fall back to even split
        total_length = len(lengths)
        lengths = [1] * len(lengths)
    result = []
    current = start
    for length in lengths:
        portion = duration * (length / total_length)
        next_t = current + portion
        result.append((current, next_t))
        current = next_t
    return result


def generate_retimed_subtitles(
    ai_events: List[SubtitleEvent],
    human_events: List[SubtitleEvent],
    alignment: List[Tuple[int, int]],
    out_path: str,
) -> None:
    """Generate a new subtitle file using an alignment map.

    The ``alignment`` list contains ``(human_index, ai_index)`` tuples.  The text
    for each human subtitle is copied while the timing comes from its aligned AI
    subtitle(s).

    * When an AI event matches multiple human events, its duration is split
      proportionally by human text length.
    * When a human event aligns to multiple AI events, those AI time spans are
      merged.
    * Human events without alignment are ignored.
    """

    # Build mapping structures
    ai_to_humans: Dict[int, List[int]] = {}
    human_to_ais: Dict[int, List[int]] = {}
    for human_idx, ai_idx in alignment:
        ai_to_humans.setdefault(ai_idx, []).append(human_idx)
        human_to_ais.setdefault(human_idx, []).append(ai_idx)

    # Pre-compute splits for AI events with multiple human matches
    split_map: Dict[Tuple[int, int], Tuple[float, float]] = {}
    for ai_idx, human_list in ai_to_humans.items():
        ai_event = ai_events[ai_idx]
        if len(human_list) == 1:
            split_map[(human_list[0], ai_idx)] = (ai_event.start, ai_event.end)
        else:
            lengths = [len(human_events[h].text) for h in human_list]
            segments = _split_durations(ai_event.start, ai_event.end, lengths)
            for h_idx, seg in zip(human_list, segments):
                split_map[(h_idx, ai_idx)] = seg

    output_events: List[SubtitleEvent] = []
    processed = set()
    for human_idx, ai_list in human_to_ais.items():
        if human_idx in processed:
            continue
        if not ai_list:
            continue  # skip unmatched human events
        if len(ai_list) == 1:
            ai_idx = ai_list[0]
            start, end = split_map.get((human_idx, ai_idx), (ai_events[ai_idx].start, ai_events[ai_idx].end))
        else:
            # Merge span across all aligned AI events
            starts = [ai_events[i].start for i in ai_list]
            ends = [ai_events[i].end for i in ai_list]
            start, end = min(starts), max(ends)
        output_events.append(SubtitleEvent(start=start, end=end, text=human_events[human_idx].text))
        processed.add(human_idx)

    save_subtitles(output_events, out_path)
