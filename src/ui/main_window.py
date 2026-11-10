# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : main_window.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Main window of Hyperscript.

Shell: menu bar built from docs/specification/05_menu-EN.yaml (non
implemented entries are stubbed via self.menu_actions[...] = ... addAction(...,
lambda: None) - keep the stubs when refactoring menus), welcome screen when no
project is open, bottom info bar, file actions (new/open/save/save as/close/
quit with save confirmation - FN002/FN005/FN006/FN008/FN009/FN010) and the
About dialogs (FN003/FN004).

The workspaces (views "Journeys"/"Agents"/"Relationships"/"Export") are handled
by the next task: the central area currently shows a placeholder page once a
project is open.
"""

import logging
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QMessageBox, QFileDialog, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent

from ui.widgets.info_bar import InfoBar
from ui.utils import theme
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.change_log_dialog import ChangeLogDialog
from core.services.project_service import ProjectService
from core.services.about_service import AboutService
from core.services.change_log_service import ChangeLogService
from usecases.project_management import CreateProjectUseCase
from usecases.file_management import (
    LoadProjectUseCase, SaveProjectUseCase, QuitApplicationUseCase
)
from config.config_loader import get as _get_config
from config.user_state_loader import get as _get_user_state, set as _set_user_state

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    # Emitted when the model is marked modified (hook on ProjectService);
    # used later to refresh views (e.g. the export preview) on modification
    map_modified = Signal()

    # ---------------------------------------------------------------------
    # Environment setup
    # ---------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        # Whether a project is currently open
        self.project_opened = False

        # Dependencies initialization
        self.project_service = ProjectService()
        # Model modification hook (core stays Qt-free); re-emitted as a Qt signal
        self.project_service.on_modified = lambda: self.map_modified.emit()
        self.create_project_usecase = CreateProjectUseCase(self.project_service)
        self.load_project_usecase = LoadProjectUseCase(self.project_service)
        self.save_project_usecase = SaveProjectUseCase(self.project_service)
        self.quit_usecase = QuitApplicationUseCase(self.project_service)
        self.about_service = AboutService()
        self.change_log_service = ChangeLogService()

        # Window dimensions (FN028: fully functional from 1280x720)
        self.setWindowTitle(_get_config("app_window_title", "Hyperscript"))
        self.setMinimumSize(int(_get_config("window_min_width", 1280)),
                            int(_get_config("window_min_height", 720)))

        # Central widget: menu bar on top, stacked pages in the middle
        # (welcome page / workspace placeholder), info bar at the bottom
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_menu_bar()

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages, 1)

        # Welcome page (no project opened)
        self.welcome_page = QWidget()
        self.pages.addWidget(self.welcome_page)

        # Workspace placeholder page (project open) - workspaces are the next task
        self.workspace_page = QWidget()
        placeholder_layout = QVBoxLayout(self.workspace_page)
        placeholder = QLabel("Workspace — handled by the next task.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        placeholder_layout.addWidget(placeholder)
        self.pages.addWidget(self.workspace_page)

        self.info_bar = InfoBar()
        main_layout.addWidget(self.info_bar)

        self._show_welcome_message()
        self._update_menu_state()

    # ---------------------------------------------------------------------
    # Menu bar (05_menu-EN.yaml); MVP-greyed entries stay disabled (RG007)
    # ---------------------------------------------------------------------
    def _create_menu_bar(self):
        self.menu_actions = {}
        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet(theme.MENU_BAR_STYLESHEET)

        # Files
        file_menu = self.menu_bar.addMenu("Files")
        self.menu_actions['new'] = file_menu.addAction("New Project...", self._create_project, "Ctrl+N")
        self.menu_actions['open'] = file_menu.addAction("Open...", self._open_project, "Ctrl+O")
        self.menu_actions['close'] = file_menu.addAction("Close", self._close_project, "Ctrl+W")
        self.menu_actions['save'] = file_menu.addAction("Save", self._save_project, "Ctrl+S")  # RG006
        self.menu_actions['save_as'] = file_menu.addAction("Save as...", self._save_project_as, "Ctrl+Shift+S")
        file_menu.addSeparator()
        self.menu_actions['export_map'] = file_menu.addAction("Export Map...", lambda: None)  # greyed out in the MVP
        self.menu_actions['import_map'] = file_menu.addAction("Import Map...", lambda: None)  # greyed out in the MVP
        file_menu.addSeparator()
        self.menu_actions['recent_projects'] = file_menu.addAction("Recent Projects", lambda: None)  # greyed out in the MVP
        file_menu.addSeparator()
        self.menu_actions['quit'] = file_menu.addAction("Quit", self._on_quit, "Ctrl+Q")

        # Edit (all entries greyed out in the MVP)
        edit_menu = self.menu_bar.addMenu("Edit")
        self.menu_actions['undo'] = edit_menu.addAction("Undo", lambda: None, "Ctrl+Z")
        self.menu_actions['redo'] = edit_menu.addAction("Redo", lambda: None, "Ctrl+Y")
        edit_menu.addSeparator()
        self.menu_actions['cut'] = edit_menu.addAction("Cut", lambda: None, "Ctrl+X")
        self.menu_actions['copy'] = edit_menu.addAction("Copy", lambda: None, "Ctrl+C")
        self.menu_actions['paste'] = edit_menu.addAction("Paste", lambda: None, "Ctrl+V")

        # Display
        display_menu = self.menu_bar.addMenu("Display")
        self.journey_menu = display_menu.addMenu("Journey")  # dynamic checkable list, built with the journeys (FN026/FN029)
        self.menu_actions['journey'] = self.journey_menu
        zoom_menu = display_menu.addMenu("Zoom")
        self.menu_actions['zoom_in'] = zoom_menu.addAction("In", lambda: None, "Ctrl+=")
        self.menu_actions['zoom_out'] = zoom_menu.addAction("Out", lambda: None, "Ctrl+-")
        self.menu_actions['zoom_reset'] = zoom_menu.addAction("Reset", lambda: None, "Ctrl+0")

        # Project
        project_menu = self.menu_bar.addMenu("Project")
        view_menu = project_menu.addMenu("View")
        self.menu_actions['view_journeys'] = view_menu.addAction("Journeys", lambda: None)
        self.menu_actions['view_agents'] = view_menu.addAction("Agents", lambda: None)
        self.menu_actions['view_relationships'] = view_menu.addAction("Relationships", lambda: None)
        self.menu_actions['view_export'] = view_menu.addAction("Export", lambda: None)
        agents_menu = project_menu.addMenu("Agents")
        self.menu_actions['agents_new'] = agents_menu.addAction("New...", lambda: None)
        self.menu_actions['agents_edit'] = agents_menu.addAction("Edit...", lambda: None)
        self.menu_actions['agents_copy'] = agents_menu.addAction("Copy", lambda: None)
        self.menu_actions['agents_delete'] = agents_menu.addAction("Delete...", lambda: None)
        self.menu_actions['agents_associate'] = agents_menu.addAction("Associate with Block...", lambda: None)
        blocks_menu = project_menu.addMenu("Narrative Blocks")
        new_block_menu = blocks_menu.addMenu("New")
        new_block_menu.addAction("Scene", lambda: None)
        new_block_menu.addAction("Pivot", lambda: None)
        new_block_menu.addAction("Condition", lambda: None)
        new_block_menu.addAction("Ending", lambda: None)
        self.menu_actions['blocks_new'] = new_block_menu
        self.menu_actions['blocks_edit'] = blocks_menu.addAction("Edit...", lambda: None)
        self.menu_actions['blocks_copy'] = blocks_menu.addAction("Copy", lambda: None)
        self.menu_actions['blocks_delete'] = blocks_menu.addAction("Delete...", lambda: None)
        transitions_menu = project_menu.addMenu("Transitions")
        self.menu_actions['transitions_new'] = transitions_menu.addAction("New", lambda: None)
        self.menu_actions['transitions_edit'] = transitions_menu.addAction("Edit...", lambda: None)
        self.menu_actions['transitions_delete'] = transitions_menu.addAction("Delete...", lambda: None)
        journeys_menu = project_menu.addMenu("Journeys")
        self.menu_actions['journeys_new'] = journeys_menu.addAction("New", lambda: None)
        self.menu_actions['journeys_edit'] = journeys_menu.addAction("Edit...", lambda: None)
        self.menu_actions['journeys_copy'] = journeys_menu.addAction("Copy", lambda: None)
        self.menu_actions['journeys_set_default'] = journeys_menu.addAction("Set as Default...", lambda: None)
        self.menu_actions['journeys_delete'] = journeys_menu.addAction("Delete...", lambda: None)
        relationships_menu = project_menu.addMenu("Relationships")
        self.menu_actions['relationships_new'] = relationships_menu.addAction("New...", lambda: None)
        self.menu_actions['relationships_edit'] = relationships_menu.addAction("Edit...", lambda: None)
        self.menu_actions['relationships_delete'] = relationships_menu.addAction("Delete...", lambda: None)

        # About (always enabled)
        about_menu = self.menu_bar.addMenu("About")
        self.menu_actions['change_log'] = about_menu.addAction("Change Log", self._show_changelog)
        self.menu_actions['about'] = about_menu.addAction("About Hyperscript", self._show_about)

    # Entries greyed out in the MVP, even with a project open (RG007)
    MVP_GREYED = {
        'export_map', 'import_map', 'recent_projects',
        'undo', 'redo', 'cut', 'copy', 'paste',
        'zoom_in', 'zoom_out', 'zoom_reset',
    }

    # Entries enabled only when a project is open (RG007/RG008)
    PROJECT_DEPENDENT = {
        'close', 'save', 'save_as', 'journey',
        'view_journeys', 'view_agents', 'view_relationships', 'view_export',
        'agents_new', 'agents_edit', 'agents_copy', 'agents_delete', 'agents_associate',
        'blocks_new', 'blocks_edit', 'blocks_copy', 'blocks_delete',
        'transitions_new', 'transitions_edit', 'transitions_delete',
        'journeys_new', 'journeys_edit', 'journeys_copy', 'journeys_set_default', 'journeys_delete',
        'relationships_new', 'relationships_edit', 'relationships_delete',
    }

    def _update_menu_state(self):
        """Enable or disable menu entries based on the project state (RG006/RG007/RG008)."""
        has_project = self.project_opened
        for key, action in self.menu_actions.items():
            if key in self.MVP_GREYED:
                action.setEnabled(False)
            elif key in self.PROJECT_DEPENDENT:
                action.setEnabled(has_project)
            else:
                action.setEnabled(True)
        # "Save" is enabled only when the open project is modified (RG006)
        self.menu_actions['save'].setEnabled(has_project and self.project_service.is_modified)

    # ---------------------------------------------------------------------
    # Welcome screen (no project open)
    # ---------------------------------------------------------------------
    def _show_welcome_message(self):
        """Display the welcome screen with a clickable 'create a new project' link (04_interface)."""
        while self.welcome_page.layout() is None or self.welcome_page.layout().count():
            item = self.welcome_page.layout().takeAt(0) if self.welcome_page.layout() else None
            if item is None:
                break
            if item.widget():
                item.widget().deleteLater()

        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_label = QLabel(f"""
            <h2 style="color: {theme.TEXT_PRIMARY};">Build the plan of your new script.</h2>
            <p style="color: {theme.TEXT_SECONDARY};">Start by <a href="new" style="color: {theme.BLOCK_SCENE_COLOR}; text-decoration: underline;">creating a new project</a> or open an existing project.</p>
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setOpenExternalLinks(False)
        welcome_label.setTextFormat(Qt.TextFormat.RichText)
        welcome_label.setWordWrap(True)
        welcome_label.linkActivated.connect(lambda link: self._create_project())
        welcome_label.setStyleSheet(f"QLabel {{ padding: 40px; background-color: {theme.BG_PRIMARY}; }}")
        self.welcome_page.setStyleSheet(f"background-color: {theme.BG_PRIMARY};")
        welcome_layout.addWidget(welcome_label)
        if self.welcome_page.layout() is None:
            QVBoxLayout(self.welcome_page)
        self.welcome_page.layout().addWidget(welcome_widget)
        self.pages.setCurrentWidget(self.welcome_page)

    # ---------------------------------------------------------------------
    # Project and application state management
    # ---------------------------------------------------------------------
    def _create_project(self):
        """Create a new project (FN005)."""
        if self.project_service.is_modified:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "The current project has been modified. Do you want to save it before creating a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes and not self._save_project():
                return

        project = self.create_project_usecase.execute()
        self.project_opened = True
        self.pages.setCurrentWidget(self.workspace_page)
        self.setWindowTitle(f"{_get_config('app_window_title', 'Hyperscript')} : {project.lb}")
        self._update_menu_state()
        logger.debug("Project created: %s", project)

    def _open_project(self):
        """Open a project from the file system (FN006)."""
        if self.project_service.is_modified:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "The current project has been modified. Do you want to save it before opening a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes and not self._save_project():
                return

        default_dir = self._get_default_project_dir()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open a Project",
            default_dir,
            "Hyperscript Project Files (*.json);;All Files (*)"
        )
        if not file_path:
            return  # cancelled by the user

        # Remember the chosen directory for next time
        _set_user_state("last_project_dir", os.path.dirname(file_path))

        if self.load_project_usecase.execute(file_path):
            self.project_opened = True
            self.pages.setCurrentWidget(self.workspace_page)
            project = self.project_service.current_project
            self.setWindowTitle(f"{_get_config('app_window_title', 'Hyperscript')} : {project.lb} ({file_path})")
            self._update_menu_state()
        else:
            QMessageBox.critical(
                self,
                "Error opening the file",
                f"The file cannot be opened: {file_path}"
            )
        logger.debug("Project loaded: %s", self.project_service.current_project)

    def _get_default_project_dir(self) -> str:
        """
        Resolve the default directory for the file dialogs.

        Priority: last used directory (user state) > configured default
        (config.json) > user home. The resolved directory is created if it
        does not exist. A leading ``~/`` in the configured path is resolved
        against the user home.
        """
        last_dir = _get_user_state("last_project_dir")
        if last_dir and os.path.isdir(last_dir):
            return last_dir

        home = os.path.expanduser("~")
        configured = os.path.expanduser(_get_config("projects_default_dir", "~/HyperscriptProjects"))

        parent = os.path.dirname(configured)
        if os.path.normcase(parent) == os.path.normcase(home):
            documents_dir = os.path.join(home, "Documents")
            if os.path.isdir(documents_dir):
                configured = os.path.join(documents_dir, os.path.basename(configured))

        try:
            os.makedirs(configured, exist_ok=True)
        except OSError:
            pass
        return configured

    def _save_project(self):
        """Save the project to its associated file, or ask for a location if it has none (FN008)."""
        file_path = self.project_service.file_path
        if file_path and os.path.isdir(os.path.dirname(file_path)):
            return self._do_save(file_path)
        return self._save_project_as()

    def _save_project_as(self) -> bool:
        """Save the project under a chosen name/location (FN009/RG012)."""
        default_dir = self._get_default_project_dir()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as...",
            default_dir,
            "Hyperscript Project Files (*.json);;All Files (*)"
        )
        if not file_path:
            return False
        if not file_path.lower().endswith('.json'):
            file_path += '.json'

        _set_user_state("last_project_dir", os.path.dirname(file_path))
        return self._do_save(file_path)

    def _do_save(self, file_path: str) -> bool:
        """Execute the save and handle the result (FN008/FN009)."""
        try:
            success = self.save_project_usecase.execute(file_path)
            if success:
                # Layout persistence (RG060) hooks in here once the
                # workspaces exist (next task)
                project = self.project_service.current_project
                self.setWindowTitle(f"{_get_config('app_window_title', 'Hyperscript')} : {project.lb} ({file_path})")
                self._update_menu_state()  # is_modified is now False: Save is disabled (RG006)
            return success
        except Exception as e:
            QMessageBox.critical(self, "Error saving the project", str(e))
            return False

    def _close_project(self) -> bool:
        """Close the current project, with save confirmation if modified (FN010)."""
        if not self.project_opened:
            return True
        if self.project_service.is_modified:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "The project has been modified. Do you want to save it before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return False
            if reply == QMessageBox.StandardButton.Yes and not self._save_project():
                return False

        self.project_service.close_project()
        self._show_welcome_message()
        self.info_bar.clear()
        self.project_opened = False
        self.setWindowTitle(_get_config("app_window_title", "Hyperscript"))
        self._update_menu_state()
        return True

    def closeEvent(self, event: QCloseEvent):
        """Confirm before quitting when the project is modified (FN002)."""
        if self._handle_quit():
            event.accept()
        else:
            event.ignore()

    def _handle_quit(self) -> bool:
        if not self.quit_usecase.should_ask_confirmation():
            return True
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "The project has been modified. Do you want to save it before quitting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            return self._save_project()
        return reply == QMessageBox.StandardButton.No

    def _on_quit(self):
        self.close()  # triggers closeEvent

    # ---------------------------------------------------------------------
    # About dialogs (FN003/FN004)
    # ---------------------------------------------------------------------
    def _show_changelog(self):
        ChangeLogDialog(self.change_log_service, self).exec()

    def _show_about(self):
        AboutDialog(self.about_service, self).exec()
