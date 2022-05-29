from enum import Enum, auto
from typing import Tuple, List
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
from rich.traceback import install

install(show_locals=True)


theme_dict = {
    "w": "dim cyan",
    "M": "bold bright_white",
    "H": "bold bright_red",
    "G": "bold blue",
    "X": "red",
    " ": "none",
    "\n": "none",
}
for cap in fleet.ship_capitals:
    theme_dict[cap] = "bold blue"
    theme_dict[cap.lower()] = "red"
for head in fleet.headings:
    theme_dict[head] = "green"


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
        # Hide computer's grids and feedback
        self.full_layout["lower_row"]["player_a"].visible = False
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
        # os.system("clear")
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
            # val = self.term.getch()  # faster refresh than term.inkey
            val = self.term.inkey()
        return val

    def display_grid(self, grid: List[fleet.Square], show_ships: bool, area: Areas):
        styled_grid = Text()
        for row in grid:
            for square in row:
                label = square.get_label()
                if not show_ships:
                    if label in fleet.ship_capitals:
                        label = "w"
                highlight = square.get_highlight()
                theme = theme_dict.get(label, '')
                style = f"{theme}{' on ' if highlight else ''}{highlight}"
                styled_grid.append(label, style=style)
                if label != "\n":
                    styled_grid.append(" ", None)
            styled_grid.append("\n", None)

        self.areas[area].update(styled_grid)
        self.clear_and_print()
        
    def display_text(self, text: str, ar: Areas):
        self.areas[ar].update(text)
        self.clear_and_print()

    def highlight_target(self, flt: fleet.Fleet, point: fleet.Point, area: Areas):
        flt.remove_all_highlights()
        flt.highlight_row(point.y, "yellow")
        flt.highlight_col(point.x, "yellow")
        flt.highlight_point(point, "red reverse blink")
        self.display_grid(flt.grid.ships_grid(False, False), show_ships=False, area=area)


    def get_fire_coords(self, flt: fleet.Fleet) -> fleet.Point:
        # TODO: don't allow firing on previously fired-on points
        target_x = 3
        target_y = 3
        self.display_text("Arrows to choose, Enter to fire.", Areas.BT)
        self.highlight_target(flt=flt, point=fleet.Point(y=target_y, x=target_x), area=Areas.BG)
        while True:
            key = self.get_direction()
            if key.name == "KEY_ENTER":
                    coords = fleet.Point(y=target_y, x=target_x)
                    break
            elif key.name == "KEY_UP":
                if target_y > 0:
                    target_y -= 1
                    self.highlight_target(flt=flt, point=fleet.Point(y=target_y, x=target_x), area=Areas.BG)
            elif key.name == "KEY_DOWN":
                if target_y < fleet.GRID_SIZE - 1:
                    target_y += 1
                    self.highlight_target(flt=flt, point=fleet.Point(y=target_y, x=target_x), area=Areas.BG)
            elif key.name == "KEY_LEFT":
                if target_x > 0:
                    target_x -= 1
                    self.highlight_target(flt=flt, point=fleet.Point(y=target_y, x=target_x), area=Areas.BG)
            elif key.name == "KEY_RIGHT":
                if target_x < fleet.GRID_SIZE - 1:
                    target_x += 1
                    self.highlight_target(flt=flt, point=fleet.Point(y=target_y, x=target_x), area=Areas.BG)
            else:
                continue

        self.display_text("", Areas.BT)
        flt.remove_all_highlights()
        self.display_grid(flt.grid.ships_grid(False, False), show_ships=False, area=Areas.BG)
        return coords

    def show_game_over(self, winner):
        game_over_title = Align(
            align="center",
            style="red bold",
            renderable="""\
 ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗ 
██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗
██║  ███╗███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
                                                                          """,
        )
        winner_text = Align(
            align="center", style="red bold", renderable=f"{winner} has won the game!"
        )
        self.game_over_layout = Layout()
        self.game_over_layout.split_column(
            Layout(name="upper_third"),
            Layout(name="middle_third"),
            Layout(name="lower_third"),
        )
        self.game_over_layout["upper_third"].update("")
        self.game_over_layout["middle_third"].update(game_over_title)
        self.game_over_layout["lower_third"].update(winner_text)
        os.system("clear")
        console.print(self.game_over_layout)
