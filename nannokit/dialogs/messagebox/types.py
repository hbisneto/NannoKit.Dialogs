"""nannokit.dialogs.messagebox.types"""

from __future__ import annotations


class MessageBoxIcon:
    """Icon/severity used by :class:`MessageDialog`.

    Named after .NET's ``MessageBoxIcon`` for the familiar feel; each
    value also drives the dialog's border color and icon glyph (see
    ``styles/messagebox.tcss`` and ``MessageDialog.ICONS``).
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


# Backwards-compatible alias - the original prototype exposed this
# class as `messagebox.type`, i.e. as `Types`. Keep both names so
# existing call sites (`messagebox.type.INFO`) keep working verbatim.
Types = MessageBoxIcon
