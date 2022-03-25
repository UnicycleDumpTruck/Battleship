from enum import Enum
from random import randint, choice

# from collections import namedtuple

try:
    from typing import Tuple, Optional
except ImportError:
    pass

from loguru import logger

GRID_SIZE = 10
headings = [chr(number + ord("a")) for number in range(GRID_SIZE)]


class Orientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    FLIP = 5
    NONE = 6


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


class Point:
    """Hold coordinate point for a ship, methods to move."""

    def __init__(self, y: int, x: int) -> None:
        self.x = x
        self.y = y
        # self.c = c

    def __repr__(self):
        return f"x: {self.x}, y: {self.y}"

    def move(self, direction: Direction, distance: int = 1):
        """Modifies self to move in given direction for distance."""
        if direction == Direction.UP:
            self.y -= distance
        if direction == Direction.DOWN:
            self.y += distance
        if direction == Direction.LEFT:
            self.x -= distance
        if direction == Direction.RIGHT:
            self.x += distance
        return self

    def moved(self, direction: Direction, distance: int):
        """Returns a new point at the projected location. Does not modify self."""
        if direction == Direction.UP:
            return Point(y=(self.y - distance), x=self.x)
        if direction == Direction.DOWN:
            return Point(y=(self.y + distance), x=self.x)
        if direction == Direction.LEFT:
            return Point(y=self.y, x=(self.x - distance))
        if direction == Direction.RIGHT:
            return Point(y=self.y, x=(self.x + distance))
        raise ValueError("Invalid direction given, can't project.")

    def valid(self) -> bool:
        if (self.x < 0) or (self.x >= GRID_SIZE):
            return False
        if (self.y < 0) or (self.y >= GRID_SIZE):
            return False
        return True


class Ship:
    """Ships of the fleet."""

    def __init__(
        self,
        ship_type: str,
        ship_size: int,
        ship_start: Point,
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
                self.ship_coords[ship_start.moved(Direction.DOWN, i)] = self.char()
        else:
            for i in range(ship_size):
                self.ship_coords[ship_start.moved(Direction.RIGHT, i)] = self.char()

    def char(self):
        if self.ship_temp:
            return "*"
        return self.ship_type[0]

    def __repr__(self):
        return f"{self.ship_type}, on {self.ship_coords.items()}"

    def take_fire(self, coord):
        logger.debug("Ship taking fire.")

        if self.ship_coords.get(coord):
            self.ship_coords[coord] = "H"  # Hit!
            logger.debug("ship_coords.values() ", self.ship_coords.values())
            if not any([ch != "H" for ch in self.ship_coords.values()]):
                self.sink()
            return True

    def sink(self):
        self.ship_sunk = True
        print(f"You sunk my {self.ship_type}")

    # def deploy(self):
    #     print(f"Deploying a {self.ship_type} of size {self.ship_size}:")
    #     orientation = ""
    #     while not (orientation == "h" or orientation == "v"):
    #         orientation = input("Horizontal or Vertical ('h' or 'v')? ")
    #     row = int(input("Row (1 through 10)? "))
    #     column = int(input("Column (1 through 10)? "))
    #     return (row, column, self.ship_size)


class Fleet:
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
        print(self.name)
        print(grid_str)

    def refresh_grid(self):
        """Rebuild grid from ships to accomadate recent shots."""
        self.grid = [["w" for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        for ship in self.ships:
            for coord in ship.ship_coords.keys():
                self.grid[coord.y][coord.x] = ship.ship_coords[coord]

    def take_fire(self, coord):
        """Pass coord to ships to check for hits, mark ship or grid."""
        if any([s.take_fire(coord) for s in self.ships]):
            print("Hit!")
        else:
            self.grid[coord[0]][coord[0]] = "M"
            print("Miss!")
        self.refresh_grid()

    def add_ship(self, ship: Ship) -> None:
        if self.valid_anchor(ship):
            ship.ship_temp = False
            self.ships.add(ship)
            for coord in ship.ship_coords.keys():
                ship.ship_coords[coord] = ship.char()
                self.taken_coords.add((coord.y, coord.x))
        else:
            raise ValueError("Can't add ship there, it overlaps other ships.")

    def add_tentative_ship(self, ship: Ship) -> None:
        if self.valid_anchor(ship):
            self.ships.add(ship)
            self.refresh_grid()
            self.print_grid()
            print("Tentative added to set. Set: ", self.ships)

    def remove_tentative_ship(self, ship: Ship) -> None:
        self.ships.remove(ship)
        self.refresh_grid()
        self.print_grid()
        print(self.ships)

    def valid_anchor(self, ship: Ship) -> bool:
        logger.debug("valid_anchor ship_coords, then taken_coords")
        logger.debug(ship.ship_coords)
        logger.debug(self.taken_coords)
        for coord in ship.ship_coords:
            if (coord.y, coord.x) in self.taken_coords:
                # Overlaps other ship
                logger.debug("Overlap detected.")
                return False
            if (coord.x >= GRID_SIZE) or (coord.y >= GRID_SIZE):
                # Reaches off grid
                return False
        return True

    def next_valid_ship(self, ship: Ship, direction: Direction) -> Ship:
        """Given a ship and a direction to move, return next valid ship, or same."""
        coords = list(ship.ship_coords.keys())
        start = Point(coords[0].y, coords[0].x)
        cardinals = {Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        while start.valid():
            print(ship)
            if direction in cardinals:
                start.move(direction)
                if start.valid():
                    test = Ship(
                        ship.ship_type,
                        ship.ship_size,
                        start,
                        ship.ship_horiz,
                        # ship.ship_temp,
                    )
                    if self.valid_anchor(test):
                        return test
            elif direction == Direction.FLIP:
                test = Ship(
                    ship.ship_type,
                    ship.ship_size,
                    start,
                    not ship.ship_horiz,
                    # ship.ship_temp,
                )
                if self.valid_anchor(test):
                    return test
                return ship
            elif direction == Direction.NONE:
                return ship
            else:
                raise ValueError("Invalid direction.")
        return ship

    def deploy_computer_fleet(self):
        for ship_type in ship_sizes.keys():
            while True:
                ship = Ship(
                    ship_type=ship_type,
                    ship_size=ship_sizes[ship_type],
                    ship_start=Point(randint(0, 11), randint(0, 11)),
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
