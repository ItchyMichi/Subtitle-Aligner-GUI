import sys
from typing import List, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction,
    QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem,
    QSplitter, QWidget, QVBoxLayout, QPushButton
)

from parser.subtitle_parser import load_subtitles, SubtitleEvent
from aligner.alignment_engine import auto_align, refine_alignment_with_anchors
from manual.manual_alignment import add_anchor
from generator.output_generator import generate_retimed_subtitles


class SubtitleRetimerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subtitle Retimer")
        self.resize(1000, 600)

        # 1. Create menus/toolbars
        self._create_actions()
        self._create_menu()

        # 2. Create central widgets
        self.ai_table = QTableWidget()
        self.human_table = QTableWidget()
        self._configure_tables()

        self.splitter = QSplitter()
        self.splitter.addWidget(self.ai_table)
        self.splitter.addWidget(self.human_table)

        # 3. Layout
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)

        # 4. Buttons for Align, Link, Save
        button_layout = QWidget()
        btn_layout = QVBoxLayout()
        self.align_btn = QPushButton("Auto-Align")
        self.link_btn = QPushButton("Link Selected Lines")
        self.save_btn = QPushButton("Save Output")
        btn_layout.addWidget(self.align_btn)
        btn_layout.addWidget(self.link_btn)
        btn_layout.addWidget(self.save_btn)
        button_layout.setLayout(btn_layout)
        layout.addWidget(button_layout)

        container.setLayout(layout)
        self.setCentralWidget(container)

        # 5. State variables
        self.ai_events: List[SubtitleEvent] = []
        self.human_events: List[SubtitleEvent] = []
        self.alignment: List[Tuple[int, int]] = []
        self.anchors: List[Tuple[int, int]] = []

        # 6. Connect signals
        self.align_btn.clicked.connect(self.on_auto_align)
        self.link_btn.clicked.connect(self.on_link_lines)
        self.save_btn.clicked.connect(self.on_save_output)

    def _create_actions(self):
        # File → Open AI Subtitles
        self.open_ai_action = QAction("Open AI Subtitles", self)
        self.open_human_action = QAction("Open Human Subtitles", self)
        self.exit_action = QAction("Exit", self)

        self.open_ai_action.triggered.connect(self.on_open_ai)
        self.open_human_action.triggered.connect(self.on_open_human)
        self.exit_action.triggered.connect(self.close)

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.open_ai_action)
        file_menu.addAction(self.open_human_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

    def _configure_tables(self):
        # Each table has 3 columns: Index, Timestamp, Text
        for table in (self.ai_table, self.human_table):
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["#", "Time", "Text"])
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)

    def on_open_ai(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open AI subtitle (.srt/.vtt)", "", "Subtitles (*.srt *.vtt)")
        if not path:
            return
        try:
            self.ai_events = load_subtitles(path)
            self._populate_table(self.ai_table, self.ai_events)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load AI subtitles:\n{e}")

    def on_open_human(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Human subtitle (.srt/.vtt)", "", "Subtitles (*.srt *.vtt)")
        if not path:
            return
        try:
            self.human_events = load_subtitles(path)
            self._populate_table(self.human_table, self.human_events)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load Human subtitles:\n{e}")

    def _populate_table(self, table: QTableWidget, events: List[SubtitleEvent]):
        table.setRowCount(len(events))
        for i, ev in enumerate(events):
            idx_item = QTableWidgetItem(str(ev.index))
            time_item = QTableWidgetItem(f"{ev.start:.3f} → {ev.end:.3f}")
            text_item = QTableWidgetItem(ev.text)
            table.setItem(i, 0, idx_item)
            table.setItem(i, 1, time_item)
            table.setItem(i, 2, text_item)
        table.resizeColumnsToContents()

    def on_auto_align(self):
        if not self.ai_events or not self.human_events:
            QMessageBox.warning(self, "Warning", "Load both AI and Human subtitles first.")
            return
        try:
            self.alignment = auto_align(self.ai_events, self.human_events)
            # Highlight matches in tables (optional—just highlight first matched pair to show it worked)
            for human_idx, ai_idx in self.alignment:
                self.human_table.selectRow(human_idx)
                self.ai_table.selectRow(ai_idx)
                break
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Auto-alignment failed:\n{e}")

    def on_link_lines(self):
        # User must have selected one row in each table
        ai_sel = self.ai_table.currentRow()
        human_sel = self.human_table.currentRow()
        if ai_sel < 0 or human_sel < 0:
            QMessageBox.warning(self, "Warning", "Select one line in each table to link.")
            return
        try:
            self.anchors = add_anchor(self.anchors, ai_sel, human_sel)
            # Recompute alignment with anchors
            self.alignment = refine_alignment_with_anchors(self.ai_events, self.human_events, self.anchors)
            # Highlight the newly anchored line
            self.ai_table.selectRow(ai_sel)
            self.human_table.selectRow(human_sel)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add anchor:\n{e}")

    def on_save_output(self):
        if not (self.ai_events and self.human_events and self.alignment):
            QMessageBox.warning(self, "Warning", "You must load both subtitles and run alignment first.")
            return
        out_path, _ = QFileDialog.getSaveFileName(self, "Save Retimed Subtitles", "", "Subtitles (*.srt *.vtt)")
        if not out_path:
            return
        try:
            generate_retimed_subtitles(self.ai_events, self.human_events, self.alignment, out_path)
            QMessageBox.information(self, "Success", f"Saved retimed subtitles to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save output:\n{e}")


def main():
    app = QApplication(sys.argv)
    window = SubtitleRetimerMainWindow()
    window.show()
    # In PyQt5, exec_ is used; for PyQt6 exec(). We'll use exec_ for compatibility.
    try:
        sys.exit(app.exec())
    except AttributeError:
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
