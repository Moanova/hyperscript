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

The workspaces (views "Journeys"/"Agents"/"Relationships"/"Export") are
activated by the tab bar; only "Journeys" is implemented in the MVP (TSK11):
blocks/transitions graph, journey filter (FN029), context menus dynamically
aligned with the application menu (RG055), layout persistence (RG060).
The other tabs show a placeholder page.
"""

import logging
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QDialog,
    QMessageBox, QFileDialog, QStackedWidget, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent

from ui.widgets.info_bar import InfoBar
from ui.widgets.tab_bar import TabBar
from ui.views import JourneysWorkspace
from ui.nodes.block_node import BlockNode
from ui.nodes.connection import Connection
from ui.utils import theme
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.change_log_dialog import ChangeLogDialog
from ui.dialogs import BlockDialog, TransitionDialog, JourneyDialog, JourneySelectionDialog
from core.services.journey_service import JourneyService
from core.services.project_service import ProjectService
from core.services.about_service import AboutService
from core.services.change_log_service import ChangeLogService
from core.services.layout_service import LayoutService
from usecases.project_management import CreateProjectUseCase
from usecases.file_management import (
    LoadProjectUseCase, SaveProjectUseCase, QuitApplicationUseCase
)
from usecases.view_management import (
    CreateBlockUseCase, UpdateBlockUseCase, DuplicateBlockUseCase, DeleteBlockUseCase,
    CreateTransitionUseCase, UpdateTransitionUseCase, DeleteTransitionUseCase
)
from usecases.journey_management import (
    CreateJourneyUseCase, UpdateJourneyUseCase, ActivateJourneyUseCase,
    SetDefaultJourneyUseCase, DuplicateJourneyUseCase, DeleteJourneyUseCase
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
        # View/journey use cases (TSK08/TSK09)
        self.create_block_usecase = CreateBlockUseCase(self.project_service)
        self.update_block_usecase = UpdateBlockUseCase(self.project_service)
        self.duplicate_block_usecase = DuplicateBlockUseCase(self.project_service)
        self.delete_block_usecase = DeleteBlockUseCase(self.project_service)
        self.create_transition_usecase = CreateTransitionUseCase(self.project_service)
        self.update_transition_usecase = UpdateTransitionUseCase(self.project_service)
        self.delete_transition_usecase = DeleteTransitionUseCase(self.project_service)
        self.create_journey_usecase = CreateJourneyUseCase(self.project_service)
        self.update_journey_usecase = UpdateJourneyUseCase(self.project_service)
        self.activate_journey_usecase = ActivateJourneyUseCase(self.project_service)
        self.set_default_journey_usecase = SetDefaultJourneyUseCase(self.project_service)
        self.duplicate_journey_usecase = DuplicateJourneyUseCase(self.project_service)
        self.delete_journey_usecase = DeleteJourneyUseCase(self.project_service)

        # Window dimensions (FN028: fully functional from 1280x720)
        self.setWindowTitle(_get_config("app_window_title", "Hyperscript"))
        self.setMinimumSize(int(_get_config("window_min_width", 1280)),
                            int(_get_config("window_min_height", 720)))

        # Central widget: menu bar on top, tab bar + stacked views in the
        # middle (welcome page / project views), info bar at the bottom
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_menu_bar()

        # Tab bar, visible only when a project is open (04_interface section 3)
        self.tab_bar = TabBar(["Journeys", "Agents", "Relationships", "Export"])
        self.tab_bar.hide()
        main_layout.addWidget(self.tab_bar)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages, 1)

        # Welcome page (no project opened)
        self.welcome_page = QWidget()
        self.pages.addWidget(self.welcome_page)

        # View pages (project open); only "Journeys" is implemented in the MVP
        self.view_pages = {}
        self.journeys_page = QWidget()
        QVBoxLayout(self.journeys_page).setContentsMargins(0, 0, 0, 0)
        self.pages.addWidget(self.journeys_page)
        self.view_pages["Journeys"] = self.journeys_page
        for name in ("Agents", "Relationships", "Export"):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            label = QLabel(f"{name} view — handled by a later task.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
            page_layout.addWidget(label)
            self.pages.addWidget(page)
            self.view_pages[name] = page

        self.info_bar = InfoBar()
        main_layout.addWidget(self.info_bar)

        # Workspace state (created when a project is opened)
        self.journeys_workspace = None
        self.journey_filter_active = False  # RG047/RG048: off by default, not persisted

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
        self.menu_actions['blocks_new_scene'] = new_block_menu.addAction("Scene", lambda: self._create_new_block("Scene"))
        self.menu_actions['blocks_new_pivot'] = new_block_menu.addAction("Pivot", lambda: self._create_new_block("Pivot"))
        self.menu_actions['blocks_new_condition'] = new_block_menu.addAction("Condition", lambda: self._create_new_block("Condition"))
        self.menu_actions['blocks_new_ending'] = new_block_menu.addAction("Ending", lambda: self._create_new_block("End"))
        self.menu_actions['blocks_new'] = new_block_menu
        self.menu_actions['blocks_edit'] = blocks_menu.addAction("Edit...", self._edit_selected_block)
        self.menu_actions['blocks_copy'] = blocks_menu.addAction("Copy", self._duplicate_selected_block)
        self.menu_actions['blocks_delete'] = blocks_menu.addAction("Delete...", self._delete_selected_block)
        transitions_menu = project_menu.addMenu("Transitions")
        self.menu_actions['transitions_new'] = transitions_menu.addAction("New", self._start_transition_creation)
        self.menu_actions['transitions_edit'] = transitions_menu.addAction("Edit...", self._edit_selected_transition)
        self.menu_actions['transitions_delete'] = transitions_menu.addAction("Delete...", self._delete_selected_transition)
        journeys_menu = project_menu.addMenu("Journeys")
        self.menu_actions['journeys_new'] = journeys_menu.addAction("New", self._new_journey)
        self.menu_actions['journeys_edit'] = journeys_menu.addAction("Edit...", self._edit_journey)
        self.menu_actions['journeys_copy'] = journeys_menu.addAction("Copy", self._copy_journey)
        self.menu_actions['journeys_set_default'] = journeys_menu.addAction("Set as Default...", self._set_default_journey)
        self.menu_actions['journeys_delete'] = journeys_menu.addAction("Delete...", self._delete_journey)
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
        self._init_workspace()
        self.pages.setCurrentWidget(self.view_pages["Journeys"])
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
            self._init_workspace()
            self.pages.setCurrentWidget(self.view_pages["Journeys"])
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
                # Layout persistence (RG060): the visual layout is stored in a
                # dedicated file next to the project file
                if self.journeys_workspace is not None:
                    nm = self.project_service.current_project.narrative_maps[0]
                    LayoutService.save_workspace_layout(
                        file_path, nm.id, self.journeys_workspace.collect_workspace_layout())
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

        self._teardown_workspace()
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
    # Workspaces (views) — "Journeys" implemented in the MVP (TSK11)
    # ---------------------------------------------------------------------
    def _current_narrative_map(self):
        project = self.project_service.current_project
        return project.narrative_maps[0] if project else None  # MVP: single map

    def _init_workspace(self):
        """Create the Journeys workspace and populate it from the saved layout
        (RG060) or with default positions (FN028)."""
        nm = self._current_narrative_map()
        if nm is None:
            return
        self._teardown_workspace()
        workspace = JourneysWorkspace(narrative_map=nm, info_bar=self.info_bar, main_window=self)
        workspace.transition_created.connect(self._on_transition_created)
        workspace.workspace_modified.connect(self._on_workspace_modified)
        workspace.context_menu_requested.connect(self._show_workspace_context_menu)
        self.journeys_page.layout().addWidget(workspace)
        self.journeys_workspace = workspace

        saved = None
        if self.project_service.file_path:
            saved = LayoutService.load_workspace_layout(self.project_service.file_path, nm.id)
        if saved is not None:
            workspace.populate_from_layout(saved, nm)
        else:
            workspace.populate_default(nm)

        # RG047/RG048: the journey filter is disabled by default, not persisted
        self.journey_filter_active = False
        workspace.set_journey_filter_active(False)
        self._rebuild_journey_menu()
        self.tab_bar.show()
        self.tab_bar.forceCurrentTab("Journeys")

    def _teardown_workspace(self):
        if self.journeys_workspace is not None:
            self.journeys_workspace.setParent(None)
            self.journeys_workspace.deleteLater()
            self.journeys_workspace = None
        self.journey_filter_active = False
        self.tab_bar.hide()

    def _on_tab_changed(self, tab_name: str):
        page = self.view_pages.get(tab_name)
        if page is not None:
            self.pages.setCurrentWidget(page)

    # ---------------------------------------------------------------------
    # Blocks and transitions actions (FN014/FN016/FN018/FN020/FN022)
    # ---------------------------------------------------------------------
    def _create_new_block(self, typ: str):
        """FN014: create a block of the given type at the first free grid position."""
        if self.journeys_workspace is None:
            return
        block = self.create_block_usecase.execute(typ, filter_active=self.journey_filter_active)  # RG040
        x, y = self.journeys_workspace.next_free_position()
        layout = LayoutService.create_node_layout(block.id, block.typ, x, y)  # RG046: snapped
        self.journeys_workspace.create_block_node(block, layout, select=True)
        self._update_menu_state()

    def _start_transition_creation(self):
        """FN020: enter transition creation mode (trace from the source's outgoing port)."""
        if self.journeys_workspace is not None:
            self.journeys_workspace.enter_transition_creation_mode()
            self.info_bar.show_message(
                "Click the outgoing port (right) of the source block, then the incoming port (left) of the target block")

    def _on_transition_created(self, source_node, target_node):
        """Apply the transition creation use case (RG028 validation); the
        workspace never writes the model (RG058)."""
        transition = self.create_transition_usecase.execute(
            source_node.entity.id, target_node.entity.id)
        if transition is None:
            self.info_bar.show_message(
                "Transition refused: block-type matrix or duplicate ordered pair (RG028)")
            return
        self.journeys_workspace.create_connection_from_data(
            source_node, target_node, transition, select=True)
        self._update_menu_state()

    def _on_workspace_modified(self):
        """FN017: moving a block marks the project as modified."""
        self.project_service.set_modified(True)
        self._update_menu_state()

    def _get_selected_item(self):
        if self.journeys_workspace is None:
            return None
        return self.journeys_workspace.get_selected_item()

    def _duplicate_selected_block(self):
        """FN016: duplicate the selected block (Start is not duplicable, RG025)."""
        item = self._get_selected_item()
        if not isinstance(item, BlockNode):
            return
        copy = self.duplicate_block_usecase.execute(item.entity, filter_active=self.journey_filter_active)
        x, y = self.journeys_workspace.next_free_position(item.pos().x() + 120, item.pos().y())
        layout = LayoutService.create_node_layout(copy.id, copy.typ, x, y)
        self.journeys_workspace.create_block_node(copy, layout, select=True)
        self._update_menu_state()

    def _delete_selected_block(self):
        """FN018: delete the selected block, with confirmation; the cascade
        (RG023) is handled by the use case."""
        item = self._get_selected_item()
        if not isinstance(item, BlockNode):
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Delete block '{item.entity.lb}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        removed = self.delete_block_usecase.execute(item.entity.id)  # RG023/RG025
        if removed is None:
            return
        self.journeys_workspace.remove_node(item)
        cascaded = sum(len(v) for k, v in removed.items() if k != 'block')
        if cascaded:
            self.info_bar.show_message(
                f"Block deleted; {cascaded} associated element(s) removed with it (cascade)")
        else:
            self.info_bar.show_message("Block deleted")
        self._update_menu_state()

    def _delete_selected_transition(self):
        """FN022: delete the selected transition, with confirmation."""
        item = self._get_selected_item()
        if not isinstance(item, Connection):
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            "Delete the selected transition?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        if self.delete_transition_usecase.execute(item.get_relation_id()):
            self.journeys_workspace.remove_connection(item)
            self.info_bar.show_message("Transition deleted")
            self._update_menu_state()

    # ---------------------------------------------------------------------
    # Journeys actions (FN023/FN025/FN027) + Display > Journey (FN026/FN029)
    # ---------------------------------------------------------------------
    def _new_journey(self):
        """FN023: create a journey (not activated; the active journey is unchanged)."""
        self.create_journey_usecase.execute()
        self._rebuild_journey_menu()
        self._update_menu_state()

    def _copy_journey(self):
        """FN025/RG043: duplicate the active journey (block attachments copied)."""
        nm = self._current_narrative_map()
        active = nm.get_active_journey() if nm else None
        if active is not None:
            self.duplicate_journey_usecase.execute(active)
        self._rebuild_journey_menu()
        self._update_menu_state()

    def _delete_journey(self):
        """FN027: delete the active journey (RG024: the last one cannot be deleted)."""
        nm = self._current_narrative_map()
        active = nm.get_active_journey() if nm else None
        if active is None:
            return
        result = self.delete_journey_usecase.execute(active)
        if not result or not result.get('success'):
            QMessageBox.information(self, "Cannot delete journey",
                                    "The last journey of the map cannot be deleted.")
            return
        self._rebuild_journey_menu()
        if self.journeys_workspace is not None:
            self.journeys_workspace.apply_journey_filter()
        self._update_menu_state()

    def _rebuild_journey_menu(self):
        """Rebuild the Display > Journey menu dynamically (FN026/FN029):
        checkable 'All journeys' on top (checked = filter disabled), then one
        checkable entry per journey."""
        self.journey_menu.clear()
        all_action = self.journey_menu.addAction(_get_config("journey_list_all_label", "All journeys"))
        all_action.setCheckable(True)
        all_action.setChecked(not self.journey_filter_active)
        all_action.triggered.connect(lambda: self._set_journey_filter_active(False))
        self.journey_menu.addSeparator()
        nm = self._current_narrative_map()
        if nm is not None:
            active = nm.get_active_journey()
            for journey in nm.journey:
                action = self.journey_menu.addAction(journey.lb)
                action.setCheckable(True)
                action.setChecked(self.journey_filter_active and active is journey)
                action.triggered.connect(lambda _checked=False, j=journey: self._activate_journey(j))

    def _activate_journey(self, journey):
        """FN026: activate a journey; the filter applies to it (FN029)."""
        self.activate_journey_usecase.execute(journey)
        self._set_journey_filter_active(True)
        self._update_menu_state()

    def _set_journey_filter_active(self, active: bool):
        """FN029/RG048: toggle the journey filter on all views (visual only,
        RG047: does not mark the project as modified)."""
        self.journey_filter_active = active
        if self.journeys_workspace is not None:
            self.journeys_workspace.set_journey_filter_active(active)
        self._rebuild_journey_menu()

    # ---------------------------------------------------------------------
    # Edition dialogs (FN015/FN021/FN024/FN038) - TSK12
    # ---------------------------------------------------------------------
    def _edit_selected_block(self):
        """FN015: edit the selected block (label, note, content, journey
        attachments RG042, structured condition FN035 for Condition blocks)."""
        item = self._get_selected_item()
        if not isinstance(item, BlockNode):
            return
        nm = self._current_narrative_map()
        attached = JourneyService.attachment_journey_ids(nm, item.entity.id)
        artefacts = [a for a in self.project_service.current_project.agent if a.typ == "Artefact"]
        dialog = BlockDialog(item.entity, nm.journey, attached, artefacts, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        self.update_block_usecase.execute(
            item.entity, lb=values['lb'], note=values['note'], content=values['content'],
            condition=values['condition'], journey_ids=values['journey_ids'])
        item.update_entity_data()  # type label + tooltip refresh
        self.journeys_workspace.apply_journey_filter()
        self._update_menu_state()

    def _edit_selected_transition(self):
        """FN021: edit the selected transition's note."""
        item = self._get_selected_item()
        if not isinstance(item, Connection):
            return
        dialog = TransitionDialog(item.get_transition(), parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.update_transition_usecase.execute(item.get_transition(), note=dialog.get_values()['note'])
        self._update_menu_state()

    def _edit_journey(self):
        """FN024: edit the active journey (label, note)."""
        nm = self._current_narrative_map()
        active = nm.get_active_journey() if nm else None
        if active is None:
            return
        dialog = JourneyDialog(active, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        self.update_journey_usecase.execute(active, lb=values['lb'], note=values['note'])
        self._rebuild_journey_menu()
        self._update_menu_state()

    def _set_default_journey(self):
        """FN038/RG062: designate the default journey via a selection dialog
        (the active journey is not modified)."""
        nm = self._current_narrative_map()
        if nm is None or not nm.journey:
            return
        dialog = JourneySelectionDialog(nm.journey, parent=self, title="Set as Default Journey")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        chosen = dialog.get_selected_journey()
        if chosen is not None:
            self.set_default_journey_usecase.execute(chosen)
            self._rebuild_journey_menu()
            self._update_menu_state()

    # ---------------------------------------------------------------------
    # Context menu: dynamically aligned with the application menu (RG055)
    # ---------------------------------------------------------------------
    def _show_workspace_context_menu(self, item, global_pos):
        """Build the context menu from the application menu's own actions (same
        labels, shortcuts and enabled states), according to the selected
        graphical object; the chosen action triggers the same handler as the
        application menu."""
        menu = QMenu(self)
        menu.setStyleSheet(theme.CONTEXT_MENU_STYLESHEET)
        if isinstance(item, BlockNode):
            for key in ('blocks_edit', 'blocks_copy', 'blocks_delete'):
                menu.addAction(self.menu_actions[key])
        elif isinstance(item, Connection):
            for key in ('transitions_edit', 'transitions_delete'):
                menu.addAction(self.menu_actions[key])
        else:
            new_menu = menu.addMenu("New")  # aligned with Project > Narrative Blocks > New
            for key in ('blocks_new_scene', 'blocks_new_pivot', 'blocks_new_condition', 'blocks_new_ending'):
                new_menu.addAction(self.menu_actions[key])
            menu.addAction(self.menu_actions['transitions_new'])
        menu.exec(global_pos)

    # ---------------------------------------------------------------------
    # About dialogs (FN003/FN004)
    # ---------------------------------------------------------------------
    def _show_changelog(self):
        ChangeLogDialog(self.change_log_service, self).exec()

    def _show_about(self):
        AboutDialog(self.about_service, self).exec()
