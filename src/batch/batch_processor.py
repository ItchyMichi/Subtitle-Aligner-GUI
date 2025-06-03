import os
from typing import List, Dict, Tuple
from parser.subtitle_parser import load_subtitles
from aligner.alignment_engine import auto_align, refine_alignment_with_anchors
from generator.output_generator import generate_retimed_subtitles


def process_pair(
    ai_path: str,
    human_path: str,
    output_path: str,
    anchors: List[Tuple[int,int]] = None
) -> bool:
    """
    1. Load ai_events = load_subtitles(ai_path)
    2. Load human_events = load_subtitles(human_path)
    3. If anchors provided: alignment = refine_alignment_with_anchors(...)
       else: alignment = auto_align(...)
    4. Call generate_retimed_subtitles(ai_events, human_events, alignment, output_path)
    5. Return True on success, False on any exception.
    """
    try:
        ai_events = load_subtitles(ai_path)
        human_events = load_subtitles(human_path)
        if anchors:
            alignment = refine_alignment_with_anchors(ai_events, human_events, anchors)
        else:
            alignment = auto_align(ai_events, human_events)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        generate_retimed_subtitles(ai_events, human_events, alignment, output_path)
        return True
    except Exception:
        return False


def process_batch(configs: List[Dict]) -> List[bool]:
    """
    Given a list of configs, each { "ai_path": str, "human_path": str, "output_path": str },
    call process_pair for each and return a list of booleans indicating success/failure.
    """
    results = []
    for cfg in configs:
        result = process_pair(cfg["ai_path"], cfg["human_path"], cfg["output_path"])
        results.append(result)
    return results
