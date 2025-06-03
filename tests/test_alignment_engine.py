import os, sys
sys.path.insert(0, os.path.abspath("src"))
import unittest
from parser.subtitle_parser import SubtitleEvent
from aligner.alignment_engine import auto_align, refine_alignment_with_anchors


class TestAlignmentEngine(unittest.TestCase):
    def setUp(self):
        self.ai = [
            SubtitleEvent(None, None, "Line one"),
            SubtitleEvent(None, None, "Line two"),
            SubtitleEvent(None, None, "Line three"),
            SubtitleEvent(None, None, "Line four"),
            SubtitleEvent(None, None, "Line five"),
        ]
        self.human = [
            SubtitleEvent(None, None, "Line one"),
            SubtitleEvent(None, None, "Line two"),
            SubtitleEvent(None, None, "Different line"),
            SubtitleEvent(None, None, "Line three"),
            SubtitleEvent(None, None, "Line four"),
            SubtitleEvent(None, None, "Line five"),
        ]

    def test_auto_align(self):
        result = auto_align(self.ai, self.human)
        expected = [(0, 0), (1, 1), (3, 2), (4, 3), (5, 4)]
        self.assertEqual(result, expected)

    def test_refine_with_anchor(self):
        anchors = [(2, 3)]  # ai index 2 aligns to human index 3
        result = refine_alignment_with_anchors(self.ai, self.human, anchors)
        expected = [(0, 0), (1, 1), (3, 2), (4, 3), (5, 4)]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
