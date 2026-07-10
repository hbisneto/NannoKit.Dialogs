"""
nannokit.dialogs
===================

C#-flavoured dialogs for `Textual <https://textual.textualize.io>`_ -
``MessageBox``, ``OpenFileDialog``, ``FolderBrowserDialog``,
``SaveFileDialog`` - usable standalone in any Textual app, or as an
official SuperNanno extension.

Quick start::

    from nannokit.dialogs import OpenFile, OpenFolder, SaveFile, messagebox

    OpenFile.show(callback=lambda path: ...)
    OpenFolder.show(callback=lambda folder: ...)
    SaveFile.show(default_filename="untitled.txt", callback=lambda path: ...)
    messagebox.show("Done!", buttons=messagebox.buttons.OK)

Each ``.show(...)`` call resolves the running Textual ``App``
automatically when called from inside an event handler/action/worker.
For anything else (background threads, startup scripts), register the
App once via :class:`~nannokit.dialogs.core.DialogManager`::

    from nannokit.dialogs.core import DialogManager

    class MyApp(App):
        def on_mount(self) -> None:
            DialogManager.attach(self)

Isolation and priority
-----------------------
``messagebox`` and ``filedialogs`` never interrupt or cancel one
another silently. Every dialog carries a :class:`~nannokit.dialogs.core.DialogPriority`
tier, and a shared :class:`~nannokit.dialogs.core.DialogQueue` decides,
whenever more than one dialog is requested around the same time,
whether the new one is stacked on top immediately (higher priority)
or queued to appear right after the current one is resolved (equal or
lower priority). See ``nannokit.dialogs.core.queue`` for details.
"""

from .core import DialogManager, DialogPriority, DialogQueue
from .filedialogs import(
    FileDialogResult,
    OpenFile, 
    OpenPath,
    OpenFolder, 
    SaveFile 
    )
from .messagebox import Buttons, MessageBoxIcon, messagebox

__all__ = [
    "OpenFile",
    "OpenFolder",
    "OpenPath",
    "SaveFile",
    "FileDialogResult",
    "messagebox",
    "Buttons",
    "MessageBoxIcon",
    "DialogManager",
    "DialogQueue",
    "DialogPriority",
]

__version__ = "0.1.0"
