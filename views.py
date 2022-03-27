import abc
import curses
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
# console.print("This is information", style="info")
# console.print("[warning]The pod bay doors are locked[/warning]")
# console.print("Something terrible happened!", style="danger")

title_text = Align(align="center", style="red bold", renderable="\nFightBoat")

G_PAD_HEIGHT = 11
G_PAD_WIDTH = 40


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


class View(abc.ABC):
    @abc.abstractmethod
    def __init__(self, controller, model):
        ...

    @abc.abstractmethod
    def display_grid(self, grid: str, area: Areas):
        ...

    @abc.abstractmethod
    def display_text(self, text: str, area: Areas):
        ...


class CursesArea:
    def __init__(self, origin: Tuple, height: int, name: str):
        self.origin = origin
        self.pad = curses.newpad(G_PAD_HEIGHT, G_PAD_WIDTH)
        self.name = name
        self.height = height

    def display_grid(self, grid: str):
        self.pad.clear()
        self.pad.addstr(self.name)
        lines = list(enumerate(grid.split("\n"), start=1))
        for line_num, line_text in lines:
            self.pad.addstr(line_num, 0, line_text)
        self.pad.refresh(
            0,
            0,
            self.origin[0],
            self.origin[1],
            self.origin[0] + self.height,  # GRID_PAD_SIZE,
            self.origin[1] + G_PAD_WIDTH,  # GRID_PAD_SIZE,
        )

    def display_text(self, text: str):
        self.pad.clear()
        self.pad.addstr(self.name)
        lines = list(enumerate(text.split("\n"), start=1))
        for line_num, line_text in lines:
            self.pad.addstr(line_num, 0, line_text)
        self.pad.refresh(
            0,
            0,
            self.origin[0],
            self.origin[1],
            self.origin[0] + self.height,  # GRID_PAD_SIZE,
            self.origin[1] + G_PAD_WIDTH,  # GRID_PAD_SIZE,
        )


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
        self.areas[ar].update(styled_grid)
        self.clear_and_print()

    def display_text(self, text: str, ar: Areas):
        self.areas[ar].update(text)
        self.clear_and_print()

    def display_feeback(self, text: str, ar: Areas):
        self.areas[ar].update(text)
        self.clear_and_print()

    def get_fire_coords(self) -> fleet.Point:
        while True:
            self.display_text(f"Firing row? ", Areas.BT)
            row_guess = self.get_direction()
            self.display_text(f"", Areas.BT)
            if row_guess in fleet.headings:
                row_guess = ord(row_guess) - 97
                break

        while True:
            self.display_text(f"Firing column? ", Areas.BT)
            col_guess = int(self.get_direction())
            self.display_text(f"", Areas.BT)
            if 0 <= col_guess and col_guess <= fleet.GRID_SIZE:
                col_guess = col_guess - 1
                break

        return fleet.Point(y=row_guess, x=col_guess)


class CursesView(View):
    def __init__(self, scrn: curses.window):
        self.scrn = scrn  # curses.newwin(600, 600, 50, 50)
        # 6 grids total
        # TODO: rename to player a and b, or passed values
        a_guess = CursesArea((0, 0), G_PAD_HEIGHT, "Computer Guesses")
        a_ships = CursesArea((G_PAD_HEIGHT, 0), G_PAD_HEIGHT, "Computer Ships")
        b_guess = CursesArea((0, G_PAD_WIDTH), G_PAD_HEIGHT, "Human Guesses")
        b_ships = CursesArea((G_PAD_HEIGHT, G_PAD_WIDTH), G_PAD_HEIGHT, "Human Ships")

        a_text = CursesArea(((G_PAD_HEIGHT * 2) + 3, 0), 2, "Computer Text")
        b_text = CursesArea(((G_PAD_HEIGHT * 2) + 3, G_PAD_WIDTH), 2, "Human Text")
        a_feedback = CursesArea((G_PAD_HEIGHT * 2, 0), 3, "Computer Feedback")
        b_feedback = CursesArea((G_PAD_HEIGHT * 2, G_PAD_WIDTH), 3, "Human Feedback")

        self.areas = {
            Areas.AG: a_guess,
            Areas.AS: a_ships,
            Areas.AT: a_text,
            Areas.AF: a_feedback,
            Areas.BG: b_guess,
            Areas.BS: b_ships,
            Areas.BT: b_text,
            Areas.BF: b_feedback,
        }

        for a in self.areas.values():
            a.display_text(a.name)

    def get_direction(self) -> str:
        return self.scrn.getkey()

    def display_grid(self, grid: str, ar: Areas):
        # self.scrn.addstr(grid)
        # self.scrn.refresh()
        self.areas[ar].display_grid(grid)

    def display_text(self, text: str, ar: Areas):
        self.areas[ar].display_text(text)

    def display_feeback(self, text: str, ar: Areas):
        self.areas[ar].display_text(text)

    def set_stage(self):
        raise NotImplementedError

    def get_fire_coords(self) -> fleet.Point:
        while True:
            self.display_text(f"Firing row? ", Areas.BT)
            row_guess = self.get_direction()
            self.display_text(f"", Areas.BT)
            if row_guess in fleet.headings:
                row_guess = ord(row_guess) - 97
                break

        while True:
            self.display_text(f"Firing column? ", Areas.BT)
            col_guess = int(self.get_direction())
            self.display_text(f"", Areas.BT)
            if 0 <= col_guess and col_guess <= fleet.GRID_SIZE:
                col_guess = col_guess - 1
                break

        return fleet.Point(y=row_guess, x=col_guess)
