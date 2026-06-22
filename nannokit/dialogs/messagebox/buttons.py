"""nannokit.dialogs.messagebox.buttons"""

from __future__ import annotations


class Buttons:
    """Button-set presets, named after .NET's ``MessageBoxButtons``.

    Each preset is a plain ``list[str]`` of button labels in display
    order, so you can also pass your own custom list to
    ``messagebox.show(..., buttons=["Discard", "Save", "Cancel"])``
    without needing a preset at all.
    """

    OK = ["OK"]
    OK_CANCEL = ["OK", "Cancel"]
    YES_NO = ["Yes", "No"]
    YES_NO_CANCEL = ["Yes", "No", "Cancel"]
    RETRY_CANCEL = ["Retry", "Cancel"]
    ABORT_RETRY_IGNORE = ["Abort", "Retry", "Ignore"]

    # Backwards-compatible alias for the original prototype's name.
    YESNO = YES_NO
