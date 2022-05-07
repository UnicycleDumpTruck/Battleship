from enum import Enum, auto
from typing import Tuple
from loguru import logger
import fleet
import os


from blessed import Terminal

from rich.text import Text
from rich import styled, box
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.console import Console
from rich.theme import Theme
from rich.align import Align

theme_dict = {
    "w": "dim cyan",
    "M": "bold bright_white",
    "H": "bold bright_red",
    "G": "bold blue",
    "headings": "green",
}
custom_theme = Theme(theme_dict)
console = Console(theme=custom_theme)

title_text = Align(align="center", style="red bold", renderable="\nFightBoat")

# G_PAD_HEIGHT = 11
# G_PAD_WIDTH = 40


class Areas(Enum):
    TR = auto()  # Title Row
    AG = auto()  # Player a guess grid display pad
    AS = auto()  # Player a ships grid display pad
    AT = auto()  # Player a status text/instructions
    AF = auto()  # Player a feedback on last move
    BG = auto()  # Player b guesses
    BS = auto()  # Player b ships
    BT = auto()  # Player b text
    BF = auto()  # Player b feedback


class RichView:
    def __init__(self, term: Terminal):
        self.term = term

        # self.scrn = scrn
        self.full_layout = Layout()
        self.full_layout.split_column(
            Layout(name="title_row", size=2),
            Layout(name="lower_row"),
        )
        self.full_layout["lower_row"].split_row(
            Layout(name="player_a"),
            Layout(name="player_b"),
        )

        self.full_layout["lower_row"]["player_a"].split_column(
            Layout(name="guesses_row", size=13),
            Layout(name="ships_row", size=13),
            Layout(name="feedback_row", size=4),
            Layout(name="prompt_row", size=4),
        )
        self.full_layout["lower_row"]["player_b"].split_column(
            Layout(name="guesses_row", size=13),
            Layout(name="ships_row", size=13),
            Layout(name="feedback_row", size=4),
            Layout(name="prompt_row", size=4),
        )

        self.areas = {
            Areas.TR: self.full_layout["title_row"],
            Areas.AG: self.full_layout["lower_row"]["player_a"]["guesses_row"],
            Areas.AS: self.full_layout["lower_row"]["player_a"]["ships_row"],
            Areas.AT: self.full_layout["lower_row"]["player_a"]["prompt_row"],
            Areas.AF: self.full_layout["lower_row"]["player_a"]["feedback_row"],
            Areas.BG: self.full_layout["lower_row"]["player_b"]["guesses_row"],
            Areas.BS: self.full_layout["lower_row"]["player_b"]["ships_row"],
            Areas.BT: self.full_layout["lower_row"]["player_b"]["prompt_row"],
            Areas.BF: self.full_layout["lower_row"]["player_b"]["feedback_row"],
        }

        for area in self.areas.values():
            area.update("")

        self.update_area(Areas.TR, title_text)

        self.clear_and_print()

    def clear_and_print(self):
        os.system("clear")
        console.print(self.full_layout)

    def update_area(self, area, text):
        self.areas[area].update(styled.Styled(text, style="red"))
        self.clear_and_print()

    def aim_column(self, area, column):
        pass

    def aim_row(self, area, row):
        pass

    def get_direction(self) -> str:
        with self.term.cbreak():
            val = self.term.getch()  # faster refresh than term.inkey
        return val

    def display_grid(self, grid: str, ar: Areas):
        # self.scrn.addstr(grid)
        # self.scrn.refresh()
        styled_grid = Text()
        for char in grid:
            if char in fleet.ship_capitals:
                styled_grid.append(char, style=theme_dict["G"])
            elif char in fleet.headings:
                styled_grid.append(char, style=theme_dict["headings"])
            elif char.isdigit():
                styled_grid.append(char, style=theme_dict["headings"])
            elif char in {" ", "\n"}:
                styled_grid.append(char, None)
            else:
                styled_grid.append(char, style=theme_dict[char])
            if char != "\n":
                styled_grid.append(" ", None)
        self.areas[ar].update(styled_grid)
        self.clear_and_print()

    def display_text(self, text: str, ar: Areas):
        self.areas[ar].update(text)
        self.clear_and_print()

    # def display_feeback(self, text: str, ar: Areas):
    #     self.areas[ar].update(text)
    #     self.clear_and_print()

    def get_fire_coords(self, flt: fleet.Fleet) -> fleet.Point:
        while True:
            while True:
                self.display_text("Firing row? ", Areas.BT)
                row_guess = self.get_direction()
                self.display_text("", Areas.BT)
                if row_guess in fleet.headings:
                    row_guess = ord(row_guess) - 97
                    break

            while True:
                self.display_text("Firing column? ", Areas.BT)
                col_guess = self.get_direction()
                if col_guess.isdigit():
                    col_guess_num = int(col_guess)
                    self.display_text(f"", Areas.BT)
                    if 0 <= col_guess_num <= fleet.GRID_SIZE:
                        col_guess_num -= 1
                        break

            coords = fleet.Point(y=row_guess, x=col_guess_num)
            if flt.at_point(coords) not in {"H", "M"}:
                break
        return coords
