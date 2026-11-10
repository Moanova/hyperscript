"""
Global pytest configuration for Hyperscript tests.
This file provides fixtures and options used across all test modules.
"""

import pytest
import os
import sys

# Make the src/ packages (config, core, ui, usecases) importable from the tests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))


def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--app-path",
        action="store",
        default=None,
        help="Path to the Hyperscript executable (e.g., C:/Program Files/Hyperscript/hyperscript.exe)"
    )
    parser.addoption(
        "--app-cmd",
        action="store",
        default=None,
        help="Full command line to launch Hyperscript (e.g., 'python src/main.py'). "
             "Alternative to --app-path when no executable is available."
    )
    parser.addoption(
        "--app-name",
        action="store",
        default=None,
        help="Name used to identify Hyperscript windows (matched against window titles). "
             "Defaults to 'Hyperscript'."
    )
    parser.addoption(
        "--capture-screenshots",
        action="store_true",
        default=False,
        help="Capture screenshots on test failures"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless mode (no visible UI)"
    )


@pytest.fixture(scope="session")
def app_exe_path(request):
    """
    Global fixture for the Hyperscript launch command.

    Returns either an executable path (when using --app-path / HYPERSCRIPT_PATH)
    or a full command line (when using --app-cmd / HYPERSCRIPT_CMD), e.g.
    'python src/main.py'. The returned value is suitable for
    pywinauto.Application().start(...).
    """
    cmd = request.config.getoption("--app-cmd")
    if cmd is None:
        cmd = os.getenv("HYPERSCRIPT_CMD")
    if cmd is not None:
        return cmd

    path = request.config.getoption("--app-path")
    if path is None:
        # Try environment variable
        path = os.getenv("HYPERSCRIPT_PATH")
    if path is None:
        # Default path (Windows)
        path = r"C:\Program Files\Hyperscript\hyperscript.exe"
    if not os.path.exists(path):
        pytest.skip(f"Hyperscript executable not found at: {path}")
    return path


@pytest.fixture(scope="session")
def app_window_name(request):
    """Name used to identify Hyperscript windows (matched against window titles)."""
    name = request.config.getoption("--app-name")
    if name is None:
        name = os.getenv("HYPERSCRIPT_WINDOW_NAME")
    if name is None:
        name = "Hyperscript"
    return name


@pytest.fixture(scope="module")
def kill_existing_instances(app_window_name):
    """Close all existing instances of Hyperscript before running tests."""
    from pywinauto import Desktop
    import time

    try:
        desktop = Desktop(backend="uia")
        for window in desktop.windows():
            if app_window_name.lower() in window.window_text().lower():
                window.close()
        time.sleep(1)  # Wait for windows to close
    except Exception:
        pass  # Ignore errors during cleanup

    yield

    # Additional cleanup after tests
    try:
        desktop = Desktop(backend="uia")
        for window in desktop.windows():
            if app_window_name.lower() in window.window_text().lower():
                window.close()
    except Exception:
        pass


@pytest.fixture(scope="module")
def launch_app(app_exe_path, kill_existing_instances):
    """Launch the Hyperscript application and return the Application object."""
    from pywinauto import Application

    # wait_for_idle=False avoids WaitForInputIdle, which fails (error 1471)
    # when the launched process is not directly a GUI process (e.g. python.exe
    # running a Qt script). Tests poll for the window themselves.
    app = Application(backend="uia").start(app_exe_path, wait_for_idle=False)
    yield app

    # Teardown: Close the application
    try:
        app.kill()
    except Exception:
        pass
