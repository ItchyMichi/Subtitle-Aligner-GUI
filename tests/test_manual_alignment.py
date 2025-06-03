import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.manual.manual_alignment import add_anchor, remove_anchor, validate_anchors


def test_add_anchor_empty():
    anchors = []
    result = add_anchor(anchors, 0, 0)
    assert result == [(0, 0)]


def test_add_anchor_duplicate():
    anchors = [(1, 2)]
    result = add_anchor(anchors, 1, 2)
    assert result == anchors


def test_add_anchor_conflict():
    anchors = [(1, 2)]
    with pytest.raises(ValueError):
        add_anchor(anchors, 1, 3)


def test_remove_anchor_exists():
    anchors = [(0, 0), (1, 1)]
    result = remove_anchor(anchors, 0, 0)
    assert result == [(1, 1)]


def test_remove_anchor_not_exists():
    anchors = [(0, 0)]
    result = remove_anchor(anchors, 1, 1)
    assert result == anchors


def test_validate_anchors():
    assert validate_anchors([(0, 0), (1, 1)])
    assert not validate_anchors([(0, 0), (0, 1)])
    assert not validate_anchors([(0, 0), (1, 0)])
