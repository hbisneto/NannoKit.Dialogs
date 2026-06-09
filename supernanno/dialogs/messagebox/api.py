from textual.app import App
from dialogs.messagebox.dialog import MessageDialog

class MessageBoxApp(App):

    CSS_PATH = [
        "../styles/default.tcss"
    ]

    def __init__(
        self,
        message,
        title,
        buttons,
        dialog_type,
        callback=None
    ):
        super().__init__()

        self.message = message
        self.title = title
        self.buttons = buttons
        self.dialog_type = dialog_type
        self.callback = callback

    def on_mount(self):

        self.push_screen(

            MessageDialog(
                message=self.message,
                title=self.title,
                buttons=self.buttons,
                dialog_type=self.dialog_type,
                callback=self.callback
            )
        )


class MessageBoxAPI:

    from dialogs.messagebox.buttons import Buttons
    from dialogs.messagebox.types import Types

    buttons = Buttons
    type = Types

    @staticmethod
    def show(
        message,
        title="Message",
        buttons=None,
        type="info",
        callback=None
    ):

        if buttons is None:
            buttons = ["OK"]

        app = MessageBoxApp(
            message=message,
            title=title,
            buttons=buttons,
            dialog_type=type,
            callback=callback
        )

        app.run()