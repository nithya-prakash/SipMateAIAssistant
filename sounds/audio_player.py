import os
import subprocess

_EFFECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "effects")
_FALLBACK_SYSTEM_SOUND = "/System/Library/Sounds/Glass.aiff"


class AudioPlayer:
    """Plays each character's own sound effect (sounds/effects/<id>.mp3) when a
    reminder appears, via afplay. Falls back to a bundled macOS system sound if
    a character's file is missing, so sound is never just silently broken.

    Uses afplay rather than QSoundEffect/QtMultimedia: QSoundEffect failed to
    decode these MP3s at all in testing (silent no-op, no exception - only a
    console warning), while afplay handles MP3/AIFF/WAV natively and reliably.
    """

    def __init__(self):
        self._procs = []  # keep references so Popen objects aren't GC'd mid-play

    def _path_for(self, character_id: str) -> str:
        path = os.path.join(_EFFECTS_DIR, f"{character_id}.mp3")
        return path if os.path.exists(path) else _FALLBACK_SYSTEM_SOUND

    def play_for_character(self, character_id: str):
        path = self._path_for(character_id)
        if not os.path.exists(path):
            return
        self._procs = [p for p in self._procs if p.poll() is None][-4:]  # reap old ones
        self._procs.append(subprocess.Popen(["afplay", path]))

    def play_ting(self):
        """Generic notification chime - kept for callers that don't have a
        specific character in hand."""
        if os.path.exists(_FALLBACK_SYSTEM_SOUND):
            self._procs.append(subprocess.Popen(["afplay", _FALLBACK_SYSTEM_SOUND]))
