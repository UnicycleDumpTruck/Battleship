from enum import Enum, auto
from typing import List
from loguru import logger
import fleet
import os

import board
from adafruit_ht16k33.matrix import Matrix8x8x2

from blessed import Terminal

from rich.traceback import install

install(show_locals=True)

i2c = board.I2C()

guess_matrix = Matrix8x8x2(i2c, 0x70)
fleet_matrix = Matrix8x8x2(i2c, 0x71)

# Available LED colors
# matrix.LED_OFF
# matrix.LED_GREEN
# matrix.LED_YELLOW
# matrix.LED_RED

# Guess Grid
# Hit: red
# Miss: yellow
# Sunk: green
# Else: off
# Highlight: dim yellow

# Fleet Grid
# Hit: red
# Miss: yellow
# Ship: green
# Highlight: dim yellow


theme_dict = {
    "w": guess_matrix.LED_OFF,
    "M": guess_matrix.LED_YELLOW,
    "H": guess_matrix.LED_RED,
    "G": guess_matrix.LED_GREEN,
    "X": guess_matrix.LED_GREEN,
}
for cap in fleet.ship_capitals:
    theme_dict[cap] = guess_matrix.LED_GREEN
    theme_dict[cap.lower()] = guess_matrix.LED_GREEN


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


class Matrices(Enum):
    AG = auto()  # Player A guesses
    AS = auto()  # Player A ships
    BG = auto()  # Player B guesses
    BS = auto()  # Player B ships


class MatrixView:
    def __init__(self, term: Terminal):
        self.term = term

        #        self.areas = {
        #            Areas.TR: "title_row",
        #            Areas.AG: "player_a guesses",
        #            Areas.AS: "player_a ships_row",
        #            Areas.AT: "player_a prompt_row",
        #            Areas.AF: "player_a feedback_row",
        #            Areas.BG: "player_b guesses_row",
        #            Areas.BS: "player_b ships_row",
        #            Areas.BT: "player_b prompt_row",
        #            Areas.BF: "player_b feedback_row",
        #        }

        self.clear_and_print()

    def clear_and_print(self):
        # os.system("clear")console.
        # print(self.full_layout)
        logger.warning("clear_and_print called!")

    def update_area(self, area, text):
        logger.info(f"Area {area}: {text}")
        self.clear_and_print()

    def get_direction(self) -> str:
        with self.term.cbreak():
            # val = self.term.getch()  # faster refresh than term.inkey
            val = self.term.inkey()
        return val

    def display_grid(self, grid: List[fleet.Square], show_ships: bool, area: Areas):
        # styled_grid = ""
        logger.debug(f"Displaying grid {area}")
        if area == Areas.BG:
            matrix = guess_matrix
        elif area == Areas.BS:
            matrix = fleet_matrix
        else:
            logger.debug(
                f"no matrix set for {area} {area == Areas.BG or area == Areas.BS}"
            )
            return
        for row_num, row in enumerate(grid):
            for col_num, square in enumerate(row):
                label = square.get_label()
                if highlight := square.get_highlight():
                    matrix[row_num, col_num] = matrix.LED_YELLOW
                else:
                    matrix[row_num, col_num] = theme_dict[label]
        #         if not show_ships:
        #             if label in fleet.ship_capitals:
        #                 label = "w"
        #         highlight = square.get_highlight()
        #         theme = theme_dict.get(label, '')
        #         style = f"{theme}{' on ' if highlight else ''}{highlight}"
        #         styled_grid.append(label, style=style)
        #         if label != "\n":
        #             styled_grid.append(" ", None)
        #     styled_grid.append("\n", None)

        # self.areas[area].update(styled_grid)
        # self.clear_and_print()

    def display_text(self, text: str, ar: Areas):
        logger.info(text)
        # self.clear_and_print()

    def highlight_target(self, flt: fleet.Fleet, point: fleet.Point, area: Areas):
        flt.highlight_reticle(point)

    def not_highlight_target(self, flt: fleet.Fleet, point: fleet.Point, area: Areas):
        flt.remove_all_highlights()
        flt.highlight_row(point.y, "yellow")
        flt.highlight_col(point.x, "yellow")
        flt.highlight_point(point, "red reverse blink")
        self.display_grid(
            flt.grid.ships_grid(False, False), show_ships=False, area=area
        )

    def get_fire_coords(self, flt: fleet.Fleet) -> fleet.Point:
        # TODO: don't allow firing on previously fired-on points
        target_x = 3
        target_y = 3
        # self.display_text("Arrows to choose, Enter to fire.", Areas.BT)
        self.highlight_target(
            flt=flt, point=fleet.Point(y=target_y, x=target_x), area=Areas.BG
        )
        while True:
            key = self.get_direction()
            if key.name == "KEY_ENTER":
                coords = fleet.Point(y=target_y, x=target_x)
                break
            elif key.name == "KEY_UP":
                if target_y > 0:
                    target_y -= 1
                    self.highlight_target(
                        flt=flt,
                        point=fleet.Point(y=target_y, x=target_x),
                        area=Areas.BG,
                    )
            elif key.name == "KEY_DOWN":
                if target_y < fleet.GRID_SIZE - 1:
                    target_y += 1
                    self.highlight_target(
                        flt=flt,
                        point=fleet.Point(y=target_y, x=target_x),
                        area=Areas.BG,
                    )
            elif key.name == "KEY_LEFT":
                if target_x > 0:
                    target_x -= 1
                    self.highlight_target(
                        flt=flt,
                        point=fleet.Point(y=target_y, x=target_x),
                        area=Areas.BG,
                    )
            elif key.name == "KEY_RIGHT":
                if target_x < fleet.GRID_SIZE - 1:
                    target_x += 1
                    self.highlight_target(
                        flt=flt,
                        point=fleet.Point(y=target_y, x=target_x),
                        area=Areas.BG,
                    )
            else:
                continue

        # self.display_text("", Areas.BT)
        flt.remove_all_highlights()
        self.display_grid(
            flt.grid.ships_grid(False, False), show_ships=False, area=Areas.BG
        )
        return coords

    def show_game_over(self, winner):
        logger.info(f"Game over! {winner} has won the game!")
