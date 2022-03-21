from enum import Enum
from random import randint, choice
from collections import namedtuple
from typing import NamedTuple

try:
    from typing import Tuple
except ImportError:
    pass

GRID_SIZE = 10
headings = [chr(number + ord("a")) for number in range(GRID_SIZE)]


class Orientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


# Ship type: (length)
ship_sizes = {
    "Patrol Boat": 2,
    "Submarine": 3,
    "Destroyer": 3,
    "Battleship": 4,
    "Aircraft Carrier": 5,
}


# Used to represent coordinates of guess shot and char of hit/miss.
# Shot = namedtuple("Shot", ["x", "y", "c"])


class Ship:
    """Ships of the fleet."""

    def __init__(
        self,
        ship_type: str,
        ship_size: int,
        ship_start: Tuple[int, int],
        ship_horiz: bool,
        ship_temp: bool = False,
    ):
        self.ship_type = ship_type
        self.ship_size = ship_size
        self.ship_horiz = ship_horiz
        self.ship_temp = ship_temp
        self.ship_sunk = False
        self.ship_coords = dict()
        if ship_horiz:
            for i in range(ship_size):
                self.ship_coords[((ship_start[0] + i), ship_start[1])] = self.char()
        else:
            for i in range(ship_size):
                self.ship_coords[((ship_start[0]), ship_start[1] + i)] = self.char()

    def char(self):
        if self.ship_temp:
            return "*"
        return self.ship_type[0]

    def __repr__(self):
        return f"{self.ship_type}, on {self.ship_coords.items()}"

    def take_fire(self, coord):
        if self.ship_coords.get(coord):
            self.ship_coords[coord] = "H"  # Hit!
            if not any([ch != "H" for ch in self.ship_coords.values()]):
                self.sink()
            return True

    def sink(self):
        self.ship_sunk = True
        print(f"You sunk my {self.ship_type}")

    def deploy(self):
        print(f"Deploying a {self.ship_type} of size {self.ship_size}:")
        orientation = ""
        while not (orientation == "h" or orientation == "v"):
            orientation = input("Horizontal or Vertical ('h' or 'v')? ")
        row = int(input("Row (1 through 10)? "))
        column = int(input("Column (1 through 10)? "))
        return (row, column, self.ship_size)


class Grid:
    def __init__(self, name):
        self.name = name
        self.grid = [["w" for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        self.taken_coords = set()
        self.ships = set()

    def print_grid(self):
        """Transfer grid to string then print to console."""
        self.refresh_grid()
        grid_str = "  "  # Space before top heading row
        grid_str += " ".join(map(str, range(1, GRID_SIZE + 1)))
        grid_str += "\n"
        row_headings = (h for h in headings)
        for row in self.grid:
            grid_str += next(row_headings)
            grid_str += " "
            for column in row:
                grid_str += column + " "
            grid_str += "\n"
        grid_str += "\n"

        print(grid_str)


# class Guesses(Grid):
#     def __init__(self, name):
#         super().__init__(name)
#         self.guesses = set(NamedTuple)

#     def record_fire(self, coords: Shot):
#         if coords not in self.guesses:
#             self.guesses.add(coords)
#             self.refresh_grid()
#         else:
#             raise ValueError("Repeat guess.")


class Fleet(Grid):
    def __init__(self, name):
        super().__init__(name)
        self.ships = set()

    def refresh_grid(self):
        """Rebuild grid from ships to accomadate recent shots."""
        self.grid = [["w" for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        for ship in self.ships:
            for coord in ship.ship_coords.keys():
                self.grid[coord[0]][coord[1]] = ship.ship_coords[coord]

    def take_fire(self, coord):
        """Pass coord to ships to check for hits, mark ship or grid."""
        if any([s.take_fire(coord) for s in self.ships]):
            print("Hit!")
        else:
            self.grid[coord[0]][coord[1]] = "M"
        self.refresh_grid()

    def add_ship(self, ship: Ship) -> None:
        if self.valid_anchor(ship):
            ship.ship_temp = False
            self.ships.add(ship)
            for coord in ship.ship_coords.keys():
                ship.ship_coords[coord] = ship.char()
                self.taken_coords.add(coord)
        else:
            raise ValueError("Can't add ship there, it overlaps other ships.")

    def add_tentative_ship(self, ship: Ship) -> None:
        if self.valid_anchor(ship):
            self.ships.add(ship)
            self.refresh_grid()
            self.print_grid()
            print(self.ships)

    def remove_tentative_ship(self, ship: Ship) -> None:
        print(ship in self.ships)
        self.ships.remove(ship)
        print(ship in self.ships)
        self.refresh_grid()
        self.print_grid()
        print(self.ships)

    def valid_coords(self, coords) -> bool:
        if (coords[0] >= GRID_SIZE) or (coords[1] >= GRID_SIZE):
            return False
        return True

    def valid_anchor(self, ship: Ship) -> bool:
        for coord in ship.ship_coords:
            if coord in self.taken_coords:
                # Overlaps other ship
                return False
            if (coord[0] >= GRID_SIZE) or (coord[1] >= GRID_SIZE):
                # Reaches off grid
                return False
        return True

    def deploy_computer_fleet(self):
        for ship_type in ship_sizes.keys():
            while True:
                ship = Ship(
                    ship_type=ship_type,
                    ship_size=ship_sizes[ship_type],
                    ship_start=(randint(0, 11), randint(0, 11)),
                    ship_horiz=choice((True, False)),
                )
                if self.valid_anchor(ship):
                    self.add_ship(ship)
                    break


if __name__ == "__main__":
    computer_fleet = Fleet("Computer Fleet")
    computer_fleet.deploy_computer_fleet()
    computer_fleet.print_grid()

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
        computer_fleet.take_fire((row_guess, col_guess))
        computer_fleet.print_grid()
