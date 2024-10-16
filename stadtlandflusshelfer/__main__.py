import random
import string

import pyfiglet  # type: ignore[import-untyped]
from textual.app import App, ComposeResult
from textual.geometry import Size
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static


class SelectedLettersWidget(Static):
    all_letters = string.ascii_uppercase

    def set_selected_letters(self, selected_letters: list[str] | None = None) -> None:
        renderable_result = " "
        if selected_letters is None:
            selected_letters = []

        for letter in self.all_letters:
            if letter in selected_letters:
                renderable_result += f"[red]{letter}[/red]"
            else:
                renderable_result += letter

        renderable_result += " "
        self.update(renderable_result)

    def on_mount(self) -> None:
        self.set_selected_letters()


class SingleLetterWidget(Static):
    WIDTH = 28
    FONT = "colossal"
    FONT = "roman"
    figlet = pyfiglet.Figlet(font=FONT, justify="center", width=WIDTH)

    def set_selected_letter(self, selected_letter: str = "") -> None:
        fancy_string = "\n" + self.figlet.renderText(selected_letter)
        self.log(f"@@@@ {selected_letter}:{len(fancy_string.splitlines())}")
        self.update(fancy_string)

    def on_mount(self) -> None:
        self.set_selected_letter()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Force content width size."""
        return self.WIDTH


class MyApp(App):
    """
    UI Elements:
    - Currently selected letter (figlet) - none at the start
    - Big Green Button to randomly select a new letter
    - Little element showing the previous selected letters
    - Binding to reset everything

    """

    TITLE = "StadtLandFluss Helfer"

    INITIAL_LETTER = "-"

    picked_letter = reactive(INITIAL_LETTER)
    unpicked_letters = reactive(list(string.ascii_uppercase))

    BINDINGS = [  # noqa: RUF012§
        ("r", "request_reset_letters", "Reset Letters"),
    ]

    CSS = """
    Screen {
         layout: vertical;
         align: center middle;
    }

    #select_next_letter_button {
        width: 30;
        padding: 1 2;
        margin: 1 0;
        text-align: center;
        border: heavy $panel;
    }

    SingleLetterWidget {
        border: double $accent;
        height: auto;
        width: auto;
        align: center middle;
    }

    SelectedLettersWidget {
        border: double $accent;
        height: auto;
        width: auto;
        align: center middle;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Button.success("Select next letter", id="select_next_letter_button")
        yield SingleLetterWidget(id="picked_letter_widget")
        yield SelectedLettersWidget(id="unpicked_letters_widget")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#picked_letter_widget").border_title = "Current Letter"
        self.query_one("#unpicked_letters_widget").border_title = "Unpicked Letters"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.log(">>> on_button_pressed <<<")
        button_id = event.button.id
        if button_id == "select_next_letter_button":
            self.picked_letter = random.choice(self.unpicked_letters)  # noqa: S311
            self.unpicked_letters.remove(self.picked_letter)
            self.mutate_reactive(MyApp.unpicked_letters)

    def watch_picked_letter(self) -> None:
        self.query_one("#picked_letter_widget", SingleLetterWidget).set_selected_letter(self.picked_letter)

    def watch_unpicked_letters(self) -> None:
        self.query_one("#unpicked_letters_widget", SelectedLettersWidget).set_selected_letters(self.unpicked_letters)
        select_next_letter_button = self.query_one("#select_next_letter_button")

        done_with_all_letters = len(self.unpicked_letters) == 0
        select_next_letter_button.disabled = done_with_all_letters

        if done_with_all_letters:
            select_next_letter_button.focus()
            self.notify("Done with all letters! Please reset...", timeout=10)

    def action_request_reset_letters(self) -> None:
        self.picked_letter = self.INITIAL_LETTER
        self.unpicked_letters = list(string.ascii_uppercase)
        self.mutate_reactive(MyApp.unpicked_letters)


def main() -> None:
    app = MyApp()
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
