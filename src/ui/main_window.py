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
activated by the tab bar; "Journeys" (TSK11) and "Agents" (TSK19b) are
implemented: blocks/transitions graph with journey + agent filters
(FN029/FN039), agent cards on anchor dots, context menus dynamically
aligned with the application menu (RG055), layout persistence (RG060/RG067).
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
from ui.views import JourneysWorkspace, AgentsWorkspace, RelationshipsWorkspace
from ui.nodes.block_node import BlockNode
from ui.nodes.connection import Connection
from ui.nodes.agent_card import AgentCardItem
from ui.utils import theme
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.change_log_dialog import ChangeLogDialog
from ui.dialogs import (
    BlockDialog, TransitionDialog, JourneyDialog, JourneySelectionDialog,
    AgentDialog, AgentSelectionDialog, AgentAssociationDialog,
    RelationshipDialog, RelationshipSelectionDialog,
)
from core.services.journey_service import JourneyService
from core.services.journey_filter_service import JourneyFilterService
from core.services.agent_filter_service import AgentFilterService
from core.services.participation_service import ParticipationService
from core.services.project_service import ProjectService
from core.services.about_service import AboutService
from core.services.change_log_service import ChangeLogService
from core.services.layout_service import LayoutService
from core.services.relationship_service import RelationshipService
from core.models.view_model import ProjectLayout
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
from usecases.agent_management import (
    CreateAgentUseCase, UpdateAgentUseCase, DuplicateAgentUseCase, DeleteAgentUseCase,
)
from usecases.participation_management import (
    AssociateParticipationUseCase, DissociateParticipationUseCase,
)
from usecases.relationship_management import (
    CreateRelationshipUseCase, UpdateRelationshipUseCase, DeleteRelationshipUseCase,
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
        # Agent / participation use cases (TSK17/TSK18)
        self.create_agent_usecase = CreateAgentUseCase(self.project_service)
        self.update_agent_usecase = UpdateAgentUseCase(self.project_service)
        self.duplicate_agent_usecase = DuplicateAgentUseCase(self.project_service)
        self.delete_agent_usecase = DeleteAgentUseCase(self.project_service)
        self.associate_participation_usecase = AssociateParticipationUseCase(self.project_service)
        self.dissociate_participation_usecase = DissociateParticipationUseCase(self.project_service)
        # Relationship use cases (TSK20)
        self.create_relationship_usecase = CreateRelationshipUseCase(self.project_service)
        self.update_relationship_usecase = UpdateRelationshipUseCase(self.project_service)
        self.delete_relationship_usecase = DeleteRelationshipUseCase(self.project_service)

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
        self.tab_bar = TabBar(["Agents", "Journeys", "Relationships", "Export"])  # TSK28: Agents first; TSK30: Agents is the default active tab
        self.tab_bar.hide()
        main_layout.addWidget(self.tab_bar)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages, 1)

        # Welcome page (no project opened)
        self.welcome_page = QWidget()
        self.pages.addWidget(self.welcome_page)

        # View pages (project open); "Journeys" (TSK11) and "Agents" (TSK19b)
        # get a workspace when a project is opened, the others a placeholder
        self.view_pages = {}
        self.journeys_page = QWidget()
        QVBoxLayout(self.journeys_page).setContentsMargins(0, 0, 0, 0)
        self.pages.addWidget(self.journeys_page)
        self.view_pages["Journeys"] = self.journeys_page
        self.agents_page = QWidget()
        QVBoxLayout(self.agents_page).setContentsMargins(0, 0, 0, 0)
        self.pages.addWidget(self.agents_page)
        self.view_pages["Agents"] = self.agents_page
        self.relationships_page = QWidget()  # TSK27: workspace added in _init_workspace
        QVBoxLayout(self.relationships_page).setContentsMargins(0, 0, 0, 0)
        self.pages.addWidget(self.relationships_page)
        self.view_pages["Relationships"] = self.relationships_page
        for name in ("Export",):
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
        self.agents_workspace = None
        self.relationships_workspace = None  # TSK27
        self._last_journeys_block_id = None  # TSK27/FN032: block selected in "Journeys"
        self.journey_filter_active = False  # RG047/RG048: off by default, not persisted
        self.agent_filter_agent_id = None  # RG047/RG063: agent filter off by default, not persisted

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
        self.agent_menu = display_menu.addMenu("Agent")  # dynamic checkable list, built with the agents (FN039/RG063)
        self.menu_actions['agent_filter'] = self.agent_menu
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
        self.menu_actions['agents_new'] = agents_menu.addAction("New...", lambda: self._new_agent())
        self.menu_actions['agents_edit'] = agents_menu.addAction("Edit...", lambda: self._edit_agent())
        self.menu_actions['agents_copy'] = agents_menu.addAction("Copy", lambda: self._copy_agent())
        self.menu_actions['agents_delete'] = agents_menu.addAction("Delete...", lambda: self._delete_agent())
        self.menu_actions['agents_associate'] = agents_menu.addAction("Associate with Block...", lambda: self._associate_agent_with_block())
        blocks_menu = project_menu.addMenu("Blocks")
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
        self.menu_actions['relationships_new'] = relationships_menu.addAction("New...", lambda: self._new_relationship())
        self.menu_actions['relationships_edit'] = relationships_menu.addAction("Edit...", lambda: self._edit_relationship())
        self.menu_actions['relationships_delete'] = relationships_menu.addAction("Delete...", lambda: self._delete_relationship())

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
        'close', 'save', 'save_as', 'journey', 'agent_filter',
        'view_journeys', 'view_agents', 'view_relationships', 'view_export',
        'agents_new',
        'blocks_new', 'blocks_edit', 'blocks_copy', 'blocks_delete',
        'transitions_new', 'transitions_edit', 'transitions_delete',
        'journeys_new', 'journeys_edit', 'journeys_copy', 'journeys_set_default', 'journeys_delete',
        'relationships_new', 'relationships_edit', 'relationships_delete',
    }

    # Entries that additionally require at least one agent in the project (TSK18)
    AGENT_DEPENDENT = {
        'agents_edit', 'agents_copy', 'agents_delete', 'agents_associate',
    }

    # Entries that additionally require at least two agents (a pair) - TSK20
    TWO_AGENTS_DEPENDENT = {
        'relationships_new',
    }

    # Entries that additionally require at least one relationship - TSK20
    RELATIONSHIP_DEPENDENT = {
        'relationships_edit', 'relationships_delete',
    }

    def _update_menu_state(self):
        """Enable or disable menu entries based on the project state (RG006/RG007/RG008)."""
        has_project = self.project_opened
        for key, action in self.menu_actions.items():
            if key in self.MVP_GREYED:
                action.setEnabled(False)
            elif key in self.AGENT_DEPENDENT:
                has_agents = has_project and bool(self.project_service.current_project.agent)
                action.setEnabled(has_agents)
            elif key in self.TWO_AGENTS_DEPENDENT:
                has_pair = has_project and len(self.project_service.current_project.agent) >= 2
                action.setEnabled(has_pair)
            elif key in self.RELATIONSHIP_DEPENDENT:
                nm = self._current_narrative_map() if has_project else None
                action.setEnabled(has_project and nm is not None and bool(nm.relationship))
            elif key in self.PROJECT_DEPENDENT:
                action.setEnabled(has_project)
            else:
                action.setEnabled(True)
        # "Save" is enabled only when the open project is modified (RG006)
        self.menu_actions['save'].setEnabled(has_project and self.project_service.is_modified)
        # TSK27: keep the "Relationships" view in sync with the model
        if has_project and self.relationships_workspace is not None:
            self.relationships_workspace.refresh()

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
        self.pages.setCurrentWidget(self.view_pages["Agents"])  # TSK30 (1.1): default view is "Agents"
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
            self.pages.setCurrentWidget(self.view_pages["Agents"])  # TSK30 (1.1): default view is "Agents"
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
                # RG067/RG070: agent card positions and the "Relationships"
                # matrix axis order are persisted at project level
                if self.agents_workspace is not None or self.relationships_workspace is not None:
                    project_layout = (self.agents_workspace.collect_project_layout()
                                      if self.agents_workspace is not None else ProjectLayout())
                    if self.relationships_workspace is not None:  # TSK27
                        self.relationships_workspace.collect_project_layout(project_layout)
                    LayoutService.save_project_layout(file_path, project_layout)
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
        """Create the Journeys and Agents workspaces and populate them from
        the saved layouts (RG060/RG067) or with default positions (FN028)."""
        nm = self._current_narrative_map()
        if nm is None:
            return
        self._teardown_workspace()
        project = self.project_service.current_project
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

        # Agents view (TSK19b): one card per project agent, positions from
        # the project-level layout (RG067) or free anchor-dot positions
        agents_workspace = AgentsWorkspace(project=project, info_bar=self.info_bar, main_window=self)
        agents_workspace.workspace_modified.connect(self._on_workspace_modified)
        agents_workspace.context_menu_requested.connect(self._show_agents_context_menu)
        self.agents_page.layout().addWidget(agents_workspace)
        self.agents_workspace = agents_workspace
        saved_project_layout = None
        if self.project_service.file_path:
            saved_project_layout = LayoutService.load_project_layout(self.project_service.file_path)
        agents_workspace.populate_agents(project, saved_project_layout)

        # Relationships view (TSK27): matrix + side panel; axis order from the
        # project-level layout (RG070)
        workspace.selection_changed.connect(self._on_journeys_selection_changed)
        relationships_workspace = RelationshipsWorkspace(project=project, narrative_map=nm,
                                                         info_bar=self.info_bar, main_window=self)
        relationships_workspace.anchor_block_selected.connect(self._on_relationships_anchor_selected)
        relationships_workspace.journey_filter_requested.connect(self._on_relationships_journey_filter_requested)  # TSK30 (4.1)
        relationships_workspace.agent_filter_requested.connect(self._set_agent_filter)
        relationships_workspace.context_menu_requested.connect(self._show_relationships_context_menu)
        relationships_workspace.cell_clicked.connect(self._on_relationship_cell_clicked)  # TSK29
        relationships_workspace.workspace_modified.connect(self._on_workspace_modified)
        self.relationships_page.layout().addWidget(relationships_workspace)
        self.relationships_workspace = relationships_workspace
        relationships_workspace.populate(project, nm, saved_project_layout)

        # RG047/RG048/RG063: the filters are disabled by default, not persisted
        # (map views only — never applied to the "Agents" view)
        self.journey_filter_active = False
        workspace.set_journey_filter_active(False)
        self.agent_filter_agent_id = None
        workspace.set_agent_filter(None)
        if self.relationships_workspace is not None:  # TSK27
            self.relationships_workspace.set_journey_filter_active(False)
            self.relationships_workspace.set_agent_filter(None)
        self._rebuild_journey_menu()
        self._rebuild_agent_menu()
        self.tab_bar.show()
        self.tab_bar.forceCurrentTab("Agents")  # TSK30 (1.1): default active tab is "Agents"

    def _teardown_workspace(self):
        if self.journeys_workspace is not None:
            self.journeys_workspace.setParent(None)
            self.journeys_workspace.deleteLater()
            self.journeys_workspace = None
        if self.agents_workspace is not None:
            self.agents_workspace.setParent(None)
            self.agents_workspace.deleteLater()
            self.agents_workspace = None
        if self.relationships_workspace is not None:  # TSK27
            self.relationships_workspace.setParent(None)
            self.relationships_workspace.deleteLater()
            self.relationships_workspace = None
        self._last_journeys_block_id = None
        self.journey_filter_active = False
        self.agent_filter_agent_id = None
        self.tab_bar.hide()

    def _on_tab_changed(self, tab_name: str):
        page = self.view_pages.get(tab_name)
        if page is not None:
            self.pages.setCurrentWidget(page)
        if tab_name == "Relationships" and self.relationships_workspace is not None:
            # FN032/RG069 (TSK27): forward the block selected in "Journeys" if
            # it belongs to the active filters, otherwise the Start block
            block_id = self._last_journeys_block_id
            if block_id is None or not self._block_in_active_filters(block_id):
                nm = self._current_narrative_map()
                start = next((b for b in nm.block if b.typ == "Start"), None) if nm else None
                block_id = start.id if start else None
            if block_id is not None:
                self.relationships_workspace.set_anchor_block(block_id)

    def _block_in_active_filters(self, block_id: int) -> bool:
        """RG048/RG063/RG064: an element outside the active filters is not selectable."""
        nm = self._current_narrative_map()
        if nm is None:
            return False
        if self.journey_filter_active:
            active = nm.get_active_journey()
            if block_id not in JourneyFilterService.visible_block_ids(nm, active.id if active else None):
                return False
        if self.agent_filter_agent_id is not None:
            if block_id not in AgentFilterService.visible_block_ids(nm, self.agent_filter_agent_id):
                return False
        return True

    def _on_journeys_selection_changed(self, item):
        """TSK27/FN032: remember the block selected in "Journeys" to forward it
        to the "Relationships" view on tab switch."""
        self._last_journeys_block_id = item.entity.id if isinstance(item, BlockNode) else None

    def _on_relationships_anchor_selected(self, block_id: int):
        nm = self._current_narrative_map()
        block = next((b for b in nm.block if b.id == block_id), None) if nm else None
        if block is not None:
            self.info_bar.show_message(f"Anchor block: {block.lb} ({block.typ})")

    # ---------------------------------------------------------------------
    # Blocks and transitions actions (FN014/FN016/FN018/FN020/FN022)
    # ---------------------------------------------------------------------
    def _create_new_block(self, typ: str):
        """FN014: create a block of the given type at the first free grid position
        anchored on the Start block (TSK16, option B), not at the scene center."""
        if self.journeys_workspace is None:
            return
        block = self.create_block_usecase.execute(typ, filter_active=self.journey_filter_active)  # RG040
        x, y = self.journeys_workspace.next_free_creation_position()
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
    def _resync_relationships_panel(self):
        """TSK30 (4.1): rebuild the side panel of the "Relationships" view after
        a journey CRUD (the journey list of the combo may have changed); the
        current filters are kept."""
        if self.relationships_workspace is not None:
            self.relationships_workspace.refresh()

    def _new_journey(self):
        """FN023: create a journey (not activated; the active journey is unchanged)."""
        self.create_journey_usecase.execute()
        self._rebuild_journey_menu()
        self._resync_relationships_panel()
        self._update_menu_state()

    def _copy_journey(self):
        """FN025/RG043: duplicate the active journey (block attachments copied)."""
        nm = self._current_narrative_map()
        active = nm.get_active_journey() if nm else None
        if active is not None:
            self.duplicate_journey_usecase.execute(active)
        self._rebuild_journey_menu()
        self._resync_relationships_panel()
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
            self.journeys_workspace.apply_filters()
        self._resync_relationships_panel()
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

    def _on_relationships_journey_filter_requested(self, journey_id):
        """TSK30 (4.1): the side panel journey combo mirrors Display > Journey -
        choosing a journey activates it (FN026) and enables the filter (FN029);
        "All journeys" (None) disables the filter."""
        if journey_id is None:
            self._set_journey_filter_active(False)
            return
        nm = self._current_narrative_map()
        journey = next((j for j in nm.journey if j.id == journey_id), None) if nm else None
        if journey is not None:
            self._activate_journey(journey)

    def _set_journey_filter_active(self, active: bool):
        """FN029/RG048: toggle the journey filter on the map views (visual only,
        RG047: does not mark the project as modified)."""
        self.journey_filter_active = active
        if self.journeys_workspace is not None:
            self.journeys_workspace.set_journey_filter_active(active)
        if self.relationships_workspace is not None:  # TSK27: resync the side panel
            self.relationships_workspace.set_journey_filter_active(active)
        self._rebuild_journey_menu()

    def _rebuild_agent_menu(self):
        """Rebuild the Display > Agent menu dynamically (FN039/RG063):
        checkable 'All agents' on top (checked = filter disabled), then one
        checkable entry per project agent."""
        self.agent_menu.clear()
        all_action = self.agent_menu.addAction(_get_config("agent_list_all_label", "All agents"))
        all_action.setCheckable(True)
        all_action.setChecked(self.agent_filter_agent_id is None)
        all_action.triggered.connect(lambda: self._set_agent_filter(None))
        self.agent_menu.addSeparator()
        project = self.project_service.current_project
        if project is not None:
            for agent in project.agent:
                action = self.agent_menu.addAction(agent.lb)
                action.setCheckable(True)
                action.setChecked(self.agent_filter_agent_id == agent.id)
                action.triggered.connect(lambda _checked=False, a=agent: self._set_agent_filter(a.id))

    def _set_agent_filter(self, agent_id):
        """FN039/RG063: set the agent filter on the map views (agent id, or
        None = 'All agents'); with the journey filter also active, the
        intersection applies (RG064). Visual only, not persisted (RG047)."""
        self.agent_filter_agent_id = agent_id
        if self.journeys_workspace is not None:
            self.journeys_workspace.set_agent_filter(agent_id)
        if self.relationships_workspace is not None:  # TSK27: resync the side panel
            self.relationships_workspace.set_agent_filter(agent_id)
        self._rebuild_journey_menu()
        self._rebuild_agent_menu()

    # ---------------------------------------------------------------------
    # Agents actions (FN031) + association with a block (FN030) - TSK18
    # ---------------------------------------------------------------------
    def _select_agent(self, title: str = "Select Agent"):
        """Agent selection dialog (FN031); None when cancelled."""
        project = self.project_service.current_project
        dialog = AgentSelectionDialog(project.agent, parent=self, title=title)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.get_selected_agent()

    def _new_agent(self):
        """FN031: create an agent (creation dialog)."""
        project = self.project_service.current_project
        dialog = AgentDialog(parent=self, default_label=f"Agent {project.get_next_id('agent')}")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        agent = self.create_agent_usecase.execute(lb=values['lb'], typ=values['typ'],
                                                  note=values['note'], content=values['content'])
        if self.agents_workspace is not None:
            self.agents_workspace.add_agent_card(agent)  # TSK19b: one card per agent
        self.info_bar.show_message(f"Agent '{values['lb']}' created")
        self._rebuild_agent_menu()
        self._update_menu_state()

    def _edit_agent(self, agent=None):
        """FN031: edit an agent (selection dialog + edition dialog). The agent
        can be passed directly (context menu of an agent card, TSK19b)."""
        if agent is None:
            agent = self._select_agent("Edit Agent")
        if agent is None:
            return
        dialog = AgentDialog(agent, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        self.update_agent_usecase.execute(agent, lb=values['lb'], typ=values['typ'],
                                          note=values['note'], content=values['content'])
        if self.agents_workspace is not None:
            self.agents_workspace.refresh_agent_card(agent)  # TSK19b
        self.info_bar.show_message(f"Agent '{agent.lb}' updated")
        self._refresh_participation_badges()  # agent labels appear in the block tooltips
        self._rebuild_agent_menu()
        self._update_menu_state()

    def _copy_agent(self, agent=None):
        """FN031: duplicate an agent (the agent can be passed directly from
        the context menu of an agent card, TSK19b)."""
        if agent is None:
            agent = self._select_agent("Copy Agent")
        if agent is None:
            return
        copy = self.duplicate_agent_usecase.execute(agent)
        if self.agents_workspace is not None:
            self.agents_workspace.add_agent_card(copy)  # TSK19b
        self.info_bar.show_message(f"Agent '{copy.lb}' created")
        self._rebuild_agent_menu()
        self._update_menu_state()

    def _delete_agent(self, agent=None):
        """FN031/RG033: delete an agent, with a confirmation reporting
        the number of cascaded elements; the cascade itself is done by the use case.
        The agent can be passed directly (context menu of an agent card, TSK19b)."""
        if agent is None:
            agent = self._select_agent("Delete Agent")
        if agent is None:
            return
        project = self.project_service.current_project
        n_part = len(ParticipationService.get_agent_participations(project, agent.id))
        n_rel = len(ParticipationService.get_agent_relationships(project, agent.id))
        cascaded = n_part + n_rel
        if cascaded:
            message = (f"Agent '{agent.lb}' is linked to {cascaded} element(s) "
                       f"({n_part} participation(s), {n_rel} relationship(s)). "
                       f"Delete the agent and all of them?")
        else:
            message = f"Delete agent '{agent.lb}'?"
        reply = QMessageBox.question(self, "Confirmation", message,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        result = self.delete_agent_usecase.execute(agent.id)
        if result is None:
            self.info_bar.show_message("Cannot delete agent")
            return
        removed = result['removed']
        total = removed['participation'] + removed['relationship']
        if total:
            self.info_bar.show_message(
                f"Agent deleted; {total} associated element(s) removed with it (cascade)")  # RG033
        else:
            self.info_bar.show_message("Agent deleted")
        self._refresh_participation_badges()
        if self.agents_workspace is not None:
            self.agents_workspace.remove_agent_card(agent.id)  # TSK19b
        self._rebuild_agent_menu()
        self._update_menu_state()

    def _associate_agent_with_block(self, agent=None):
        """FN030: 'Associate with Block...' - pick an agent (or take the one
        of the agent card that opened the context menu, TSK19b), then the
        block currently selected in the Journeys view, and open the
        association dialog."""
        if agent is None:
            agent = self._select_agent("Associate Agent with Block")
        if agent is None:
            return
        item = self._get_selected_item()
        if not isinstance(item, BlockNode):
            self.info_bar.show_message("Select a block in the Journeys view first")
            return
        self._open_association_dialog(item.entity)

    def _open_association_dialog(self, block):
        """Open the agent association dialog for a block (FN030); the dialog's
        signals are applied through the use cases (RG058), then the block
        badges are refreshed. Also used by the block context menu (TSK19)."""
        project = self.project_service.current_project
        dialog = AgentAssociationDialog(
            project.agent, block, self._participating_agent_ids(block.id),
            new_agent_label=f"Agent {project.get_next_id('agent')}", parent=self)
        dialog.participation_toggled.connect(
            lambda agent_id, checked: self._on_participation_toggled(block, agent_id, checked, dialog))
        dialog.agent_create_requested.connect(
            lambda values: self._on_agent_create_requested(block, values, dialog))
        dialog.exec()
        self._update_menu_state()

    def _participating_agent_ids(self, block_id: int) -> set:
        nm = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        return {p.agent_id for p in ParticipationService.get_block_participations(nm, block_id)}

    def _on_participation_toggled(self, block, agent_id: int, checked: bool, dialog):
        if checked:
            self.associate_participation_usecase.execute(agent_id, block.id)
            dialog.set_status(f"Agent associated with '{block.lb}'")
        else:
            self.dissociate_participation_usecase.execute(agent_id, block.id)
            dialog.set_status(f"Agent dissociated from '{block.lb}'")
        self._refresh_participation_badges()
        dialog.refresh(self.project_service.current_project.agent,
                       self._participating_agent_ids(block.id))

    def _on_agent_create_requested(self, block, values: dict, dialog):
        """FN030: create the agent and associate it with the block in one operation."""
        agent = self.create_agent_usecase.execute(lb=values['lb'], typ=values['typ'],
                                                  note=values['note'], content=values['content'])
        self.associate_participation_usecase.execute(agent.id, block.id)
        if self.agents_workspace is not None:
            self.agents_workspace.add_agent_card(agent)  # TSK19b
        self._rebuild_agent_menu()
        dialog.set_status(f"Agent '{agent.lb}' created and associated")
        self._refresh_participation_badges()
        dialog.refresh(self.project_service.current_project.agent,
                       self._participating_agent_ids(block.id))

    def _refresh_participation_badges(self):
        if self.journeys_workspace is not None:
            self.journeys_workspace.refresh_all_participation_badges()

    # ---------------------------------------------------------------------
    # Relationships actions (FN034, SU011) - TSK20
    # ---------------------------------------------------------------------
    def _select_relationship(self, title: str = "Select Relationship"):
        """Relationship selection dialog (FN034); None when cancelled or no relationship."""
        project = self.project_service.current_project
        nm = self._current_narrative_map()
        if project is None or nm is None or not nm.relationship:
            return None
        dialog = RelationshipSelectionDialog(nm.relationship, project, nm, parent=self, title=title)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.get_selected_relationship()

    def _new_relationship(self):
        """FN034: create a relationship (creation dialog)."""
        project = self.project_service.current_project
        nm = self._current_narrative_map()
        dialog = RelationshipDialog(project.agent, nm, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        rel = self.create_relationship_usecase.execute(
            values['agent_1_id'], values['agent_2_id'], values['typ'], values['block_id'],
            note=values['note'], content=values['content'])
        if rel is None:
            self.info_bar.show_message(
                "Relationship refused: a relationship already exists for this (block, agent pair) (RG035)")
            return
        self.info_bar.show_message(f"Relationship '{rel.typ}' created")
        self._update_menu_state()

    def _edit_relationship(self):
        """FN034: edit a relationship (selection dialog + edition dialog)."""
        rel = self._select_relationship("Edit Relationship")
        if rel is None:
            return
        project = self.project_service.current_project
        nm = self._current_narrative_map()
        dialog = RelationshipDialog(project.agent, nm, entity=rel, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        result = self.update_relationship_usecase.execute(
            rel, typ=values['typ'], block_id=values['block_id'],
            note=values['note'], content=values['content'])
        if result is None:
            self.info_bar.show_message(
                "Relationship refused: the new anchor block already holds a relationship for this pair (RG035)")
            return
        self.info_bar.show_message("Relationship updated")
        self._update_menu_state()

    def _delete_relationship(self):
        """FN034/SU011: delete a relationship, with prior confirmation."""
        rel = self._select_relationship("Delete Relationship")
        if rel is None:
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Delete the relationship '{rel.typ}' (anchor block #{rel.block_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        if self.delete_relationship_usecase.execute(rel.id):
            self.info_bar.show_message("Relationship deleted")
        self._update_menu_state()

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
        self.journeys_workspace.apply_filters()
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
        self._resync_relationships_panel()
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
            self._resync_relationships_panel()
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
            # FN030 (TSK19b): context-menu label on a block, same handler as
            # Project > Agents > Associate with Block...
            project = self.project_service.current_project
            has_agents = project is not None and bool(project.agent)
            associate_action = menu.addAction(
                "Associate agents...", lambda: self._open_association_dialog(item.entity))
            associate_action.setEnabled(has_agents)
        elif isinstance(item, Connection):
            for key in ('transitions_edit', 'transitions_delete'):
                menu.addAction(self.menu_actions[key])
        else:
            # TSK16: on the empty grid the creation entries carry context-menu
            # labels ("New Block" / "New Transition"); the same handlers as
            # the application menu (Project > Blocks > New, Project >
            # Transitions > New) are triggered
            new_block_menu = menu.addMenu("New Block")
            for key in ('blocks_new_scene', 'blocks_new_pivot', 'blocks_new_condition', 'blocks_new_ending'):
                new_block_menu.addAction(self.menu_actions[key])
            menu.addAction("New Transition", self._start_transition_creation)
        menu.exec(global_pos)

    def _show_relationships_context_menu(self, row, col, global_pos):
        """RG055 (TSK27): context menu of a matrix cell - same handlers as
        Project > Relationships, plus 'View in Journeys view' (FN032)."""
        menu = QMenu(self)
        menu.setStyleSheet(theme.CONTEXT_MENU_STYLESHEET)
        new_action = menu.addAction("New...", self._new_relationship)
        edit_action = menu.addAction("Edit...", self._edit_relationship)
        delete_action = menu.addAction("Delete...", self._delete_relationship)
        new_action.setEnabled(self.menu_actions['relationships_new'].isEnabled())
        edit_action.setEnabled(self.menu_actions['relationships_edit'].isEnabled())
        delete_action.setEnabled(self.menu_actions['relationships_delete'].isEnabled())
        # RG069: with the agent filter active, creation is forbidden on a pair
        # not involving the filtered agent
        if (self.relationships_workspace is not None and row >= 0 and col >= 0
                and self.agent_filter_agent_id is not None):
            a_row = self.relationships_workspace.agent_id_at_row(row)
            a_col = self.relationships_workspace.agent_id_at_col(col)
            if self.agent_filter_agent_id not in (a_row, a_col):
                new_action.setEnabled(False)
        menu.addSeparator()
        view_action = menu.addAction("View in Journeys view")
        action = menu.exec(global_pos)
        if action is view_action:
            self._view_relationship_anchor_in_journeys(row, col)

    def _on_relationship_cell_clicked(self, row, col):
        """TSK29/TSK30 (3.7): left click on a matrix cell - if the pair has a
        relationship at the selected block, open its edit dialog; otherwise
        create an "Undefined" relationship directly (pair + current anchor
        block), no dialog."""
        ws = self.relationships_workspace
        nm = self._current_narrative_map()
        project = self.project_service.current_project
        if ws is None or nm is None or project is None:
            return
        a_row, a_col = ws.agent_id_at_row(row), ws.agent_id_at_col(col)
        if a_row is None or a_col is None:
            return
        anchor = ws.get_anchor_block_id()
        rel = RelationshipService.pair_state_at_block(nm, a_row, a_col, anchor) if anchor else None
        if rel is not None:
            dialog = RelationshipDialog(project.agent, nm, entity=rel, parent=self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            values = dialog.get_values()
            result = self.update_relationship_usecase.execute(
                rel, typ=values['typ'], block_id=values['block_id'],
                note=values['note'], content=values['content'])
            if result is None:
                self.info_bar.show_message(
                    "Relationship refused: the new anchor block already holds a relationship for this pair (RG035)")
                return
            self.info_bar.show_message("Relationship updated")
        else:
            if anchor is None:
                self.info_bar.show_message("Select an anchor block in the side panel first")
                return
            # TSK30 (3.7): direct creation of an "Undefined" relationship
            rel = self.create_relationship_usecase.execute(a_row, a_col, "Undefined", anchor)
            if rel is None:
                self.info_bar.show_message(
                    "Relationship refused: a relationship already exists for this (block, agent pair) (RG035)")
                return
            self.info_bar.show_message(f"Relationship '{rel.typ}' created")
        self.relationships_workspace.refresh()
        self._update_menu_state()

    def _view_relationship_anchor_in_journeys(self, row, col):
        """FN032/RG056 (TSK27): switch to "Journeys" and focus the anchor block
        of the cell's relationship state (or the current anchor block)."""
        ws = self.relationships_workspace
        nm = self._current_narrative_map()
        if ws is None or nm is None:
            return
        a_row, a_col = ws.agent_id_at_row(row), ws.agent_id_at_col(col)
        block_id = ws.get_anchor_block_id()
        if a_row is not None and a_col is not None and block_id is not None:
            rel = RelationshipService.pair_state_at_block(nm, a_row, a_col, block_id)
            if rel is not None:
                block_id = rel.block_id
        self.tab_bar.forceCurrentTab("Journeys")
        if self.journeys_workspace is not None and block_id is not None:
            self.journeys_workspace.focus_block(block_id)

    def _show_agents_context_menu(self, item, global_pos):
        """Context menu of the "Agents" view (RG055): same labels and enabled
        states as the application menu (Project > Agents), with the handlers
        applied to the agent of the card under the cursor (TSK19b); on the
        empty area, the creation entry ("New...")."""
        menu = QMenu(self)
        menu.setStyleSheet(theme.CONTEXT_MENU_STYLESHEET)
        if isinstance(item, AgentCardItem):
            agent = item.entity
            for key, handler in (('agents_edit', self._edit_agent),
                                 ('agents_copy', self._copy_agent),
                                 ('agents_delete', self._delete_agent),
                                 ('agents_associate', self._associate_agent_with_block)):
                src = self.menu_actions[key]
                action = menu.addAction(src.text())
                action.setEnabled(src.isEnabled())
                action.triggered.connect(lambda _checked=False, h=handler, a=agent: h(a))
        else:
            menu.addAction(self.menu_actions['agents_new'])
        menu.exec(global_pos)

    # ---------------------------------------------------------------------
    # About dialogs (FN003/FN004)
    # ---------------------------------------------------------------------
    def _show_changelog(self):
        ChangeLogDialog(self.change_log_service, self).exec()

    def _show_about(self):
        AboutDialog(self.about_service, self).exec()
