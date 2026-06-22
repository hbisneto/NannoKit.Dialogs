# nannokit.dialogs

Dialogs extension for [SuperNanno](https://github.com/hbisneto/SuperNanno) - `MessageBox`,
`OpenFileDialog`, `FolderBrowserDialog`, `SaveFileDialog`, reimagined for
[Textual](https://textual.textualize.io), with an API that feels like home if
you come from C#/.NET.

```python
from nannokit.dialogs import OpenFile, OpenFolder, SaveFile, messagebox

OpenFile.show(
    initial_directory=".",
    filters=["*.py", "*.toml"],
    callback=lambda path: print("Opened:", path),
)

OpenFolder.show(callback=lambda folder: print("Selected:", folder))

SaveFile.show(default_filename="untitled.txt", callback=lambda path: print("Saved to:", path))

messagebox.show(
    "Save changes before closing?",
    title="SuperNanno",
    buttons=messagebox.buttons.YES_NO_CANCEL,
    type=messagebox.type.WARNING,
    callback=lambda choice: print("User picked:", choice),
)
```

Works **standalone** in any Textual app, and as an official SuperNanno
extension - no required setup beyond calling `.show(...)` from inside an
event handler.

## Install

```bash
pip install nannokit.dialogs

# or, with the SuperNanno core app pulled in too:
pip install "nannokit.dialogs[supernanno]"
```

## Why this feels different from a typical Textual dialog

| .NET | nannokit.dialogs |
|---|---|
| `new OpenFileDialog().ShowDialog()` | `OpenFile.show(callback=...)` |
| `new FolderBrowserDialog().ShowDialog()` | `OpenFolder.show(callback=...)` |
| `new SaveFileDialog().ShowDialog()` | `SaveFile.show(callback=...)` |
| `MessageBox.Show(text, caption, buttons, icon)` | `messagebox.show(text, title=..., buttons=..., type=...)` |
| `OpenFileDialog.CheckFileExists` | `must_exist=` |
| `OpenFileDialog.Multiselect` | `multiselect=` |
| `OpenFileDialog.Filter` | `filters=` |
| `SaveFileDialog.OverwritePrompt` | `confirm_overwrite=` |

Textual is async and has no blocking `ShowDialog()` return value, so every
`.show(...)` takes a `callback` instead - fire-and-forget, with the result
delivered when the user is done.

## How app resolution works (and why you don't have to think about it)

Every dialog needs to know *which* running Textual `App` to attach itself
to. `DialogManager` resolves that automatically:

1. If you called `DialogManager.attach(self)` once (e.g. in `App.on_mount`),
   that App is always used.
2. Otherwise, it falls back to Textual's own `active_app` context variable,
   which is set for the duration of any event handler/action/binding/worker
   belonging to a running App. In practice, this means calling
   `OpenFile.show(...)` from a key binding or a button handler **just
   works**, with zero setup - the same feeling as calling
   `new OpenFileDialog().ShowDialog()` from any UI-thread callback in C#.

```python
from textual.app import App
from nannokit.dialogs.core import DialogManager

class MyApp(App):
    def on_mount(self) -> None:
        # Recommended, and required only for calls made from outside
        # a running event handler (background threads, startup scripts).
        DialogManager.attach(self)
```

## Package layout

```
src/supernanno/dialogs/
├── core/                 # Shared plumbing - no UI of its own
│   ├── manager.py        # DialogManager: resolves the active App
│   ├── base.py           # DialogScreenBase: shared ModalScreen plumbing
│   ├── config.py         # Reserved for future shared config
│   └── theme.py          # Reserved for future shared palette
├── messagebox/
│   ├── api.py            # MessageBoxAPI -> the `messagebox` singleton
│   ├── dialog.py         # MessageDialog (ModalScreen)
│   ├── buttons.py        # Buttons presets (OK, YES_NO, ...)
│   └── types.py          # MessageBoxIcon (INFO/WARNING/ERROR/SUCCESS)
├── filedialogs/
│   ├── base.py           # FileSystemDialogBase: shared tree+nav+validation
│   ├── tree.py           # FilterableDirectoryTree (hidden files, globs)
│   ├── open_file.py      # OpenFile
│   ├── open_folder.py    # OpenFolder
│   └── save_file.py      # SaveFile (+ overwrite confirmation)
└── styles/
    ├── messagebox.tcss
    └── filedialog.tcss
```

`supernanno` itself has **no** `__init__.py` - it's a PEP 420 namespace
package on purpose, so future sibling extensions (`supernanno.git`,
`supernanno.linting`, ...) can each ship independently under the same
top-level namespace without conflicting with this one.

### Adding a new dialog

Most new filesystem-flavoured dialogs need **no new screen at all** - just
a thin `show(...)` classmethod configuring `FileSystemDialogBase`, the same
way `OpenFile` and `OpenFolder` do. A dialog that needs genuinely different
*behaviour* (not just labels) overrides one hook - see `SaveFile`, which
overrides `_confirm()` to add an overwrite prompt (itself built on top of
`messagebox`, demonstrating that dialogs can compose with each other).

A dialog with a different shape entirely (e.g. a future `ColorPicker`)
subclasses `DialogScreenBase[ResultT]` directly and gets Escape-to-cancel
and App-resolution for free.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Tests use Textual's own `Pilot`/`run_test()` harness - no real terminal
required.

## License

BSD 3-Clause - see [LICENSE](LICENSE).
