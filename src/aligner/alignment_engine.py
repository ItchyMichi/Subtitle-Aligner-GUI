try:
    from rapidfuzz import fuzz as _fuzz_ratio
    def fuzz_ratio(a, b):
        return _fuzz_ratio(a, b)
except ModuleNotFoundError:
    import difflib
    def fuzz_ratio(a, b):
        return difflib.SequenceMatcher(None, a, b).ratio() * 100

from typing import List, Tuple
from parser.subtitle_parser import SubtitleEvent


def auto_align(
    ai_events: List[SubtitleEvent],
    human_events: List[SubtitleEvent],
    similarity_threshold: float = 80.0,
    max_line_offset: int = 15
) -> List[Tuple[int, int]]:
    """Return list of ``(human_idx, ai_idx)`` pairs for text matches.

    Each human line is compared against AI lines within ``±max_line_offset``.
    The candidate with the highest fuzzy ratio above ``similarity_threshold`` is
    selected. Lines without a suitable match are skipped. Returned indices are
    sorted by human line so that ``ai_idx`` values strictly increase.
    Raises ``ValueError`` if either list is empty.
    """
    if not ai_events or not human_events:
        raise ValueError("Subtitle event lists must not be empty")

    alignment: List[Tuple[int, int]] = []
    last_ai_idx = -1

    for h_idx, h_event in enumerate(human_events):
        best_idx = None
        best_score = similarity_threshold
        start = max(0, h_idx - max_line_offset)
        end = min(len(ai_events), h_idx + max_line_offset + 1)

        for ai_idx in range(start, end):
            if ai_idx <= last_ai_idx:
                continue
            score = fuzz_ratio(h_event.text, ai_events[ai_idx].text)
            if score >= best_score:
                if score > best_score or best_idx is None:
                    best_score = score
                    best_idx = ai_idx
        if best_idx is not None:
            alignment.append((h_idx, best_idx))
            last_ai_idx = best_idx
    return alignment


def refine_alignment_with_anchors(
    ai_events: List[SubtitleEvent],
    human_events: List[SubtitleEvent],
    anchors: List[Tuple[int, int]],
    similarity_threshold: float = 80.0,
    max_line_offset: int = 10
) -> List[Tuple[int, int]]:
    """Realign subtitles while respecting manual anchors.

    ``anchors`` should contain ``(ai_idx, human_idx)`` tuples. The sequences are
    split at each anchor and :func:`auto_align` is run on every segment. Anchor
    pairs are preserved in the final alignment. A ``ValueError`` is raised if an
    anchor references an index outside the provided lists.
    """
    if not ai_events or not human_events:
        raise ValueError("Subtitle event lists must not be empty")

    if not anchors:
        return auto_align(ai_events, human_events, similarity_threshold, max_line_offset)

    for ai_idx, h_idx in anchors:
        if ai_idx >= len(ai_events) or h_idx >= len(human_events) or ai_idx < 0 or h_idx < 0:
            raise ValueError("Anchor index out of range")

    combined: List[Tuple[int, int]] = []
    anchors_sorted = sorted(anchors, key=lambda p: (p[1], p[0]))
    prev_ai = -1
    prev_h = -1

    for ai_idx, h_idx in anchors_sorted:
        seg_ai = ai_events[prev_ai + 1: ai_idx]
        seg_h = human_events[prev_h + 1: h_idx]
        if seg_ai and seg_h:
            seg_res = auto_align(seg_ai, seg_h, similarity_threshold, max_line_offset)
            for h_off, ai_off in seg_res:
                combined.append((h_off + prev_h + 1, ai_off + prev_ai + 1))
        combined.append((h_idx, ai_idx))
        prev_ai = ai_idx
        prev_h = h_idx

    seg_ai = ai_events[prev_ai + 1:]
    seg_h = human_events[prev_h + 1:]
    if seg_ai and seg_h:
        seg_res = auto_align(seg_ai, seg_h, similarity_threshold, max_line_offset)
        for h_off, ai_off in seg_res:
            combined.append((h_off + prev_h + 1, ai_off + prev_ai + 1))

    return combined
