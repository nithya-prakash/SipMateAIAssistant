import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from characters.character import CharacterCategory, RendererType
from characters.registry import CharacterRegistry
from renderers.factory import RendererFactory
from renderers.static_character import StaticCharacterWidget

_CATEGORY_LABELS = {
    "all": "All",
    CharacterCategory.SIPMATE_ORIGINAL: "🐾 SipMate Originals",
}

_CARD_STYLE = """
QFrame#card { background-color: #2A2A2E; border-radius: 12px; }
QLabel#name { color: white; }
QLabel#meta { color: #A0A0A8; }
QLabel#preview { color: #7FD1FF; }
QPushButton { border-radius: 6px; padding: 4px 8px; color: white; }
QPushButton#select { background-color: #007AFF; }
QPushButton#select[active="true"] { background-color: #34C759; }
QPushButton#fav { background-color: #3A3A3F; }
QPushButton#fav[active="true"] { background-color: #FFB020; color: #1d1d1f; }
QPushButton#preview_btn { background-color: #3A3A3F; }
"""


class CharacterCard(QFrame):
    def __init__(self, character, settings_manager, on_changed):
        super().__init__()
        self.character = character
        self.settings_manager = settings_manager
        self.on_changed = on_changed
        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        if character.renderer_type == RendererType.LOTTIE:
            # Lottie renderers have no pause/autoplay knob, and with only 8
            # characters total, letting them play continuously in the grid is
            # cheap and looks better than a frozen first frame.
            self.visual = RendererFactory.create_renderer(character)
        else:
            self.visual = StaticCharacterWidget(character, autoplay=False)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.visual)
        row.addStretch()
        layout.addLayout(row)

        name = QLabel(f"{character.emoji}  {character.name}")
        name.setObjectName("name")
        name.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        meta = QLabel(f"{_CATEGORY_LABELS.get(character.category, character.category)}\n{character.personality}")
        meta.setObjectName("meta")
        meta.setFont(QFont("Arial", 9))
        meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        meta.setWordWrap(True)
        layout.addWidget(meta)

        self.preview_label = QLabel("")
        self.preview_label.setObjectName("preview")
        self.preview_label.setFont(QFont("Arial", 9))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        self.preview_label.setFixedHeight(34)
        layout.addWidget(self.preview_label)

        btn_row = QHBoxLayout()
        self.btn_fav = QPushButton("★ Favorite")
        self.btn_fav.setObjectName("fav")
        self.btn_fav.clicked.connect(self._toggle_favorite)
        btn_row.addWidget(self.btn_fav)

        self.btn_select = QPushButton("Select")
        self.btn_select.setObjectName("select")
        self.btn_select.clicked.connect(self._select)
        btn_row.addWidget(self.btn_select)
        layout.addLayout(btn_row)

        self.btn_preview = QPushButton("▶ Preview")
        self.btn_preview.setObjectName("preview_btn")
        self.btn_preview.clicked.connect(self._preview)
        layout.addWidget(self.btn_preview)

        self.refresh_state()

    def refresh_state(self):
        settings = self.settings_manager.settings
        is_fav = self.character.id in settings.favorite_character_ids
        self.btn_fav.setProperty("active", "true" if is_fav else "false")
        self.btn_fav.setText("★ Favorited" if is_fav else "☆ Favorite")
        self.btn_fav.style().unpolish(self.btn_fav)
        self.btn_fav.style().polish(self.btn_fav)

        is_selected = settings.character_mode == "single" and settings.selected_character_id == self.character.id
        self.btn_select.setProperty("active", "true" if is_selected else "false")
        self.btn_select.setText("✓ Selected" if is_selected else "Select")
        self.btn_select.style().unpolish(self.btn_select)
        self.btn_select.style().polish(self.btn_select)

    def _toggle_favorite(self):
        favs = list(self.settings_manager.settings.favorite_character_ids)
        if self.character.id in favs:
            favs.remove(self.character.id)
        else:
            favs.append(self.character.id)
        self.settings_manager.update(favorite_character_ids=favs)
        self.refresh_state()

    def _select(self):
        self.settings_manager.update(character_mode="single", selected_character_id=self.character.id)
        self.on_changed()

    def _preview(self):
        if hasattr(self.visual, "start_preview"):
            self.visual.start_preview()  # Lottie cards are already playing continuously
        if self.character.messages:
            self.preview_label.setText(random.choice(self.character.messages))


class CharacterCollectionWindow(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.registry = CharacterRegistry()
        self.cards = []

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("SipMate Character Collection")
        self.resize(760, 620)
        self.setStyleSheet("background-color: #1E1E1E; color: white;" + _CARD_STYLE)

        self._init_ui()

    def _init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 10)
        outer.setSpacing(12)

        title = QLabel("Character Collection")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        outer.addWidget(title)

        filter_row = QHBoxLayout()
        self.filter_buttons = {}
        for key, label in _CATEGORY_LABELS.items():
            btn = QPushButton(label)
            btn.setStyleSheet("background-color: #3A3A3F; color: white; border-radius: 6px; padding: 6px 10px;")
            btn.clicked.connect(lambda _, k=key: self._apply_filter(k))
            filter_row.addWidget(btn)
            self.filter_buttons[key] = btn
        filter_row.addStretch()
        outer.addLayout(filter_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(14)
        scroll.setWidget(container)
        outer.addWidget(scroll)

        for character in self.registry.get_all():
            card = CharacterCard(character, self.settings_manager, self._on_selection_changed)
            card.setFixedWidth(160)
            self.cards.append(card)

        self._apply_filter("all")

    def _apply_filter(self, category):
        # Clear the grid without destroying the card widgets (they're reused).
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        visible = [c for c in self.cards if category == "all" or c.character.category == category]
        columns = 4
        for i, card in enumerate(visible):
            self.grid.addWidget(card, i // columns, i % columns)
            card.setVisible(True)

    def _on_selection_changed(self):
        for card in self.cards:
            card.refresh_state()

    def showEvent(self, event):
        for card in self.cards:
            card.refresh_state()
        super().showEvent(event)
