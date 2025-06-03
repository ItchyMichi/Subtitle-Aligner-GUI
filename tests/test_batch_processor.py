import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import os
import tempfile
from parser.subtitle_parser import SubtitleEvent, save_subtitles, load_subtitles
from batch.batch_processor import process_batch


def create_sub_file(path, texts):
    events = []
    time = 0.0
    for idx, text in enumerate(texts, start=1):
        events.append(SubtitleEvent(index=idx, start=time, end=time + 1.0, text=text))
        time += 1.0
    save_subtitles(events, path)


def test_process_batch():
    with tempfile.TemporaryDirectory() as tmpdir:
        pair_configs = []
        for idx in range(3):
            ai_path = os.path.join(tmpdir, f"ai{idx}.srt")
            human_path = os.path.join(tmpdir, f"human{idx}.srt")
            output_path = os.path.join(tmpdir, f"out{idx}.srt")
            create_sub_file(ai_path, [f"a{idx}1", f"a{idx}2"])
            create_sub_file(human_path, [f"h{idx}1", f"h{idx}2"])
            pair_configs.append({"ai_path": ai_path, "human_path": human_path, "output_path": output_path})
        results = process_batch(pair_configs)
        assert results == [True, True, True]
        for cfg in pair_configs:
            assert os.path.exists(cfg["output_path"])
            events = load_subtitles(cfg["output_path"])
            assert len(events) == 2
