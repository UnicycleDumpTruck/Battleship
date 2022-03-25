from abc import ABC
from random import randint
from rich.traceback import install

from fleet import Ship, Fleet, headings, GRID_SIZE, ship_sizes, Direction, Point

install(show_locals=True)


class Combat(ABC):
    """Abstract base class for combat controllers."""

    def __init__(self):
        pass


class HVCCombat(Combat):
    """Human vs computer combat controller."""

    def __init__(self):
        self.computer_fleet = Fleet("Computer Fleet")
        self.computer_fleet.deploy_computer_fleet()
        self.human_fleet = Fleet("Human Fleet")

    def input_ships(self):
        for ship_type in ship_sizes.keys():
            next_direction = Direction.RIGHT
            ship = Ship(
                ship_type=ship_type,
                ship_size=ship_sizes[ship_type],
                ship_start=Point(0, 0),
                ship_horiz=True,
                # ship_temp=True,
            )

            while True:
                # if not self.human_fleet.valid_anchor(ship):
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
                    qu = f"Enter to anchor {ship.ship_type} wasd to move: "
                    chr_in = input(qu).lower()
                    if chr_in == "":
                        self.human_fleet.remove_tentative_ship(ship)
                        self.human_fleet.add_ship(ship)
                        self.human_fleet.print_grid()
                        break
                    else:
                        self.human_fleet.remove_tentative_ship(ship)
                        next_direction = cmds.get(chr_in, Direction.NONE)
                        continue
                # else:
                #     ship = self.human_fleet.next_valid_ship(ship, next_direction)

    def run(self):
        self.computer_fleet.print_grid()
        self.input_ships()
        while True:
            while True:
                row_guess = input("Row letter? ").strip().lower()
                if row_guess in headings:
                    row_guess = ord(row_guess) - 97
                    break

            while True:
                col_guess = int(input("Column number? ").strip().lower())
                if 0 <= col_guess and col_guess <= GRID_SIZE:
                    col_guess = col_guess - 1
                    break

            self.computer_fleet.take_fire(Point(y=row_guess, x=col_guess))
            self.computer_fleet.print_grid()


if __name__ == "__main__":
    ctrl = HVCCombat()
    ctrl.run()
