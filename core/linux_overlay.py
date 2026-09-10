"""Linux overlay support via raw Xlib EWMH hints.

**Unverified** — written against the EWMH spec most window managers (GNOME,
KDE, XFCE, i3, ...) honor, but this project has only ever been built and run
on macOS. There is no Linux machine in this environment to confirm it
behaves as intended, and Linux WM behavior is inherently the least uniform
of the three platforms — treat this as the roughest of the three best-effort
implementations. See the README's "Platform support" section.

This targets X11 (including XWayland). A native Wayland session has no
equivalent mechanism reachable from Qt's `winId()` — that's a known,
unaddressed gap, not something silently papered over.

Sends two `_NET_WM_STATE` client messages to the root window per the EWMH
spec: `_NET_WM_STATE_ABOVE` for always-on-top, `_NET_WM_STATE_SKIP_TASKBAR`
to keep it out of the taskbar (Linux has no separate "Dock" concept for a
non-application-window like this).
"""
from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)

_NET_WM_STATE_ADD = 1


def _send_state_client_message(disp, root, window, atom_name: str) -> None:
    from Xlib import X
    from Xlib.protocol import event

    net_wm_state = disp.intern_atom("_NET_WM_STATE")
    prop = disp.intern_atom(atom_name)

    client_event = event.ClientMessage(
        window=window,
        client_type=net_wm_state,
        data=(32, [_NET_WM_STATE_ADD, prop, 0, 1, 0]),
    )
    mask = X.SubstructureRedirectMask | X.SubstructureNotifyMask
    root.send_event(client_event, event_mask=mask)


def enforce_overlay(win_id: int) -> None:
    if not sys.platform.startswith("linux"):
        return
    try:
        from Xlib import display as xdisplay

        disp = xdisplay.Display()
        try:
            root = disp.screen().root
            window = disp.create_resource_object("window", win_id)

            _send_state_client_message(disp, root, window, "_NET_WM_STATE_ABOVE")
            _send_state_client_message(disp, root, window, "_NET_WM_STATE_SKIP_TASKBAR")

            disp.flush()
        finally:
            disp.close()
    except ImportError:
        logger.warning("linux_overlay: python-xlib not installed — overlay will use plain Qt always-on-top only")
    except Exception:
        logger.exception("linux_overlay: enforce_overlay failed (no X11 display, or window manager doesn't support EWMH)")


def debug_overlay(win_id: int) -> None:
    if not sys.platform.startswith("linux"):
        return
    try:
        from Xlib import display as xdisplay

        disp = xdisplay.Display()
        try:
            window = disp.create_resource_object("window", win_id)
            net_wm_state = disp.intern_atom("_NET_WM_STATE")
            prop = window.get_full_property(net_wm_state, 0)
            atom_ids = list(prop.value) if prop else []
            atom_names = [disp.get_atom_name(a) for a in atom_ids]
            logger.info("Linux overlay X11 _NET_WM_STATE atoms -> %s", atom_names)
        finally:
            disp.close()
    except ImportError:
        logger.warning("linux_overlay: python-xlib not installed, cannot read window state")
    except Exception:
        logger.exception("linux_overlay: debug_overlay failed")
