"""
nannokit.dialogs.core.theme
===============================

Reserved extension point for a future shared palette (so that
``messagebox``, ``filedialogs``, and any later dialog like
``ColorPicker`` can pull colors from one place instead of hardcoding
hex values independently in each ``.tcss`` file, as they do today).

Deliberately empty for now - see :mod:`nannokit.dialogs.core.config`
for the rationale of keeping this as a real, stable module.
"""

from __future__ import annotations


class DialogTheme:
    """Shared theme registry for all dialogs.

    Reserved for future use (e.g. custom palettes, dark/light mode).
    """
