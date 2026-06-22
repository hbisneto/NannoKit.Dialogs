"""
nannokit.dialogs.core.config
================================

Reserved extension point for package-wide configuration (default
button labels/locale, default icons, animation toggles, etc.).

Deliberately empty for now - kept as a real module (rather than added
later) so that future options have an obvious, stable home and don't
end up bolted onto :class:`DialogManager` or scattered across
individual dialogs.
"""

from __future__ import annotations


class DialogConfig:
    """Shared configuration for all dialogs.

    Reserved for future use (e.g. default locale, default button
    labels, default icon set).
    """
