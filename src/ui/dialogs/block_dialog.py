# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : block_dialog.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Block edition dialog (TSK12, FN015/FN035/RG042).

Edits a narrative block (fusion of planoscript's ComponentDialog and
RelationDialog, adapted to the single typed Block):
- "Label", "Note", "Content" (FN015); the type is displayed read-only
  (RG029: chosen at creation, immutable);
- "Journeys": multiple-choice list of the map's journeys (RG042: the list
  cannot be emptied - a block cannot be detached from its last journey;
  disabled when the map has a single journey);
- for a Condition block only: the structured condition (FN035): kind
  (Choice / Artefact / Skill / Flag), optional reference to an Artefact
  agent, label.

get_values() returns {'lb', 'note', 'content', 'journey_ids', 'condition'}.
"""
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from core.models.data_model import CONDITION_KINDS, Block
from config.config_loader import get as _get_config
from ui.utils import theme


class BlockDialog(QDialog):
    """Edition dialog of a narrative block."""

    NOTE_MAX_HEIGHT_PX = _get_config("dialog_note_max_height_px", 60)
    CONTENT_MIN_HEIGHT_PX = _get_config("dialog_content_min_height_px", 160)
    JOURNEYS_LIST_MAX_HEIGHT_PX = 120

    def __init__(self, block: Block, journeys: List, attached_journey_ids,
                 artefact_agents: List = (), parent=None):
        """
        Args:
            block: the Block entity being edited
            journeys: list of the Journey entities of the map
            attached_journey_ids: ids of the journeys the block is currently
                attached to (checked in the list)
            artefact_agents: list of the project's Artefact agents (for the
                condition reference of a Condition block)
        """
        super().__init__(parent)
        self.block = block
        self._journeys = list(journeys)
        self._attached = set(attached_journey_ids or [])
        self._artefact_agents = list(artefact_agents)
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

        # Type, read-only (RG029: chosen at creation, immutable)
        type_label = QLabel(self.block.typ)
        self.form.addRow("Type:", type_label)

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

        # Structured condition (Condition blocks only - FN035, unique support)
        if self.block.typ == "Condition":
            self._setup_condition_fields()

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
        if len(self._journeys) <= 1:
            # RG042: the option is disabled when the map has a single journey
            self.journeys_list.setEnabled(False)
        self.form.addRow("Journeys:", self.journeys_list)

        # Inline validation message (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {theme.ERROR_COLOR};")
        self.layout.addWidget(self.error_label)

    def _setup_condition_fields(self):
        """Structured condition of a Condition block (FN035)."""
        condition = getattr(self.block, 'condition', None) or {}

        self.condition_kind_combo = QComboBox()
        self.condition_kind_combo.addItems(CONDITION_KINDS)
        kind = condition.get("kind", CONDITION_KINDS[0])
        index = self.condition_kind_combo.findText(kind)
        if index >= 0:
            self.condition_kind_combo.setCurrentIndex(index)
        self.form.addRow("Condition kind:", self.condition_kind_combo)

        self.condition_ref_combo = QComboBox()
        self.condition_ref_combo.addItem("None", None)
        ref_id = condition.get("ref_agent_id")
        for agent in self._artefact_agents:
            self.condition_ref_combo.addItem(agent.lb, agent.id)
            if ref_id is not None and agent.id == ref_id:
                self.condition_ref_combo.setCurrentIndex(self.condition_ref_combo.count() - 1)
        self.form.addRow("Artefact ref:", self.condition_ref_combo)

        self.condition_label_edit = QLineEdit()
        self.condition_label_edit.setText(condition.get("label") or "")
        self.form.addRow("Condition label:", self.condition_label_edit)

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

    def get_condition(self) -> Optional[dict]:
        """Return the structured condition values (Condition blocks only)."""
        if self.block.typ != "Condition":
            return None
        return {
            "kind": self.condition_kind_combo.currentText(),
            "ref_agent_id": self.condition_ref_combo.currentData(),
            "label": self.condition_label_edit.text(),
        }

    def get_values(self) -> dict:
        """Return the values entered by the user."""
        return {
            'lb': self.lb_edit.text().strip(),
            'note': self.note_edit.toPlainText(),
            'content': self.content_edit.toPlainText(),
            'journey_ids': self.get_journey_ids(),
            'condition': self.get_condition(),
        }
