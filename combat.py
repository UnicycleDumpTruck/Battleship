from abc import ABC
from random import randint, choice
from curses import wrapper
from time import sleep
from rich.traceback import install
from loguru import logger

from fleet import Ship, Fleet, headings, GRID_SIZE, ship_sizes, Direction, Point
from views import CursesView, Areas

install(show_locals=True)


class Combat(ABC):
    """Abstract base class for combat controllers."""

    def __init__(self):
        pass


class HVCCombat(Combat):
    """Human vs computer combat controller."""

    def __init__(self, view):
        self.view = view
        self.computer_fleet = Fleet("Computer Fleet")
        self.computer_fleet.deploy_computer_fleet()
        self.human_fleet = Fleet("Human Fleet")

    def input_ships(self):
        for ship_type in ship_sizes.keys():
            next_direction = Direction.NONE
            ship = Ship(
                ship_type=ship_type,
                ship_size=ship_sizes[ship_type],
                ship_start=Point(x=0, y=0),
                ship_horiz=choice((True, False)),
                # ship_temp=True,
            )

            while True:
                if not self.human_fleet.valid_anchor(ship):
                    next_direction = choice(list(Direction))
                ship = self.human_fleet.next_valid_ship(ship, next_direction)
                if self.human_fleet.valid_anchor(ship):
                    self.human_fleet.add_tentative_ship(ship)
                    cmds = {
                        "w": Direction.UP,
                        "s": Direction.DOWN,
                        "a": Direction.LEFT,
                        "d": Direction.RIGHT,
                        "f": Direction.FLIP,
                    }
                    self.view.display_grid(self.human_fleet.ships_grid(True), Areas.BS)
                    self.view.display_text(f"{ship.ship_type} Ewasdf", Areas.BT)
                    chr_in = self.view.get_direction()
                    self.view.display_text("", Areas.BS)
                    # qu = f"Enter to anchor {ship.ship_type} wasd to move: "
                    # chr_in = input(qu).lower()
                    if chr_in == "\n":
                        self.human_fleet.remove_tentative_ship(ship)
                        self.human_fleet.add_ship(ship)
                        self.view.display_grid(
                            self.human_fleet.ships_grid(True), Areas.BS
                        )
                        break
                    else:
                        self.human_fleet.remove_tentative_ship(ship)
                        next_direction = cmds.get(chr_in, Direction.NONE)
                        self.view.display_grid(
                            self.human_fleet.ships_grid(True), Areas.BS
                        )
                        continue
                # else:
                #     ship = self.human_fleet.next_valid_ship(ship, next_direction)

    def run(self):
        logger.debug("HVCCombat running.")
        self.view.display_grid(self.computer_fleet.ships_grid(True), Areas.AS)
        self.input_ships()
        # TODO: Make this into a turn function, check if game won each turn
        while True:
            while True:
                self.view.display_text(f"Firing row? ", Areas.BT)
                row_guess = self.view.get_direction()
                self.view.display_text(f"", Areas.BT)
                if row_guess in headings:
                    row_guess = ord(row_guess) - 97
                    break

            while True:
                self.view.display_text(f"Firing column? ", Areas.BT)
                col_guess = int(self.view.get_direction())
                self.view.display_text(f"", Areas.BT)
                if 0 <= col_guess and col_guess <= GRID_SIZE:
                    col_guess = col_guess - 1
                    break

            results = self.computer_fleet.take_fire(Point(y=row_guess, x=col_guess))
            if results[2]:
                feedback = f"You sunk my {results[1]} and WON THE GAME!"
                break
            elif results[0] and results[1]:
                feedback = f"You sunk my {results[1]}!"
            elif results[0]:
                feedback = "Hit!"
            else:
                feedback = "Miss!"
            self.view.display_text(feedback, Areas.BT)
            self.view.display_grid(self.computer_fleet.ships_grid(True), Areas.AS)
            self.view.display_grid(self.computer_fleet.ships_grid(False), Areas.BG)
            results = self.human_fleet.take_fire(
                Point(y=randint(0, GRID_SIZE - 1), x=randint(0, GRID_SIZE - 1))
            )
            self.view.display_grid(self.human_fleet.ships_grid(False), Areas.AG)
            self.view.display_grid(self.human_fleet.ships_grid(True), Areas.BS)
