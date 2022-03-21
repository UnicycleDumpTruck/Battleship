from abc import ABC
from random import randint
from fleet import Ship, Fleet, headings, GRID_SIZE, ship_sizes


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
            while True:
                ship = Ship(
                    ship_type=ship_type,
                    ship_size=ship_sizes[ship_type],
                    ship_start=(randint(0, GRID_SIZE), randint(0, GRID_SIZE)),
                    ship_horiz=True,
                    ship_temp=True,
                )
                if self.human_fleet.valid_anchor(ship):
                    self.human_fleet.add_tentative_ship(ship)
                    # TODO: add horizontal/vertical flip ability.
                    qu = "Would you like you your %s here? (y/n)" % ship.ship_type
                    if input(qu).lower() == "y":
                        self.human_fleet.remove_tentative_ship(ship)
                        self.human_fleet.add_ship(ship)
                        self.human_fleet.print_grid()
                        break
                    else:
                        self.human_fleet.remove_tentative_ship(ship)
                        continue

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

            print(row_guess, col_guess)
            self.computer_fleet.take_fire((row_guess, col_guess))
            self.computer_fleet.print_grid()


if __name__ == "__main__":
    ctrl = HVCCombat()
    ctrl.run()
