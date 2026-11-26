# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : block_dialog.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Block edition dialog (TSK12, FN015/RG042; TSK39 session 12: FN030).

Edits a narrative block (fusion of planoscript's ComponentDialog and
RelationDialog, adapted to the single typed Block):
- "Label", "Note", "Content" (FN015); the type is immutable (RG029: chosen
  at creation) and is not a row of the dialog (TSK16), only the window title
  recalls it;
- "Journeys": multiple-choice list of the map's journeys (RG042: the list
  cannot be emptied - a block cannot be detached from its last journey;
  disabled when the map has a single journey);
- "Agents": multiple-choice list of the project's agents (FN030, TSK39
  session 12) - the participating agents are checked; the checked set is
  applied by the caller through the participation use cases. The structured
  condition fields (FN035) were removed in session 12 to simplify the model.

get_values() returns {'lb', 'note', 'content', 'journey_ids', 'agent_ids'}.
"""
from typing import List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from core.models.data_model import Block
from config.config_loader import get as _get_config
from ui.utils import theme


class BlockDialog(QDialog):
    """Edition dialog of a narrative block."""

    NOTE_MAX_HEIGHT_PX = _get_config("dialog_note_max_height_px", 60)
    CONTENT_MIN_HEIGHT_PX = _get_config("dialog_content_min_height_px", 160)
    JOURNEYS_LIST_MAX_HEIGHT_PX = 120

    def __init__(self, block: Block, journeys: List, attached_journey_ids,
                 agents: List = (), participating_agent_ids=(), parent=None):
        """
        Args:
            block: the Block entity being edited
            journeys: list of the Journey entities of the map
            attached_journey_ids: ids of the journeys the block is currently
                attached to (checked in the list)
            agents: list of the project's Agent entities
            participating_agent_ids: ids of the agents currently participating
                in the block (checked in the list)
        """
        super().__init__(parent)
        self.block = block
        self._journeys = list(journeys)
        self._attached = set(attached_journey_ids or [])
        self._agents = list(agents)
        self._participating = set(participating_agent_ids or [])
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle(f"Edit Block ({self.block.typ})")
        self.setModal(True)
        self.setMinimumSize(525, 420)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)
        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.layout.addLayout(self.form, stretch=1)
        self.layout.setAlignment(self.form, Qt.AlignTop)
        self._add_buttons()

    def _setup_content(self):
        # Label field
        self.lb_edit = QLineEdit()
        self.lb_edit.setText(getattr(self.block, 'lb', '') or '')
        self.form.addRow("Label:", self.lb_edit)

        # Note field (compact area, summary notes)
        self.note_edit = QTextEdit()
        self.note_edit.setPlainText(getattr(self.block, 'note', None) or "")
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.note_edit.setMaximumHeight(self.NOTE_MAX_HEIGHT_PX)
        self.form.addRow("Note:", self.note_edit)

        # Content field (larger area, narrative content)
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(getattr(self.block, 'content', None) or "")
        self.content_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_edit.setMinimumHeight(self.CONTENT_MIN_HEIGHT_PX)
        self.form.addRow("Content:", self.content_edit)

        # Journeys multiple-choice list (RG042)
        self.journeys_list = QListWidget()
        for journey in self._journeys:
            item = QListWidgetItem(journey.lb)
            item.setData(Qt.ItemDataRole.UserRole, journey.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked
                               if journey.id in self._attached
                               else Qt.CheckState.Unchecked)
            self.journeys_list.addItem(item)
        self.journeys_list.setMaximumHeight(self.JOURNEYS_LIST_MAX_HEIGHT_PX)
        if len(self._journeys) <= 1 or self.block.typ == "Start":
            # RG042: disabled when the map has a single journey;
            # RG068: the Start block's attachments are never editable
            self.journeys_list.setEnabled(False)
        self.form.addRow("Journeys:", self.journeys_list)

        # Agents multiple-choice list (FN030, TSK39 session 12): same pattern
        # as the journey attachments - the participating agents are checked
        self.agents_list = QListWidget()
        for agent in sorted(self._agents, key=lambda a: (a.lb, a.id)):
            item = QListWidgetItem(f"{agent.lb} ({agent.typ})")
            item.setData(Qt.ItemDataRole.UserRole, agent.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked
                               if agent.id in self._participating
                               else Qt.CheckState.Unchecked)
            self.agents_list.addItem(item)
        self.agents_list.setMaximumHeight(self.JOURNEYS_LIST_MAX_HEIGHT_PX)
        self.form.addRow("Agents:", self.agents_list)

        # Inline validation message (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {theme.ERROR_COLOR};")
        self.layout.addWidget(self.error_label)

    def _add_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self._validate)
        ok_button.setFixedWidth(100)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(100)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def _validate(self):
        if not self.get_values()['lb']:
            self.error_label.setText("Label cannot be empty")
            return
        if self.journeys_list.isEnabled() and not self.get_journey_ids():
            self.error_label.setText("A block must belong to at least one journey")  # RG042
            return
        self.accept()

    def get_journey_ids(self) -> List[int]:
        """Return the ids of the checked journeys."""
        ids = []
        for i in range(self.journeys_list.count()):
            item = self.journeys_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ids.append(item.data(Qt.ItemDataRole.UserRole))
        return ids

    def get_agent_ids(self) -> List[int]:
        """Return the ids of the checked agents (FN030)."""
        ids = []
        for i in range(self.agents_list.count()):
            item = self.agents_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ids.append(item.data(Qt.ItemDataRole.UserRole))
        return ids

    def get_values(self) -> dict:
        """Return the values entered by the user."""
        return {
            'lb': self.lb_edit.text().strip(),
            'note': self.note_edit.toPlainText(),
            'content': self.content_edit.toPlainText(),
            'journey_ids': self.get_journey_ids(),
            'agent_ids': self.get_agent_ids(),
        }
