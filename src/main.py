"""
PII Shield — Windows 11 PII Anonymizer
Modern PySide6 desktop app. Offline. No OCR. No PDF.
"""
import sys
import os
import json
import copy
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QCheckBox, QLineEdit,
    QTextEdit, QScrollArea, QFrame, QSplitter, QStackedWidget,
    QMessageBox, QRadioButton, QButtonGroup, QGroupBox,
    QSizePolicy, QToolButton, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import (
    QFont, QColor, QPalette, QIcon, QDragEnterEvent,
    QDropEvent, QTextCursor, QTextCharFormat
)

# ── our modules ──
sys.path.insert(0, os.path.dirname(__file__))
from patterns import BUILTIN_CATEGORIES
from engine import detect, apply_redactions
from file_handler import (
    read_file, write_file, extension_supported,
    suggest_output_path, suggest_report_path, SUPPORTED_EXTENSIONS
)
from audit import generate_report, save_report

# ─────────────────────────────────────────────────────────────────── #
#  Styles                                                             #
# ─────────────────────────────────────────────────────────────────── #
STYLESHEET = """
QMainWindow, QWidget#root {
    background-color: #0f1115;
    color: #f2f5f7;
}
QWidget {
    background-color: transparent;
    color: #f2f5f7;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}
QLabel {
    color: #f2f5f7;
}
QLabel#muted {
    color: #adb8c4;
    font-size: 12px;
}
QLabel#section_title {
    font-size: 16px;
    font-weight: 700;
    color: #f2f5f7;
}
QLabel#step_chip {
    background: rgba(76,194,255,0.15);
    color: #4cc2ff;
    border: 1px solid rgba(76,194,255,0.3);
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 8px 16px;
    color: #f2f5f7;
    font-weight: 600;
}
QPushButton:hover {
    background: rgba(255,255,255,0.11);
    border-color: rgba(255,255,255,0.2);
}
QPushButton:pressed {
    background: rgba(255,255,255,0.04);
}
QPushButton#primary {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(76,194,255,0.35), stop:1 rgba(76,194,255,0.18));
    border-color: rgba(76,194,255,0.4);
    color: #e8f8ff;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(76,194,255,0.5), stop:1 rgba(76,194,255,0.3));
}
QPushButton#success {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(119,224,181,0.32), stop:1 rgba(119,224,181,0.16));
    border-color: rgba(119,224,181,0.4);
    color: #d0faeb;
}
QPushButton#success:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(119,224,181,0.48), stop:1 rgba(119,224,181,0.28));
}
QPushButton#danger {
    background: rgba(255,122,122,0.12);
    border-color: rgba(255,122,122,0.3);
    color: #ffaaaa;
}
QPushButton#nav {
    background: transparent;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    text-align: left;
    color: #adb8c4;
    font-size: 13px;
}
QPushButton#nav:hover {
    background: rgba(255,255,255,0.06);
    color: #f2f5f7;
}
QPushButton#nav_active {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(76,194,255,0.2), stop:1 rgba(76,194,255,0.09));
    border: 1px solid rgba(76,194,255,0.25);
    border-radius: 12px;
    padding: 10px 14px;
    text-align: left;
    color: #f2f5f7;
    font-size: 13px;
    font-weight: 600;
}
QLineEdit {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 8px 12px;
    color: #f2f5f7;
    selection-background-color: rgba(76,194,255,0.3);
}
QLineEdit:focus {
    border-color: rgba(76,194,255,0.5);
    background: rgba(76,194,255,0.06);
}
QTextEdit {
    background: rgba(255,255,255,0.97);
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 12px;
    padding: 10px;
    color: #17212b;
    font-size: 13px;
    selection-background-color: #ffe793;
}
QCheckBox {
    spacing: 8px;
    color: #f2f5f7;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.04);
}
QCheckBox::indicator:checked {
    background: rgba(76,194,255,0.25);
    border-color: rgba(76,194,255,0.5);
}
QRadioButton {
    spacing: 8px;
    color: #f2f5f7;
}
QRadioButton::indicator {
    width: 16px; height: 16px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.04);
}
QRadioButton::indicator:checked {
    background: rgba(76,194,255,0.5);
    border-color: rgba(76,194,255,0.8);
}
QScrollArea {
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.15);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QFrame#card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px;
}
QFrame#card_accent {
    background: rgba(119,224,181,0.07);
    border: 1px solid rgba(119,224,181,0.2);
    border-radius: 16px;
}
QFrame#card_warn {
    background: rgba(255,209,102,0.07);
    border: 1px solid rgba(255,209,102,0.22);
    border-radius: 14px;
}
QFrame#sidebar {
    background: rgba(255,255,255,0.025);
    border-right: 1px solid rgba(255,255,255,0.08);
}
QFrame#titlebar {
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
QProgressBar {
    background: rgba(255,255,255,0.06);
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #4cc2ff, stop:1 #77e0b5);
    border-radius: 4px;
}
"""

# ─────────────────────────────────────────────────────────────────── #
#  Helpers                                                            #
# ─────────────────────────────────────────────────────────────────── #

def card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("card")
    return f


def make_label(text, obj_name=None, bold=False, size=None) -> QLabel:
    l = QLabel(text)
    if obj_name:
        l.setObjectName(obj_name)
    if bold or size:
        f = l.font()
        if bold:
            f.setBold(True)
        if size:
            f.setPointSize(size)
        l.setFont(f)
    return l


def make_btn(text, obj_name="", min_w=None) -> QPushButton:
    b = QPushButton(text)
    if obj_name:
        b.setObjectName(obj_name)
    if min_w:
        b.setMinimumWidth(min_w)
    return b


def separator(horizontal=True) -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine if horizontal else QFrame.VLine)
    line.setStyleSheet("background: rgba(255,255,255,0.08); border:none; max-height:1px;")
    return line


# ─────────────────────────────────────────────────────────────────── #
#  Detection worker thread                                            #
# ─────────────────────────────────────────────────────────────────── #

class DetectWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, text, enabled_ids, custom_patterns):
        super().__init__()
        self.text = text
        self.enabled_ids = enabled_ids
        self.custom_patterns = custom_patterns

    def run(self):
        try:
            findings = detect(self.text, self.enabled_ids, self.custom_patterns)
            self.finished.emit(findings)
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────────────────────────────────────────────────── #
#  Screen 1 — Upload                                                  #
# ─────────────────────────────────────────────────────────────────── #

class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card { border: 2px dashed rgba(76,194,255,0.3); "
            "border-radius: 18px; background: rgba(76,194,255,0.04); }"
        )
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        icon = make_label("📂", size=36)
        icon.setAlignment(Qt.AlignCenter)

        title = make_label("Drag & drop a file here", bold=True)
        title.setAlignment(Qt.AlignCenter)
        f = title.font(); f.setPointSize(15); title.setFont(f)

        sub = make_label("or use the Browse button below", "muted")
        sub.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(sub)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                "QFrame#card { border: 2px dashed rgba(76,194,255,0.7); "
                "border-radius: 18px; background: rgba(76,194,255,0.09); }"
            )

    def dragLeaveEvent(self, event):
        self.setStyleSheet(
            "QFrame#card { border: 2px dashed rgba(76,194,255,0.3); "
            "border-radius: 18px; background: rgba(76,194,255,0.04); }"
        )

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(
            "QFrame#card { border: 2px dashed rgba(76,194,255,0.3); "
            "border-radius: 18px; background: rgba(76,194,255,0.04); }"
        )
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                self.file_dropped.emit(path)
                break


class UploadScreen(QWidget):
    file_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        # Header
        hdr = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.addWidget(make_label("Upload File", "section_title"))
        title_col.addWidget(make_label(
            "Anonymize Word and text-based documents — fully offline", "muted"))
        hdr.addLayout(title_col)
        hdr.addStretch()
        chip = make_label("Step 1 of 4", "step_chip")
        hdr.addWidget(chip)
        root.addLayout(hdr)

        # Warning banner
        warn = QFrame()
        warn.setObjectName("card_warn")
        wl = QHBoxLayout(warn)
        wl.setContentsMargins(14, 10, 14, 10)
        wl.addWidget(make_label("⚠️  No OCR. No PDF. Text-based files only. "
                                "Scanned or image-based documents are not supported in this version."))
        root.addWidget(warn)

        # Drop zone
        self.dropzone = DropZone()
        self.dropzone.file_dropped.connect(self._on_file)
        root.addWidget(self.dropzone)

        # Browse row
        browse_row = QHBoxLayout()
        browse_row.addStretch()
        self.browse_btn = make_btn("📁  Browse files", "primary", 160)
        self.browse_btn.clicked.connect(self._browse)
        browse_row.addWidget(self.browse_btn)
        browse_row.addStretch()
        root.addLayout(browse_row)

        # File info card
        self.file_card = card()
        fl = QVBoxLayout(self.file_card)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(8)
        self.file_label = make_label("No file selected", "muted")
        fl.addWidget(self.file_label)
        root.addWidget(self.file_card)

        # Supported formats
        sup_card = card()
        sl = QVBoxLayout(sup_card)
        sl.setContentsMargins(16, 12, 16, 14)
        sl.setSpacing(6)
        sl.addWidget(make_label("Supported file formats", bold=True))
        sl.addWidget(make_label(
            "  .docx  .doc  .txt  .md  .markdown  .rtf  .csv  .log"
            "  .xml  .json  .ini  .cfg  .yaml  .yml  .toml", "muted"))
        not_sup = make_label("  ✗  Not supported: .pdf, scanned images, any OCR-required file")
        not_sup.setStyleSheet("color: #ff9999;")
        sl.addWidget(not_sup)
        root.addWidget(sup_card)

        root.addStretch()

        # Footer buttons
        footer = QHBoxLayout()
        footer.addStretch()
        self.next_btn = make_btn("Configure Detection  →", "primary", 200)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self._next)
        footer.addWidget(self.next_btn)
        root.addLayout(footer)

        self._path = None

    def _browse(self):
        exts = " ".join(f"*{e}" for e in sorted(SUPPORTED_EXTENSIONS))
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "",
            f"Supported files ({exts});;All files (*.*)"
        )
        if path:
            self._on_file(path)

    def _on_file(self, path):
        if not extension_supported(path):
            QMessageBox.warning(
                self, "Unsupported file",
                f"'{Path(path).suffix}' files are not supported.\n\n"
                "Version 1 supports Word and plain-text formats only.\n"
                "No PDF. No scanned documents. No OCR."
            )
            return
        self._path = path
        name = Path(path).name
        size_kb = os.path.getsize(path) // 1024
        self.file_label.setText(
            f"✅  {name}   ({size_kb} KB)   ready to process"
        )
        self.file_label.setStyleSheet("color: #77e0b5; font-weight: 600;")
        self.next_btn.setEnabled(True)

    def _next(self):
        if self._path:
            self.file_selected.emit(self._path)

    def reset(self):
        self._path = None
        self.file_label.setText("No file selected")
        self.file_label.setStyleSheet("")
        self.next_btn.setEnabled(False)


# ─────────────────────────────────────────────────────────────────── #
#  Screen 2 — Detect Settings                                         #
# ─────────────────────────────────────────────────────────────────── #

class DetectScreen(QWidget):
    run_detection = Signal(list, list, int)   # enabled_ids, custom_pats, mode

    MODES = ["Conservative (high precision — fewer false positives)",
             "Balanced",
             "Broad (high recall — catches more, may include false positives)"]

    def __init__(self):
        super().__init__()
        self._checkboxes = {}
        self._custom_rows = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        col = QVBoxLayout()
        col.addWidget(make_label("Configure Detection", "section_title"))
        col.addWidget(make_label(
            "Choose which PII categories to detect. All are enabled by default.", "muted"))
        hdr.addLayout(col)
        hdr.addStretch()
        hdr.addWidget(make_label("Step 2 of 4", "step_chip"))
        root.addLayout(hdr)

        # File info
        self.file_info = make_label("", "muted")
        root.addWidget(self.file_info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner.setObjectName("")
        il = QVBoxLayout(inner)
        il.setContentsMargins(0, 0, 8, 0)
        il.setSpacing(14)

        # Built-in categories
        cat_card = card()
        cat_layout = QVBoxLayout(cat_card)
        cat_layout.setContentsMargins(16, 14, 16, 14)
        cat_layout.setSpacing(10)
        cat_layout.addWidget(make_label("Built-in PII categories", bold=True))
        cat_layout.addWidget(make_label(
            "All enabled by default — uncheck any you do not need.", "muted"))
        cat_layout.addWidget(separator())

        grid_widget = QWidget()
        grid = QHBoxLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        col_a = QVBoxLayout()
        col_b = QVBoxLayout()
        col_a.setSpacing(8)
        col_b.setSpacing(8)

        for i, cat in enumerate(BUILTIN_CATEGORIES):
            cb = QCheckBox(cat["label"])
            cb.setChecked(True)
            cb.setProperty("cat_id", cat["id"])
            self._checkboxes[cat["id"]] = cb
            (col_a if i % 2 == 0 else col_b).addWidget(cb)

        grid.addLayout(col_a)
        grid.addLayout(col_b)
        cat_layout.addWidget(grid_widget)
        il.addWidget(cat_card)

        # Detection mode
        mode_card = card()
        ml = QVBoxLayout(mode_card)
        ml.setContentsMargins(16, 14, 16, 14)
        ml.setSpacing(8)
        ml.addWidget(make_label("Detection mode", bold=True))
        self._mode_group = QButtonGroup(self)
        for i, m in enumerate(self.MODES):
            rb = QRadioButton(m)
            if i == 0:
                rb.setChecked(True)
            self._mode_group.addButton(rb, i)
            ml.addWidget(rb)
        il.addWidget(mode_card)

        # Replacement style
        rep_card = card()
        rl = QVBoxLayout(rep_card)
        rl.setContentsMargins(16, 12, 16, 12)
        rl.setSpacing(4)
        rl.addWidget(make_label("Replacement style", bold=True))
        rl.addWidget(make_label(
            "Detected values are replaced with irreversible category labels "
            "e.g. [EMAIL], [PHONE], [NAME]", "muted"))
        il.addWidget(rep_card)

        # Custom patterns
        self._custom_card = card()
        cl = QVBoxLayout(self._custom_card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(10)
        cl.addWidget(make_label("Custom patterns  (this run only, not saved)", bold=True))
        cl.addWidget(make_label(
            "Add up to 5 regex patterns for organisation-specific values "
            "such as employee IDs or case numbers.", "muted"))
        cl.addWidget(separator())

        self._custom_container = QVBoxLayout()
        self._custom_container.setSpacing(8)
        cl.addLayout(self._custom_container)

        self._add_pattern_btn = make_btn("＋  Add pattern", min_w=140)
        self._add_pattern_btn.clicked.connect(self._add_pattern_row)
        cl.addWidget(self._add_pattern_btn)
        il.addWidget(self._custom_card)

        il.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll)

        # Footer
        footer = QHBoxLayout()
        back_btn = make_btn("←  Back")
        back_btn.clicked.connect(self._go_back)
        self.run_btn = make_btn("Run Detection  →", "primary", 180)
        self.run_btn.clicked.connect(self._emit_run)
        footer.addWidget(back_btn)
        footer.addStretch()
        footer.addWidget(self.run_btn)
        root.addLayout(footer)

        self._back_cb = None  # set by MainWindow

    def _add_pattern_row(self):
        if len(self._custom_rows) >= 5:
            QMessageBox.information(self, "Limit reached",
                                    "You can add up to 5 custom patterns.")
            return
        row_widget = QFrame()
        row_widget.setObjectName("card")
        rl = QVBoxLayout(row_widget)
        rl.setContentsMargins(12, 10, 12, 10)
        rl.setSpacing(6)

        name_row = QHBoxLayout()
        name_row.addWidget(make_label("Name:"))
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("e.g. Employee ID")
        name_row.addWidget(name_edit)
        rl.addLayout(name_row)

        pat_row = QHBoxLayout()
        pat_row.addWidget(make_label("Regex:"))
        pat_edit = QLineEdit()
        pat_edit.setPlaceholderText(r"e.g. EMP-\d{6}")
        pat_row.addWidget(pat_edit)
        rl.addLayout(pat_row)

        del_btn = make_btn("✕  Remove", "danger")
        row_data = {"name": name_edit, "pattern": pat_edit, "widget": row_widget}
        del_btn.clicked.connect(lambda: self._remove_pattern_row(row_data))
        rl.addWidget(del_btn)

        self._custom_rows.append(row_data)
        self._custom_container.addWidget(row_widget)

        if len(self._custom_rows) >= 5:
            self._add_pattern_btn.setEnabled(False)

    def _remove_pattern_row(self, row_data):
        self._custom_rows.remove(row_data)
        row_data["widget"].setParent(None)
        row_data["widget"].deleteLater()
        self._add_pattern_btn.setEnabled(True)

    def _emit_run(self):
        enabled_ids = [
            cat_id for cat_id, cb in self._checkboxes.items() if cb.isChecked()
        ]
        custom_pats = [
            {"name": r["name"].text(), "pattern": r["pattern"].text()}
            for r in self._custom_rows
            if r["pattern"].text().strip()
        ]
        mode = self._mode_group.checkedId()
        self.run_detection.emit(enabled_ids, custom_pats, mode)

    def _go_back(self):
        if self._back_cb:
            self._back_cb()

    def set_file_path(self, path):
        self.file_info.setText(f"File:  {Path(path).name}")


# ─────────────────────────────────────────────────────────────────── #
#  Screen 3 — Review                                                  #
# ─────────────────────────────────────────────────────────────────── #

class FindingRow(QFrame):
    toggled = Signal()

    def __init__(self, finding, index):
        super().__init__()
        self.finding = finding
        self.index = index
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)
        self._build()

    def _build(self):
        hl = QHBoxLayout(self)
        hl.setContentsMargins(10, 8, 10, 8)
        hl.setSpacing(10)

        self.check = QCheckBox()
        self.check.setChecked(self.finding.kept)
        self.check.stateChanged.connect(self._toggle)

        tag_lbl = make_label(self.finding.tag, bold=True)
        tag_lbl.setStyleSheet("color: #4cc2ff;")

        orig_lbl = make_label(
            f""{self.finding.original[:40]}{"…" if len(self.finding.original) > 40 else ""}"",
            "muted"
        )

        line_lbl = make_label(f"Line {self.finding.line_number}", "muted")
        line_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        hl.addWidget(self.check)
        hl.addWidget(tag_lbl)
        hl.addWidget(orig_lbl, 1)
        hl.addWidget(line_lbl)
        self._update_style()

    def _toggle(self):
        self.finding.kept = self.check.isChecked()
        self._update_style()
        self.toggled.emit()

    def _update_style(self):
        if self.finding.kept:
            self.setStyleSheet(
                "QFrame#card { background: rgba(76,194,255,0.08); "
                "border: 1px solid rgba(76,194,255,0.2); border-radius: 12px; }"
            )
        else:
            self.setStyleSheet(
                "QFrame#card { background: rgba(255,255,255,0.03); "
                "border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; }"
            )


class ReviewScreen(QWidget):
    go_export = Signal()

    def __init__(self):
        super().__init__()
        self._findings = []
        self._rows = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        col = QVBoxLayout()
        col.addWidget(make_label("Review Findings", "section_title"))
        self.sub_label = make_label("Review each detected item. Uncheck any false positives.", "muted")
        col.addWidget(self.sub_label)
        hdr.addLayout(col)
        hdr.addStretch()
        hdr.addWidget(make_label("Step 3 of 4", "step_chip"))
        root.addLayout(hdr)

        # Summary bar
        self.summary_card = card()
        sum_layout = QHBoxLayout(self.summary_card)
        sum_layout.setContentsMargins(16, 10, 16, 10)
        self.total_lbl = make_label("0 findings", bold=True)
        self.kept_lbl = make_label("0 to redact")
        self.kept_lbl.setStyleSheet("color: #77e0b5; font-weight:600;")
        self.ignored_lbl = make_label("0 ignored")
        self.ignored_lbl.setStyleSheet("color: #adb8c4;")

        btn_all = make_btn("✓ Keep all")
        btn_none = make_btn("✗ Ignore all")
        btn_all.clicked.connect(self._keep_all)
        btn_none.clicked.connect(self._ignore_all)

        sum_layout.addWidget(self.total_lbl)
        sum_layout.addWidget(make_label("  ·  "))
        sum_layout.addWidget(self.kept_lbl)
        sum_layout.addWidget(make_label("  ·  "))
        sum_layout.addWidget(self.ignored_lbl)
        sum_layout.addStretch()
        sum_layout.addWidget(btn_all)
        sum_layout.addWidget(btn_none)
        root.addWidget(self.summary_card)

        # Split: findings list | document preview
        splitter = QSplitter(Qt.Horizontal)

        # Left: findings
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 6, 0)
        ll.setSpacing(8)
        ll.addWidget(make_label("Detected items", bold=True))

        self.findings_scroll = QScrollArea()
        self.findings_scroll.setWidgetResizable(True)
        self.findings_inner = QWidget()
        self.findings_layout = QVBoxLayout(self.findings_inner)
        self.findings_layout.setContentsMargins(0, 0, 0, 0)
        self.findings_layout.setSpacing(6)
        self.findings_layout.addStretch()
        self.findings_scroll.setWidget(self.findings_inner)
        ll.addWidget(self.findings_scroll)
        splitter.addWidget(left)

        # Right: doc preview
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(6, 0, 0, 0)
        rl.setSpacing(8)
        preview_hdr = QHBoxLayout()
        preview_hdr.addWidget(make_label("Document preview", bold=True))
        preview_hdr.addStretch()
        legend = QHBoxLayout()
        for color, lbl in [("#ffe793", "Detected"), ("#9ee7b2", "Kept"), ("#cdd6df", "Ignored")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            legend.addWidget(dot)
            legend.addWidget(make_label(lbl, "muted"))
            legend.addSpacing(6)
        preview_hdr.addLayout(legend)
        rl.addLayout(preview_hdr)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMinimumWidth(380)
        rl.addWidget(self.preview)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([340, 680])
        root.addWidget(splitter, 1)

        # Footer
        footer = QHBoxLayout()
        back_btn = make_btn("←  Back")
        back_btn.clicked.connect(self._go_back)
        self.export_btn = make_btn("Proceed to Export  →", "primary", 200)
        self.export_btn.clicked.connect(self.go_export.emit)
        footer.addWidget(back_btn)
        footer.addStretch()
        footer.addWidget(self.export_btn)
        root.addLayout(footer)

        self._back_cb = None

    def load(self, text, findings):
        self._findings = findings
        self._rows = []
        # Clear old rows
        while self.findings_layout.count() > 1:
            item = self.findings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, f in enumerate(findings):
            row = FindingRow(f, i)
            row.toggled.connect(self._refresh_counts)
            self._rows.append(row)
            self.findings_layout.insertWidget(i, row)

        self._refresh_counts()
        self._render_preview(text)
        self._text = text

    def _refresh_counts(self):
        total = len(self._findings)
        kept = sum(1 for f in self._findings if f.kept)
        ignored = total - kept
        self.total_lbl.setText(f"{total} findings")
        self.kept_lbl.setText(f"{kept} to redact")
        self.ignored_lbl.setText(f"{ignored} ignored")

    def _render_preview(self, text):
        self.preview.clear()
        cursor = self.preview.textCursor()
        fmt_default = QTextCharFormat()
        fmt_default.setForeground(QColor("#17212b"))

        fmt_detect = QTextCharFormat()
        fmt_detect.setBackground(QColor("#ffe793"))
        fmt_detect.setForeground(QColor("#483800"))
        fmt_detect.setFontWeight(QFont.Bold)

        findings_sorted = sorted(self._findings, key=lambda f: f.start)
        cursor_pos = 0
        for f in findings_sorted:
            # text before
            cursor.insertText(text[cursor_pos:f.start], fmt_default)
            # the tag
            tag_fmt = QTextCharFormat()
            if f.kept:
                tag_fmt.setBackground(QColor("#9ee7b2"))
                tag_fmt.setForeground(QColor("#1a4a2d"))
            else:
                tag_fmt.setBackground(QColor("#e0e4e8"))
                tag_fmt.setForeground(QColor("#6a7480"))
            tag_fmt.setFontWeight(QFont.Bold)
            cursor.insertText(f.tag, tag_fmt)
            cursor_pos = f.end

        cursor.insertText(text[cursor_pos:], fmt_default)
        self.preview.verticalScrollBar().setValue(0)

    def refresh_preview(self):
        if hasattr(self, '_text'):
            self._render_preview(self._text)

    def _keep_all(self):
        for f, r in zip(self._findings, self._rows):
            f.kept = True
            r.check.blockSignals(True)
            r.check.setChecked(True)
            r.check.blockSignals(False)
            r._update_style()
        self._refresh_counts()
        self.refresh_preview()

    def _ignore_all(self):
        for f, r in zip(self._findings, self._rows):
            f.kept = False
            r.check.blockSignals(True)
            r.check.setChecked(False)
            r.check.blockSignals(False)
            r._update_style()
        self._refresh_counts()
        self.refresh_preview()

    def _go_back(self):
        if self._back_cb:
            self._back_cb()


# ─────────────────────────────────────────────────────────────────── #
#  Screen 4 — Export                                                  #
# ─────────────────────────────────────────────────────────────────── #

class ExportScreen(QWidget):
    do_export = Signal(str, str, bool)  # out_path, report_path, save_report
    start_over = Signal()

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        hdr = QHBoxLayout()
        col = QVBoxLayout()
        col.addWidget(make_label("Export", "section_title"))
        col.addWidget(make_label(
            "Your anonymized copy will be a new file. The original will not be changed.", "muted"))
        hdr.addLayout(col)
        hdr.addStretch()
        hdr.addWidget(make_label("Step 4 of 4", "step_chip"))
        root.addLayout(hdr)

        # Summary card
        self.summary_card = card()
        sl = QVBoxLayout(self.summary_card)
        sl.setContentsMargins(16, 14, 16, 14)
        sl.setSpacing(8)
        sl.addWidget(make_label("Export summary", bold=True))
        sl.addWidget(separator())
        self.sum_labels = {}
        for key, text in [("total", "Total findings:  —"),
                           ("redacted", "To be redacted:  —"),
                           ("ignored", "Ignored by you:  —"),
                           ("original", "Original file:  unchanged")]:
            lbl = make_label(text)
            if key == "original":
                lbl.setStyleSheet("color: #77e0b5;")
            sl.addWidget(lbl)
            self.sum_labels[key] = lbl
        root.addWidget(self.summary_card)

        # Output file
        out_card = card()
        ol = QVBoxLayout(out_card)
        ol.setContentsMargins(16, 14, 16, 14)
        ol.setSpacing(10)
        ol.addWidget(make_label("Anonymized copy output path", bold=True))
        out_row = QHBoxLayout()
        self.out_edit = QLineEdit()
        browse_out = make_btn("Browse")
        browse_out.clicked.connect(self._browse_out)
        out_row.addWidget(self.out_edit, 1)
        out_row.addWidget(browse_out)
        ol.addLayout(out_row)
        root.addWidget(out_card)

        # Report
        rep_card = card()
        rl = QVBoxLayout(rep_card)
        rl.setContentsMargins(16, 14, 16, 14)
        rl.setSpacing(10)
        rep_hdr = QHBoxLayout()
        rep_hdr.addWidget(make_label("Audit report  (JSON)", bold=True))
        self.report_cb = QCheckBox("Generate report")
        self.report_cb.setChecked(True)
        rep_hdr.addStretch()
        rep_hdr.addWidget(self.report_cb)
        rl.addLayout(rep_hdr)
        rep_row = QHBoxLayout()
        self.rep_edit = QLineEdit()
        browse_rep = make_btn("Browse")
        browse_rep.clicked.connect(self._browse_rep)
        rep_row.addWidget(self.rep_edit, 1)
        rep_row.addWidget(browse_rep)
        rl.addLayout(rep_row)
        root.addWidget(rep_card)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        # Result banner
        self.result_card = QFrame()
        self.result_card.setObjectName("card_accent")
        res_l = QVBoxLayout(self.result_card)
        res_l.setContentsMargins(14, 12, 14, 12)
        self.result_label = make_label("")
        self.result_label.setWordWrap(True)
        res_l.addWidget(self.result_label)
        self.result_card.setVisible(False)
        root.addWidget(self.result_card)

        root.addStretch()

        # Footer
        footer = QHBoxLayout()
        back_btn = make_btn("←  Back")
        back_btn.clicked.connect(self._go_back)
        self.export_btn = make_btn("Export files", "success", 160)
        self.export_btn.clicked.connect(self._export)
        self.start_over_btn = make_btn("Start over", min_w=120)
        self.start_over_btn.clicked.connect(self.start_over.emit)
        self.start_over_btn.setVisible(False)

        footer.addWidget(back_btn)
        footer.addStretch()
        footer.addWidget(self.start_over_btn)
        footer.addWidget(self.export_btn)
        root.addLayout(footer)

        self._back_cb = None
        self._original_path = ""

    def setup(self, original_path, findings):
        self._original_path = original_path
        total = len(findings)
        kept = sum(1 for f in findings if f.kept)
        ignored = total - kept

        self.sum_labels["total"].setText(f"Total findings:  {total}")
        self.sum_labels["redacted"].setText(f"To be redacted:  {kept}")
        self.sum_labels["ignored"].setText(f"Ignored by you:  {ignored}")

        self.out_edit.setText(suggest_output_path(original_path))
        self.rep_edit.setText(suggest_report_path(original_path))
        self.result_card.setVisible(False)
        self.start_over_btn.setVisible(False)
        self.export_btn.setEnabled(True)

    def _browse_out(self):
        ext = Path(self._original_path).suffix
        path, _ = QFileDialog.getSaveFileName(self, "Save anonymized copy", self.out_edit.text(),
                                              f"*{ext};;All files (*.*)")
        if path:
            self.out_edit.setText(path)

    def _browse_rep(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save audit report", self.rep_edit.text(),
                                              "JSON files (*.json);;All files (*.*)")
        if path:
            self.rep_edit.setText(path)

    def _export(self):
        self.do_export.emit(
            self.out_edit.text(),
            self.rep_edit.text(),
            self.report_cb.isChecked()
        )

    def show_progress(self, show: bool):
        self.progress.setVisible(show)
        self.export_btn.setEnabled(not show)

    def show_result(self, success: bool, msg: str):
        self.result_label.setText(msg)
        if success:
            self.result_card.setObjectName("card_accent")
        else:
            self.result_card.setObjectName("card_warn")
        self.result_card.setVisible(True)
        self.start_over_btn.setVisible(success)

    def _go_back(self):
        if self._back_cb:
            self._back_cb()


# ─────────────────────────────────────────────────────────────────── #
#  Main Window                                                        #
# ─────────────────────────────────────────────────────────────────── #

class MainWindow(QMainWindow):
    NAV_LABELS = ["🏠  Home", "🔍  Detect", "📋  Review", "📤  Export"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PII Shield — Offline PII Anonymizer")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)

        self._file_path = None
        self._file_text = None
        self._file_meta = None
        self._findings = []
        self._enabled_ids = []
        self._custom_pats = []

        self._build()

    def _build(self):
        root_widget = QWidget()
        root_widget.setObjectName("root")
        self.setCentralWidget(root_widget)
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Title bar
        titlebar = QFrame()
        titlebar.setObjectName("titlebar")
        titlebar.setFixedHeight(52)
        tb_layout = QHBoxLayout(titlebar)
        tb_layout.setContentsMargins(20, 0, 20, 0)

        brand = QHBoxLayout()
        mark = make_label("P")
        mark.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #4cc2ff, stop:1 #77e0b5);"
            "color: #07111a; border-radius: 8px; "
            "font-weight: 900; font-size: 14px; "
            "min-width:28px; max-width:28px; min-height:28px; max-height:28px;"
            "qproperty-alignment: AlignCenter;"
        )
        brand.addWidget(mark)
        brand_label = make_label("PII Shield")
        brand_label.setStyleSheet("font-size:15px; font-weight:700;")
        brand.addWidget(brand_label)

        tagline = make_label("  •  Offline  •  Windows 11  •  No OCR  •  No PDF  •  Text-based files only", "muted")

        tb_layout.addLayout(brand)
        tb_layout.addWidget(tagline)
        tb_layout.addStretch()
        root_layout.addWidget(titlebar)

        # Body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 18, 14, 18)
        side_layout.setSpacing(4)

        side_layout.addWidget(make_label("Workflow", "muted"))
        side_layout.addSpacing(4)

        self._nav_btns = []
        for i, lbl in enumerate(self.NAV_LABELS):
            btn = QPushButton(lbl)
            btn.setObjectName("nav")
            btn.clicked.connect(lambda _, idx=i: self._nav_to(idx))
            side_layout.addWidget(btn)
            self._nav_btns.append(btn)

        side_layout.addSpacing(20)
        side_layout.addWidget(separator())
        side_layout.addSpacing(10)

        priv = QFrame()
        priv.setObjectName("card_accent")
        priv_l = QVBoxLayout(priv)
        priv_l.setContentsMargins(12, 10, 12, 10)
        priv_l.setSpacing(4)
        priv_l.addWidget(make_label("🔒 Privacy promise", bold=True))
        priv_l.addWidget(make_label(
            "Files never leave your device. All processing happens locally.", "muted"))
        side_layout.addWidget(priv)
        side_layout.addStretch()

        body.addWidget(sidebar)

        # Main stack
        self._stack = QStackedWidget()
        body.addWidget(self._stack, 1)

        # Screens
        self.upload_screen = UploadScreen()
        self.detect_screen = DetectScreen()
        self.review_screen = ReviewScreen()
        self.export_screen = ExportScreen()

        self._stack.addWidget(self.upload_screen)
        self._stack.addWidget(self.detect_screen)
        self._stack.addWidget(self.review_screen)
        self._stack.addWidget(self.export_screen)

        # Wire signals
        self.upload_screen.file_selected.connect(self._on_file_selected)
        self.detect_screen.run_detection.connect(self._on_run_detection)
        self.review_screen.go_export.connect(lambda: self._nav_to(3))
        self.export_screen.do_export.connect(self._on_export)
        self.export_screen.start_over.connect(self._start_over)

        self.detect_screen._back_cb = lambda: self._nav_to(0)
        self.review_screen._back_cb = lambda: self._nav_to(1)
        self.export_screen._back_cb = lambda: self._nav_to(2)

        root_layout.addLayout(body)
        self._set_active_nav(0)

    def _set_active_nav(self, idx):
        for i, btn in enumerate(self._nav_btns):
            btn.setObjectName("nav_active" if i == idx else "nav")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _nav_to(self, idx):
        self._stack.setCurrentIndex(idx)
        self._set_active_nav(idx)

    def _on_file_selected(self, path):
        self._file_path = path
        try:
            self._file_text, self._file_meta = read_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Read error", f"Could not read file:\n{e}")
            return
        self.detect_screen.set_file_path(path)
        self._nav_to(1)

    def _on_run_detection(self, enabled_ids, custom_pats, mode):
        self._enabled_ids = enabled_ids
        self._custom_pats = custom_pats
        self.detect_screen.run_btn.setEnabled(False)
        self.detect_screen.run_btn.setText("Detecting…")

        self._worker = DetectWorker(self._file_text, enabled_ids, custom_pats)
        self._worker.finished.connect(self._on_detection_done)
        self._worker.error.connect(self._on_detection_error)
        self._worker.start()

    def _on_detection_done(self, findings):
        self.detect_screen.run_btn.setEnabled(True)
        self.detect_screen.run_btn.setText("Run Detection  →")
        self._findings = findings

        if not findings:
            QMessageBox.information(
                self, "No PII found",
                "No PII was detected in this file with the current settings.\n\n"
                "• Try enabling more categories.\n"
                "• Switch to Balanced or Broad detection mode."
            )
            return

        self.review_screen.load(self._file_text, self._findings)
        self._nav_to(2)

    def _on_detection_error(self, msg):
        self.detect_screen.run_btn.setEnabled(True)
        self.detect_screen.run_btn.setText("Run Detection  →")
        QMessageBox.critical(self, "Detection error", msg)

    def _on_export(self, out_path, rep_path, save_rep):
        if not out_path:
            QMessageBox.warning(self, "Missing path", "Please set an output file path.")
            return
        self.export_screen.show_progress(True)
        try:
            self.export_screen.setup(self._file_path, self._findings)
            write_file(self._file_path, self._findings, self._file_meta, out_path)
            report_msg = ""
            if save_rep and rep_path:
                report = generate_report(
                    self._file_path, out_path, self._findings, self._custom_pats)
                save_report(report, rep_path)
                report_msg = f"\n📋 Audit report saved:\n   {rep_path}"

            self.export_screen.show_progress(False)
            self.export_screen.show_result(
                True,
                f"✅  Export complete!\n\n"
                f"📄 Anonymized file saved:\n   {out_path}"
                f"{report_msg}\n\n"
                f"The original file was not modified."
            )
        except Exception as e:
            self.export_screen.show_progress(False)
            self.export_screen.show_result(False, f"❌  Export failed:\n{e}")

    def _start_over(self):
        self._file_path = None
        self._file_text = None
        self._file_meta = None
        self._findings = []
        self.upload_screen.reset()
        self._nav_to(0)


# ─────────────────────────────────────────────────────────────────── #
#  Entry point                                                        #
# ─────────────────────────────────────────────────────────────────── #

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("PII Shield")
    app.setStyleSheet(STYLESHEET)

    # Dark palette base
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0f1115"))
    palette.setColor(QPalette.WindowText, QColor("#f2f5f7"))
    palette.setColor(QPalette.Base, QColor("#1a1d24"))
    palette.setColor(QPalette.AlternateBase, QColor("#14171e"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1a1d24"))
    palette.setColor(QPalette.ToolTipText, QColor("#f2f5f7"))
    palette.setColor(QPalette.Text, QColor("#f2f5f7"))
    palette.setColor(QPalette.Button, QColor("#1c202a"))
    palette.setColor(QPalette.ButtonText, QColor("#f2f5f7"))
    palette.setColor(QPalette.Highlight, QColor("#4cc2ff"))
    palette.setColor(QPalette.HighlightedText, QColor("#07111a"))
    app.setPalette(palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
