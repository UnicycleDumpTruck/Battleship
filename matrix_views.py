from enum import Enum, auto
from typing import List
import os

import board
from adafruit_ht16k33.matrix import Matrix8x8x2
from loguru import logger
from blessed import Terminal
from rich.traceback import install

import fleet
from views import Areas

install(show_locals=True)

i2c = board.I2C()


class MatrixView:
    def __init__(self, term: Terminal):
        self.term = term
        self.clear_and_print()
        self.guess_matrix = Matrix8x8x2(i2c, 0x70)
        self.fleet_matrix = Matrix8x8x2(i2c, 0x71)

        self.theme_dict = {
            "w": self.guess_matrix.LED_OFF,  # Water
            "M": self.guess_matrix.LED_YELLOW,  # Miss
            "H": self.guess_matrix.LED_RED,  # Hit
            "G": self.guess_matrix.LED_GREEN,  # Fleet ship or sunk ship
            # "X": guess_matrix.LED_GREEN,    # Sunk ship, not used
        }
        for cap in fleet.ship_capitals:
            self.theme_dict[cap] = self.guess_matrix.LED_GREEN
            self.theme_dict[cap.lower()] = self.guess_matrix.LED_GREEN

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

    def display_grid(
        self, grid: List[List[fleet.Square]], show_ships: bool, area: Areas
    ):
        if area == Areas.BG:
            matrix = self.guess_matrix
        elif area == Areas.BS:
            matrix = self.fleet_matrix
        else:
            return
        for row_num, row in enumerate(grid):
            for col_num, square in enumerate(row):
                label = square.get_label()
                if highlight := square.get_highlight():
                    matrix[row_num, col_num] = matrix.LED_YELLOW
                else:
                    if not show_ships and label in fleet.ship_capitals:
                        label = "w"
                    matrix[row_num, col_num] = self.theme_dict[label]

    def display_text(self, text: str, ar: Areas):
        logger.info(text)

    def highlight_target(self, flt: fleet.Fleet, point: fleet.Point, area: Areas):
        flt.highlight_reticle(point)
        self.display_grid(
            flt.grid.ships_grid(False, False), show_ships=False, area=area
        )

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
        logger.info("Arrows to choose, Enter to fire.")
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

        flt.remove_all_highlights()
        self.display_grid(
            flt.grid.ships_grid(False, False), show_ships=False, area=Areas.BG
        )
        return coords

    def show_game_over(self, winner):
        logger.info(f"Game over! {winner} has won the game!")
