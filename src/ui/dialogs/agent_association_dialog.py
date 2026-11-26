# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agent_association_dialog.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Agent association dialog for one block (TSK18, FN030, SU008).

Lists all the agents of the project with their current participation status
(checked/unchecked) for the target block. Checking/unchecking emits
participation_toggled; the "New agent..." button opens an AgentDialog and
emits agent_create_requested with its values (create + associate in a single
operation, FN030).

RG058: the dialog NEVER writes the model (unlike planoscript's version, which
called the use cases directly): MainWindow connects the signals, applies the
use cases, then calls refresh() to resync the list and set_status() for the
feedback line.
"""
from typing import Iterable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel
)

from core.models.data_model import Agent, Block
from config.config_loader import get as _get_config
from ui.dialogs.agent_dialog import AgentDialog
from ui.dialogs.base_dialog import BUTTON_WIDTH_PX, WIDE_BUTTON_WIDTH_PX
from ui.utils import theme


class AgentAssociationDialog(QDialog):
    """Checkable agent list for one block; signals only (RG058)."""

    participation_toggled = Signal(int, bool)  # agent_id, checked
    agent_create_requested = Signal(dict)      # AgentDialog.get_values()

    def __init__(self, agents: Iterable[Agent], block: Block,
                 participating_agent_ids: Iterable[int],
                 new_agent_label: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._agents = list(agents)
        self._block = block
        self._participating = set(participating_agent_ids)
        self._new_agent_label = new_agent_label
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        self.setWindowTitle(f"Add Participation with '{self._block.lb}'")  # TSK39 (1.3): libellé normalisé
        self.setModal(True)
        self.setMinimumSize(_get_config("agent_association_dialog_min_width_px", 400),
                            _get_config("agent_association_dialog_min_height_px", 400))
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)

        self.list_widget = QListWidget()
        self.list_widget.itemChanged.connect(self._item_changed)
        self.layout.addWidget(self.list_widget, stretch=1)

        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.new_button = QPushButton("New agent...")
        self.new_button.clicked.connect(self._new_agent_requested)
        self.new_button.setFixedWidth(WIDE_BUTTON_WIDTH_PX)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setFixedWidth(BUTTON_WIDTH_PX)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.close_button)
        self.layout.addLayout(button_layout)

    def refresh(self, agents: Iterable[Agent], participating_agent_ids: Iterable[int]):
        """Resync the list after MainWindow applied the use cases."""
        self._agents = list(agents)
        self._participating = set(participating_agent_ids)
        self._refresh_list()

    def set_status(self, text: str):
        """Set the feedback line shown below the agent list."""
        self.status_label.setText(text)

    def _refresh_list(self):
        # itemChanged fires on every flag/check change: disconnect while
        # rebuilding the list to avoid spurious signals
        self.list_widget.itemChanged.disconnect(self._item_changed)
        self.list_widget.clear()
        for agent in self._agents:
            item = QListWidgetItem(f"{agent.lb} ({agent.typ})")
            item.setData(Qt.ItemDataRole.UserRole, agent.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if agent.id in self._participating
                else Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
        self.list_widget.itemChanged.connect(self._item_changed)

    def _item_changed(self, item):
        agent_id = item.data(Qt.ItemDataRole.UserRole)
        self.participation_toggled.emit(
            agent_id, item.checkState() == Qt.CheckState.Checked)

    def _new_agent_requested(self):
        dialog = AgentDialog(parent=self, default_label=self._new_agent_label)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.agent_create_requested.emit(dialog.get_values())
