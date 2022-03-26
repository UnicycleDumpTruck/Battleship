import abc
import curses
from enum import Enum
from typing import Tuple
from loguru import logger
import fleet

GRID_PAD_HEIGHT = 14
GRID_PAD_WIDTH = 30


class Areas(Enum):
    AG = 0  # Player a guess grid display pad
    AS = 1  # Player a ships grid display pad
    AT = 2  # Player a status text/instructions
    BG = 3  # Player b guesses
    BS = 4  # Player b ships
    BT = 5  # Player b text


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
    def __init__(self, scrn: curses.window, origin: Tuple, name: str):
        self.origin = origin
        self.pad = curses.newpad(GRID_PAD_HEIGHT, GRID_PAD_WIDTH)
        self.name = name

    def display_text(self, text: str):
        l = curses.LINES
        c = curses.COLS
        # pw = self.pad.get_wch()
        self.pad.clear()
        lines = list(enumerate(text.split("\n")))
        len_lines = len(lines)
        for line_num, line_text in lines:
            self.pad.addstr(line_num, 0, line_text)
        self.pad.refresh(
            0,
            0,
            self.origin[0],
            self.origin[1],
            self.origin[0] + GRID_PAD_HEIGHT,  # GRID_PAD_SIZE,
            self.origin[1] + GRID_PAD_WIDTH,  # GRID_PAD_SIZE,
        )

    # def display_text(self, text: str)::
    #     self.pad.clear()
    #     self.pad.addstr(text)
    #     self.pad.refresh(
    #         0,
    #         0,
    #         self.
    #     )


class CursesView(View):
    def __init__(self, scrn: curses.window):
        self.scrn = scrn  # curses.newwin(600, 600, 50, 50)
        logger.debug(f"L:{curses.LINES} C:{curses.COLS}")
        # 6 grids total

        a_guess = CursesArea(self.scrn, (0, 0), "Computer Guesses")
        a_ships = CursesArea(self.scrn, (GRID_PAD_HEIGHT, 0), "Computer Ships")
        b_guess = CursesArea(self.scrn, (0, GRID_PAD_WIDTH), "Human Guesses")
        b_ships = CursesArea(
            self.scrn, (GRID_PAD_HEIGHT, GRID_PAD_WIDTH), "Human Ships"
        )
        a_text = CursesArea(self.scrn, (GRID_PAD_HEIGHT * 2, 0), "Computer Text")
        b_text = CursesArea(
            self.scrn, (GRID_PAD_HEIGHT * 2, GRID_PAD_WIDTH), "Human Text"
        )

        self.areas = {
            Areas.AG: a_guess,
            Areas.AS: a_ships,
            Areas.AT: a_text,
            Areas.BG: b_guess,
            Areas.BS: b_ships,
            Areas.BT: b_text,
        }

        for a in self.areas.values():
            a.display_text(a.name)

    def get_direction(self) -> str:
        return self.scrn.getkey()

    def display_grid(self, grid: str, ar: Areas):
        # self.scrn.addstr(grid)
        # self.scrn.refresh()
        self.areas[ar].display_text(grid)

    def display_text(self, text: str, ar: Areas):
        self.areas[ar].display_text(text)

    def set_stage(self):
        raise NotImplementedError
