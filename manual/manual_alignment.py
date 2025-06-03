from typing import List, Tuple


def add_anchor(
    anchors: List[Tuple[int, int]],
    ai_index: int,
    human_index: int
) -> List[Tuple[int, int]]:

    """Return a new list of anchors with (ai_index, human_index) appended, unless it already exists.
    Raises ValueError if the anchor conflicts with an existing anchor."""

    """
    Return a new list of anchors with (ai_index, human_index) appended, unless it already exists.
    Raises ValueError if the anchor conflicts with an existing anchor (e.g. same ai_index mapped to two human_indices).
    """

    if not validate_anchors(anchors):
        raise ValueError("Invalid anchors list")

    for ai, human in anchors:
        if ai == ai_index and human == human_index:
            # anchor already present
            return anchors
        if ai == ai_index and human != human_index:
            raise ValueError(
                f"AI index {ai_index} already mapped to human index {human}"
            )
        if human == human_index and ai != ai_index:
            raise ValueError(
                f"Human index {human_index} already mapped to ai index {ai}"
            )

    return anchors + [(ai_index, human_index)]


def remove_anchor(
    anchors: List[Tuple[int, int]],
    ai_index: int,
    human_index: int
) -> List[Tuple[int, int]]:

    """Return a list of anchors with the specified pair removed. If the pair isn't present, return anchors unchanged."""

    """
    Return a list of anchors with the specified pair removed. If the pair isn't present, return anchors unchanged.
    """

    if (ai_index, human_index) not in anchors:
        return anchors

    return [pair for pair in anchors if pair != (ai_index, human_index)]


def validate_anchors(
    anchors: List[Tuple[int, int]]
) -> bool:

    """Check that no ai_index or human_index appears more than once across all anchors."""

    """
    Check that no ai_index or human_index appears more than once across all anchors.
    """

    ai_seen = set()
    human_seen = set()
    for ai, human in anchors:
        if ai in ai_seen or human in human_seen:
            return False
        ai_seen.add(ai)
        human_seen.add(human)
    return True
