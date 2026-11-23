# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : preview_workspace.py
# Version      : 1
# Date         : 2026-11-23
# Content      : Reading preview workspace, "Preview" view (SU010/FN033, TSK38)
# Design       : TSC (docs/conception/05_preview-FR/EN.md, TSK37)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Reading preview workspace (TSK38, SU010/FN033): the "Preview" tab.

A read-only reading preview of the current narrative map, rendered as an HTML
subset in a QTextBrowser (pattern of the planoscript PoC, TSK33 plano).

Decisions (docs/conception/05_preview-FR/EN.md, TSK37):
- strictly read-only, no interaction on the content; internal links are
  anchors with passive scroll only (#journey-*, #agent-*, #block-*), they
  never change the application state;
- the note of a component is a tooltip on hover: QTextBrowser strips anchor
  titles, so note anchors ("#note-<kind>-<id>") are resolved through a note
  index (anchorAt + QToolTip.showText, pattern of the workspace nodes);
- refresh_preview() never marks the map nor the project as modified;
- dark theme like the other workspaces: the app-wide stylesheet sets a light
  text color, so the browser background must be set explicitly to the
  workspace background (BG_PRIMARY), otherwise the text is invisible.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

from PySide6.QtWidgets import QTextBrowser, QToolTip
from PySide6.QtCore import QUrl

from config.config_loader import get as _get_config
from ui.utils import theme

if TYPE_CHECKING:
    from core.models.data_model import Agent, Journey, NarrativeMap, Project

_LINK_COLOR = _get_config("link_color", "#E5C07B")

# The browser must carry the workspace background explicitly: the app-wide
# stylesheet already sets a light text color on every QWidget, and
# QTextBrowser's default background is white.
_PREVIEW_BROWSER_STYLESHEET = f"""
    QTextBrowser {{
        background-color: {theme.BG_PRIMARY};
        color: {theme.TEXT_PRIMARY};
        border: none;
        font-family: "{theme.FONT_FAMILY}", system-ui, sans-serif;
        font-size: {theme.MENU_FONT_SIZE_PX}px;
    }}
    QTextBrowser a {{
        color: {_LINK_COLOR};
    }}
"""


class PreviewWorkspace(QTextBrowser):
    """Read-only reading preview of the narrative map ("Preview" tab)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(theme.SCROLLBAR_STYLESHEET + _PREVIEW_BROWSER_STYLESHEET)
        self.setReadOnly(True)
        self.setOpenLinks(False)  # no link opens anything (TSK37 decision)
        self.setOpenExternalLinks(False)
        self.anchorClicked.connect(self._on_anchor_clicked)
        self._notes: Dict[str, str] = {}  # note anchor href -> note text
        self.setPlaceholderText("Open a project to preview its reading.")

    def refresh_preview(self, project: 'Project', narrative_map: 'NarrativeMap',
                        journey: Optional['Journey'] = None,
                        agent_id: Optional[int] = None) -> None:
        """Regenerate the preview. Called on tab activation, on model change
        while the tab is active, and on filter change. Never marks the
        map/project as modified."""
        from core.services.preview_service import PreviewService
        self._notes = PreviewService.build_note_index(project, narrative_map)
        self.setHtml(PreviewService.build_preview_html(project, narrative_map, journey, agent_id))

    def _on_anchor_clicked(self, url: QUrl) -> None:
        """Internal anchors only: passive scroll to the target section
        (#journey-*, #agent-*, #block-*). Note anchors (#note-*) are hover
        tooltips, they never navigate."""
        href = url.toString() if hasattr(url, "toString") else str(url)
        if href.startswith("#"):
            name = href[1:]
            if name.startswith(("journey-", "agent-", "block-")):
                self.scrollToAnchor(name)

    def mouseMoveEvent(self, event) -> None:
        """Custom tooltip on note anchors (anchorAt + QToolTip)."""
        anchor = self.anchorAt(event.position().toPoint())
        if anchor and anchor.startswith("#note-"):
            note = self._notes.get(anchor)
            if note:
                QToolTip.showText(event.globalPosition().toPoint(), note)
                return
        QToolTip.hideText()
        super().mouseMoveEvent(event)
