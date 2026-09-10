"""Single entry point `ui/overlay_window.py` and `main.py` use for
platform-specific always-on-top / no-focus-steal / no-taskbar-icon behavior.

Dispatches by `sys.platform`. Only the macOS path (`core.mac_overlay`) has
actually been run and verified on real hardware — see the README's
"Platform support" section. Windows (`core.windows_overlay`) and Linux
(`core.linux_overlay`) implement the equivalent OS-native mechanism for the
same behavior, but this project has only ever been built and run on macOS,
so treat those two as best-effort and unverified.

Every function here is defensive: a missing platform dependency or any
runtime failure is logged and swallowed, never raised — a broken overlay
enforcement call must never crash the app or stop reminders from firing.
"""
from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def enforce_overlay(win_id: int) -> None:
    """Call every time the overlay is shown (and periodically while visible)
    to keep it above other apps, non-activating, and off the taskbar/Dock."""
    try:
        if sys.platform == "darwin":
            from core.mac_overlay import enforce_mac_overlay
            enforce_mac_overlay(win_id)
        elif sys.platform == "win32":
            from core.windows_overlay import enforce_overlay as _enforce
            _enforce(win_id)
        elif sys.platform.startswith("linux"):
            from core.linux_overlay import enforce_overlay as _enforce
            _enforce(win_id)
        else:
            logger.warning("overlay_platform: unsupported platform %s — no native overlay enforcement applied", sys.platform)
    except Exception:
        logger.exception("overlay_platform: enforce_overlay failed")


def debug_overlay(win_id: int) -> None:
    """Logs the live native window state — used by the tray's manual 'Test Overlay' trigger."""
    try:
        if sys.platform == "darwin":
            from core.mac_overlay import debug_mac_overlay
            debug_mac_overlay(win_id)
        elif sys.platform == "win32":
            from core.windows_overlay import debug_overlay as _debug
            _debug(win_id)
        elif sys.platform.startswith("linux"):
            from core.linux_overlay import debug_overlay as _debug
            _debug(win_id)
    except Exception:
        logger.exception("overlay_platform: debug_overlay failed")


def hide_from_taskbar_and_dock() -> None:
    """App-wide, one-time setup (called once at startup).

    macOS: hides the Dock icon via NSApplicationActivationPolicyAccessory.
    Windows/Linux: taskbar visibility is a per-window property there
    (WS_EX_TOOLWINDOW / _NET_WM_STATE_SKIP_TASKBAR), already handled inside
    `enforce_overlay` for the overlay window itself — there's nothing
    app-wide to set on those platforms, so this is a no-op there.
    """
    if sys.platform != "darwin":
        return
    try:
        from AppKit import NSApp, NSApplicationActivationPolicyAccessory
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except ImportError:
        logger.warning("overlay_platform: PyObjC not installed — the Dock icon will remain visible")
    except Exception:
        logger.exception("overlay_platform: hide_from_taskbar_and_dock failed")
