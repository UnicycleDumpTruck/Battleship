import abc
import curses
from enum import Enum, auto
from typing import Tuple
from loguru import logger
import fleet

G_PAD_HEIGHT = 14
G_PAD_WIDTH = 40


class Areas(Enum):
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

    @abc.abstractmethod
    def set_stage(self, stage):  # Whose turn, etc
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


class CursesView(View):
    def __init__(self, scrn: curses.window):
        self.scrn = scrn  # curses.newwin(600, 600, 50, 50)
        logger.debug(f"L:{curses.LINES} C:{curses.COLS}")
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
