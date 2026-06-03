from PyQt6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from src.ui import styles

class QueueItemWidget(QFrame):
    def __init__(self, idx, filename, duration, on_up_clicked, on_down_clicked, parent=None):
        super().__init__(parent)
        self.idx = idx
        self.filename = filename
        self.duration = duration
        self.on_up_clicked = on_up_clicked
        self.on_down_clicked = on_down_clicked
        self.init_ui()

    def init_ui(self):
        self.setObjectName("queueItem")
        self.setStyleSheet(styles.QUEUE_ITEM_STYLE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Index label (e.g. "01")
        self.idx_label = QLabel(self.idx, self)
        self.idx_label.setObjectName("queueIndex")
        self.idx_label.setStyleSheet(styles.QUEUE_INDEX_STYLE)
        layout.addWidget(self.idx_label)

        # Text layout (Title + Duration)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_label = QLabel(self.filename, self)
        self.title_label.setObjectName("queueTitle")
        self.title_label.setStyleSheet(styles.QUEUE_TITLE_STYLE)
        self.title_label.setWordWrap(True)

        self.dur_label = QLabel(self.duration, self)
        self.dur_label.setObjectName("queueDuration")
        self.dur_label.setStyleSheet(styles.QUEUE_DURATION_STYLE)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.dur_label)
        layout.addLayout(text_layout)
        layout.addStretch(1)

        # Up and Down navigation buttons
        btn_container = QWidget(self)
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(3)

        up_btn = QPushButton("▲", self)
        up_btn.setObjectName("queueNavBtn")
        up_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        up_btn.setStyleSheet(styles.QUEUE_NAV_BUTTON_STYLE)
        up_btn.clicked.connect(self.on_up_clicked)
        btn_layout.addWidget(up_btn)

        down_btn = QPushButton("▼", self)
        down_btn.setObjectName("queueNavBtn")
        down_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        down_btn.setStyleSheet(styles.QUEUE_NAV_BUTTON_STYLE)
        down_btn.clicked.connect(self.on_down_clicked)
        btn_layout.addWidget(down_btn)

        layout.addWidget(btn_container)

class QueueListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setStyleSheet("background: transparent; border: none;")
        self.setObjectName("queueList")
        self.queue_data = [] # Stores tuples: (idx, filename, duration)

    def populate(self, data):
        self.clear()
        self.queue_data = data
        for i, (idx, filename, duration) in enumerate(self.queue_data):
            item = QListWidgetItem(self)
            
            # Catch the checked signal argument to prevent overriding row index 'i'
            up_cb = lambda checked=False, r=i: self.move_item_up(r)
            down_cb = lambda checked=False, r=i: self.move_item_down(r)
            
            widget = QueueItemWidget(idx, filename, duration, up_cb, down_cb)
            item.setSizeHint(widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, widget)

    def move_item_up(self, row):
        if row <= 0:
            return
        # Swap items in data array
        self.queue_data[row], self.queue_data[row-1] = self.queue_data[row-1], self.queue_data[row]
        self.rebuild_queue(row - 1)

    def move_item_down(self, row):
        if row >= len(self.queue_data) - 1:
            return
        # Swap items in data array
        self.queue_data[row], self.queue_data[row+1] = self.queue_data[row+1], self.queue_data[row]
        self.rebuild_queue(row + 1)

    def rebuild_queue(self, select_row):
        # Update prefix numbers (01, 02, 03, etc.) sequentially
        updated_data = []
        for i, (_, filename, duration) in enumerate(self.queue_data):
            idx_str = f"{i+1:02d}"
            updated_data.append((idx_str, filename, duration))

        self.populate(updated_data)
        self.setCurrentRow(select_row)
        print(f"[ACTION] Play Queue reordered by button controls. Selected row: {select_row}.")
