# utils/platform_utils.py
"""
Cross-platform utility functions for window management and OS-specific paths.
"""

import platform

from utils.logger import setup_logger

logger = setup_logger("utils.platform")

SYSTEM = platform.system()


def get_active_window_title() -> str:
    """
    Get the title of the currently active/focused window.
    Works on Windows. Returns placeholder on other platforms.
    """
    try:
        if SYSTEM == "Windows":
            import pygetwindow as gw

            active_window = gw.getActiveWindow()
            if active_window:
                title: str = str(active_window.title)
                if not title or title.strip() == "":
                    return "No Active Window"
                if "ProductivityAnalyzer" in title:
                    return "ProductivityAnalyzer (Self)"
                return title
            return "No Active Window"

        elif SYSTEM == "Darwin":
            try:
                from AppKit import NSWorkspace  # type: ignore[import-untyped]

                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                result: str = str(active_app.get("NSApplicationName", "No Active Window"))
                return result
            except ImportError:
                return "macOS (install pyobjc for tracking)"

        elif SYSTEM == "Linux":
            import subprocess

            try:
                proc = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowname"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                return proc.stdout.strip() or "No Active Window"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return "Linux (install xdotool for tracking)"

        return "Unsupported OS"

    except Exception as e:
        logger.error(f"Error getting active window: {e}")
        return "Error"


def minimize_window(window_title: str) -> bool:
    """Minimize a window by its title. Windows only."""
    try:
        if SYSTEM == "Windows":
            import pygetwindow as gw

            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                windows[0].minimize()
                return True
        return False
    except Exception as e:
        logger.error(f"Error minimizing window '{window_title}': {e}")
        return False


def get_hosts_path() -> str:
    """Get the system hosts file path based on the OS."""
    if SYSTEM == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    elif SYSTEM in ("Linux", "Darwin"):
        return "/etc/hosts"
    else:
        raise OSError(f"Unsupported operating system: {SYSTEM}")
