import importlib
import sys
from pathlib import Path
import pytest

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

pytest.importorskip("PyQt5")

def test_import_main_window():
    module = importlib.import_module('gui.gui_frontend')
    cls = getattr(module, 'SubtitleRetimerMainWindow')
    assert cls is not None
