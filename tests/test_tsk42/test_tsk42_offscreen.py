# Application  : Hyperscript
# Script       : test_tsk42_offscreen.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen tests for TSK42 (session 12): "Files > Export Project..." exports
the project as a standalone HTML reading document (SU007/FN013 revised).

Menu states: export_project enabled only with a project open; export_map and
import_map stay greyed (MVP_GREYED) until further notice. _export_project:
folder chosen by the user (mocked QFileDialog), export folder created with
index.html + agents.html + journey-<id>.html + style.css, overwrite
confirmation when the folder exists, read-only (nothing marked modified).
"""

import os

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

import ui.main_window as mw_module
from ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def _isolated_user_state(tmp_path, monkeypatch):
    import config.user_state_loader as usl
    monkeypatch.setattr(usl, "_STATE_PATH", str(tmp_path / "user_state.json"))
    monkeypatch.setattr(usl, "_state", {})


def make_main_window():
    mw = MainWindow()
    mw._create_project()
    return mw


def close_main_window(mw):
    mw._teardown_workspace()
    mw.project_service.set_modified(False)
    mw.close()


class FakeFileDialog:
    next_dir = ""

    @staticmethod
    def getExistingDirectory(*args, **kwargs):
        return FakeFileDialog.next_dir


class FakeMessageBox:
    class StandardButton:
        Yes = 1
        No = 2

    answer = 1
    questions = []
    criticals = []

    @staticmethod
    def question(*args, **kwargs):
        FakeMessageBox.questions.append(args)
        return FakeMessageBox.answer

    @staticmethod
    def critical(*args, **kwargs):
        FakeMessageBox.criticals.append(args)


# ---------------------------------------------------------------------
# Menu states: export_project vs the greyed export_map / import_map
# ---------------------------------------------------------------------
def test_export_project_menu_entry_states(qapp):
    mw = MainWindow()  # no project open
    try:
        mw._update_menu_state()
        assert not mw.menu_actions['export_project'].isEnabled()
        assert not mw.menu_actions['export_map'].isEnabled()
        assert not mw.menu_actions['import_map'].isEnabled()
        mw._create_project()
        mw._update_menu_state()
        assert mw.menu_actions['export_project'].isEnabled()
        assert mw.menu_actions['export_project'].text() == "Export Project..."
        # TSK42: "Export Map..." / "Import Map..." stay greyed until further notice
        assert not mw.menu_actions['export_map'].isEnabled()
        assert not mw.menu_actions['import_map'].isEnabled()
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# _export_project: writes the export folder in the chosen parent dir
# ---------------------------------------------------------------------
def test_export_project_writes_folder(qapp, monkeypatch, tmp_path):
    mw = make_main_window()
    try:
        monkeypatch.setattr(mw_module, "QFileDialog", FakeFileDialog)
        monkeypatch.setattr(mw_module, "QMessageBox", FakeMessageBox)
        FakeFileDialog.next_dir = str(tmp_path)
        FakeMessageBox.answer = FakeMessageBox.StandardButton.Yes
        FakeMessageBox.questions = []
        mw._export_project()
        folder = os.path.join(str(tmp_path), "New project")  # project lb
        assert os.path.isdir(folder)
        names = set(os.listdir(folder))
        assert {"index.html", "agents.html", "style.css"} <= names
        assert any(n.startswith("journey-") and n.endswith(".html") for n in names)
        with open(os.path.join(folder, "index.html"), encoding="utf-8") as f:
            assert f.read().startswith("<!DOCTYPE html>")
        assert FakeMessageBox.questions == []  # folder did not exist: no confirmation
        assert not mw.project_service.is_modified  # read-only export (RG058)
    finally:
        close_main_window(mw)


def test_export_project_cancelled_dialog_writes_nothing(qapp, monkeypatch, tmp_path):
    mw = make_main_window()
    try:
        monkeypatch.setattr(mw_module, "QFileDialog", FakeFileDialog)
        FakeFileDialog.next_dir = ""  # cancelled
        mw._export_project()
        assert os.listdir(str(tmp_path)) == []
    finally:
        close_main_window(mw)


def test_export_project_existing_folder_asks_confirmation(qapp, monkeypatch, tmp_path):
    mw = make_main_window()
    try:
        monkeypatch.setattr(mw_module, "QFileDialog", FakeFileDialog)
        monkeypatch.setattr(mw_module, "QMessageBox", FakeMessageBox)
        FakeFileDialog.next_dir = str(tmp_path)
        folder = os.path.join(str(tmp_path), "New project")
        os.makedirs(folder)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write("OLD")
        # No -> no overwrite
        FakeMessageBox.answer = FakeMessageBox.StandardButton.No
        FakeMessageBox.questions = []
        mw._export_project()
        assert len(FakeMessageBox.questions) == 1
        with open(os.path.join(folder, "index.html"), encoding="utf-8") as f:
            assert f.read() == "OLD"
        # Yes -> files overwritten
        FakeMessageBox.answer = FakeMessageBox.StandardButton.Yes
        mw._export_project()
        with open(os.path.join(folder, "index.html"), encoding="utf-8") as f:
            assert f.read().startswith("<!DOCTYPE html>")
        assert not mw.project_service.is_modified
    finally:
        close_main_window(mw)
