from abc import ABC
from fleet import Ship, Fleet, headings, GRID_SIZE


class Combat(ABC):
    """Abstract base class for combat controllers."""

    def __init__(self):
        pass


class HVCCombat(Combat):
    """Human vs computer combat controller."""

    def __init__(self):
        self.computer_fleet = Fleet("Computer Fleet")
        self.computer_fleet.deploy_computer_fleet()

    def run(self):
        self.computer_fleet.print_grid()
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
