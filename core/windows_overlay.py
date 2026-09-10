"""Windows overlay support via pywin32.

**Unverified** — written using the standard Win32 mechanisms for this
exact problem, but this project has only ever been built and run on macOS.
There is no Windows machine in this environment to confirm it actually
behaves as intended; see the README's "Platform support" section.

On Windows, `QWidget.winId()` already returns the native HWND directly (no
extra indirection needed, unlike macOS where it's an NSView pointer one
level removed from the NSWindow).

- Always-on-top: `SetWindowPos` with `HWND_TOPMOST`.
- Never steals focus: `WS_EX_NOACTIVATE` extended style.
- No taskbar button: `WS_EX_TOOLWINDOW` extended style — Windows has no
  separate "Dock" concept, so this single flag covers both roles that
  `core.mac_overlay` needs two different mechanisms for.
"""
from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def enforce_overlay(win_id: int) -> None:
    if sys.platform != "win32":
        return
    try:
        import win32con
        import win32gui

        hwnd = int(win_id)

        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        ex_style |= win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
        )
    except ImportError:
        logger.warning("windows_overlay: pywin32 not installed — overlay will use plain Qt always-on-top only")
    except Exception:
        logger.exception("windows_overlay: enforce_overlay failed")


def debug_overlay(win_id: int) -> None:
    if sys.platform != "win32":
        return
    try:
        import win32con
        import win32gui

        hwnd = int(win_id)
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        rect = win32gui.GetWindowRect(hwnd)
        is_topmost = bool(ex_style & win32con.WS_EX_TOPMOST) if hasattr(win32con, "WS_EX_TOPMOST") else "unknown"
        logger.info(
            "Windows overlay HWND state -> ex_style: 0x%08X (NOACTIVATE=%s, TOOLWINDOW=%s), topmost=%s, rect: %s",
            ex_style,
            bool(ex_style & win32con.WS_EX_NOACTIVATE),
            bool(ex_style & win32con.WS_EX_TOOLWINDOW),
            is_topmost,
            rect,
        )
    except ImportError:
        logger.warning("windows_overlay: pywin32 not installed, cannot read HWND state")
    except Exception:
        logger.exception("windows_overlay: debug_overlay failed")
