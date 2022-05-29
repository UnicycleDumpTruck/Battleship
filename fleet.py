from enum import Enum
from random import randint, choice
from itertools import chain
from collections import namedtuple
import contextlib

with contextlib.suppress(ImportError):
    from typing import Tuple, Optional, NamedTuple, List, Union
from rich.traceback import install
from loguru import logger

install(show_locals=True)

# Size of coordinate grid upon which game takes place:
GRID_SIZE = 9

# Alphabetic row headings:
headings = [chr(number + ord("a")) for number in range(GRID_SIZE)]


# Orientation state of ship on grid
class Orientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


# Commands for flipping, not moving, or direction to move points & ships
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    FLIP = 5
    NONE = 6


# Names and lengths of ships
ship_sizes = {
    "Patrol Boat": 2,
    "Submarine": 3,
    "Destroyer": 3,
    "Battleship": 4,
    "Aircraft Carrier": 5,
}

ship_capitals = set(boat[0] for boat in ship_sizes.keys())

hit_chars = {"H", "M", None}
hit_chars.update(c.lower() for c in ship_capitals)

# Used to represent x,y coordinates
Point = namedtuple("Point", ["x", "y"])


def point_moved(point: Point, direction: Direction, distance: int = 1):
    """Returns a new point at the projected location. Does not modify original."""
    if direction == Direction.UP:
        return Point(y=(point.y - distance), x=point.x)
    if direction == Direction.DOWN:
        return Point(y=(point.y + distance), x=point.x)
    if direction == Direction.LEFT:
        return Point(y=point.y, x=(point.x - distance))
    if direction == Direction.RIGHT:
        return Point(y=point.y, x=(point.x + distance))
    raise ValueError("Invalid direction given, can't project.")


def point_valid(point: Point):
    """Returns True if point is within grid bounds."""
    if (point.x < 0) or (GRID_SIZE <= point.x):
        return False
    if (point.y < 0) or (GRID_SIZE <= point.y):
        return False
    return True


def point_above(point: Point) -> Optional[Point]:
    return None if point.y < 1 else Point(point.x, point.y - 1)


def point_left(point: Point) -> Optional[Point]:
    return None if point.x < 1 else Point(point.x - 1, point.y)


def point_right(point: Point) -> Optional[Point]:
    return None if point.x > GRID_SIZE - 2 else Point(point.x + 1, point.y)


def point_below(point: Point) -> Optional[Point]:
    return None if point.y > GRID_SIZE - 2 else Point(point.x, point.y + 1)


def surrounding_points(point: Point) -> List:
    funcs = [point_above, point_left, point_right, point_below]
    surrounding = [f(point) for f in funcs]
    return list(filter(None, surrounding))


class Ship:
    """Ship of the fleet."""

    def __init__(
        self,
        ship_type: str,
        ship_size: int,
        ship_start: Point,
        ship_horiz: bool,
        ship_temp: bool = False,
    ):
        """Initialize the Ship."""
        self.ship_start = ship_start
        self.ship_type = ship_type
        self.ship_size = ship_size
        self.ship_horiz = ship_horiz
        self.ship_temp = ship_temp
        self.ship_sunk = False
        self.ship_coords = {}
        if ship_horiz:
            for i in range(ship_size):
                self.ship_coords[
                    point_moved(ship_start, Direction.DOWN, i)
                ] = self.char()
        else:
            for i in range(ship_size):
                self.ship_coords[
                    point_moved(ship_start, Direction.RIGHT, i)
                ] = self.char()

    def char(self) -> str:
        """Return the character representing ship type or temp ship."""
        return "*" if self.ship_temp else self.ship_type[0]

    def __repr__(self) -> str:
        """Return string representation of Ship object."""
        return f"{self.ship_type}, on {self.ship_coords.items()}"

    def take_fire(self, coord: Point) -> bool:
        """Given a point, mark self and return True if hits."""
        if self.ship_coords.get(coord):
            self.ship_coords[coord] = "H"  # Hit!
            if all(ch == "H" for ch in self.ship_coords.values()):
                self.sink()
            return True
        return False

    def sink(self) -> None:
        """Record self as sunk."""
        self.ship_sunk = True
        for key in self.ship_coords.keys():
            self.ship_coords[key] = self.char().lower()


class Square():
    def __init__(self, x: int, y: int, label: str, highlit: str = None):
        """Initialize Square."""
        self.x = x
        self.y = y
        self._label = label
        self.highlit = highlit

    def get_label(self):
        """Return label for grid square, such as 'w' for water, 'p' for patrol boat."""
        return self._label

    def set_label(self, label: str):
        """Set label for grid square, such as 'w' for water, 'p' for patrol boat."""
        self._label = label

    def set_highlight(self, highlight_type: str):
        """Store type of highlight, perhaps primary or secondary."""
        self.highlit = highlight_type

    def remove_highlight(self):
        """Remove highlighting."""
        self.highlit = None

    def __eq__(self, other):
        """Return equality, checking only x and y."""
        return self.x == other.x and self.y == other.y and type(other) == type(self)

    def __hash__(self) -> int:
        """Return hash of only x and y."""
        return hash(self._x, self._y)

    def __repr__(self) -> str:
        return self._label


class Grid:
    """Grid of Squares containing characters and highlight status."""
    def __init__(self, side_length):
        self._grid = [[Square(x, y, "w") for x in range(side_length)] for y in range(side_length)]

    def get_char_at(self, coords: Optional[Point]) -> str:
        """Return water or letter of ship (sunk or not) at coords."""
        return self._grid[coords.y][coords.x].get_label() if coords else None

    def set_label_at(self, coords: Point, label: str):
        self._grid[coords.y][coords.x].set_label(label)

    def list_of_squares_as_points(self):
        """Return a list of Points representing each grid square."""
        return [
            Point(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
        ]

    def ships_grid(self, show_ships: bool, headers: bool):
        """Return string representation of grid, with or without ships."""
        grid_str = ""
        if headers:
            row_headings = iter(headings)
            grid_str += " "  # Space before top heading row
            grid_str += "".join(map(str, range(1, GRID_SIZE + 1)))
            grid_str += "\n"
        for row in self._grid:
            if headers:
                grid_str += next(row_headings)
                grid_str += ""
            for column in row:
                if show_ships:
                    grid_str += column.get_label() + ""
                else:
                    if column.get_label() in {"a", "s", "p", "d", "b", "X", "H", "M", "w"}:
                        grid_str += column.get_label() + ""
                    else:
                        grid_str += "w"
            grid_str += "\n"
        grid_str += "\n"
        return grid_str


class Fleet:
    """Fleet of Ships and Grid of hits and misses."""

    def __init__(self, name):
        """Initialize Fleet."""
        self.name = name
        self._fleet_grid = Grid(GRID_SIZE)
        self.taken_coords = set()
        self.ships = set()
        self.wounded_ships = set()
        self.defeated = False
        self.point_list = self._fleet_grid.list_of_squares_as_points()

    def random_unshot_point(self):
        while True:
            p = Point(y=randint(0, GRID_SIZE - 1), x=randint(0, GRID_SIZE - 1))
            if self.at_point(p) not in hit_chars:
                return p

    def at_point(self, coords: Optional[Point]) -> str:
        """Return character at given Point on grid. Used to check for duplicate shot."""
        return self._fleet_grid.get_char_at(coords) if coords else None


    def unsunk_hits(self) -> List[Point]:
        """Return list of points marked as hit, but not sunk."""
        # listy = self.point_list
        return [p for p in self.point_list if self.at_point(p) == "H"]

    def lone_point(self, coords: Point) -> bool:
        """Returns true if point has no hits or misses around it."""
        return all(
            self.at_point(p) not in hit_chars for p in surrounding_points(coords)
        )

    def possible_hits_for_point(self, point: Point) -> List[Optional[Point]]:
        points = []
        # logger.debug(f"Surrounding points of H: {surrounding_points(point)}")
        # logger.debug(
        #     f"Surrounding chars of H: {[self.at_point(p) for p in surrounding_points(point)]}"
        # )
        if self.lone_point(point):
            points.extend(surrounding_points(point))
        # logger.debug(points)
        if self.at_point(point_above(point)) not in hit_chars and self.hit_below(point):
            points.append(point_above(point))
        if self.at_point(point_below(point)) not in hit_chars and self.hit_above(point):
            points.append(point_below(point))
        if self.at_point(point_left(point)) not in hit_chars and self.hit_right(point):
            points.append(point_left(point))
        if self.at_point(point_right(point)) not in hit_chars and self.hit_left(point):
            points.append(point_right(point))
        # logger.debug(points)
        points.extend(
            [p for p in surrounding_points(point) if self.at_point(p) not in hit_chars]
        )
        # logger.debug(points)
        return points

    def possible_hits(self):
        # logger.debug(self.unsunk_hits())
        return list(
            chain.from_iterable(
                self.possible_hits_for_point(p) for p in self.unsunk_hits()
            )
        )

    def hit_above(self, point: Point) -> bool:
        """Returns true if there is a hit above."""
        return self.at_point(point_above(point)) == "H"

    def hit_below(self, point: Point) -> bool:
        """Returns true if there is a hit below."""
        return self.at_point(point_below(point)) == "H"

    def hit_left(self, point: Point) -> bool:
        """Returns true if there is a hit left."""
        return self.at_point(point_left(point)) == "H"

    def hit_right(self, point: Point) -> bool:
        """Returns true if there is a hit right."""
        return self.at_point(point_right(point)) == "H"

    def ships_grid(self, show_ships: bool, headers: bool = False):
        self.refresh_grid()
        return self._fleet_grid.ships_grid(show_ships=show_ships, headers=False)

    def refresh_grid(self):
        """Rewrite coords from ships to accomadate recent hits."""
        for ship in self.ships:
            for coord in ship.ship_coords.keys():
                self._fleet_grid.set_label_at(coord, label=ship.ship_coords[coord]),

    def take_fire(self, coord: Point) -> Tuple[bool, str, bool]:
        """Pass coord to ships to check for hits, mark ship and/or grid."""
        hit = False
        sunk = ""
        for s in self.ships:
            if s.take_fire(coord):
                self.wounded_ships.add(s)
                # logger.debug(self.wounded_ships)
                hit = True
                # logger.info("Hit!")
                if s.ship_sunk:
                    self.wounded_ships.remove(s)
                    # logger.debug(self.wounded_ships)
                    sunk = s.ship_type
                    if all(ship.ship_sunk for ship in self.ships):
                        self.defeated = True
                return (hit, sunk, self.defeated)

        self._fleet_grid.set_label_at(coord, "M")
        # logger.info("Miss!")
        self.refresh_grid()
        return (hit, sunk, self.defeated)

    def add_ship(self, ship: Ship) -> None:
        """Add a ship to the Fleet, and mark its coords as taken."""
        if self.valid_anchor(ship):
            ship.ship_temp = False
            self.ships.add(ship)
            for coord in ship.ship_coords.keys():
                ship.ship_coords[coord] = ship.char()
                self.taken_coords.add((coord.y, coord.x))
        else:
            raise ValueError("Can't add ship there, it overlaps other ships.")

    def add_tentative_ship(self, ship: Ship) -> None:
        """Add a ship to the Fleet, but DON'T mark the coordinates as taken."""
        if self.valid_anchor(ship):
            self.ships.add(ship)
            self.refresh_grid()

    def remove_tentative_ship(self, ship: Ship) -> None:
        """Remove temporary ship from fleet, usually to move it elsewhere."""
        self.ships.remove(ship)
        for coord in ship.ship_coords.keys():
            self._fleet_grid.set_label_at(coord, "w")
        self.refresh_grid()

    def valid_anchor(self, ship: Ship) -> bool:
        """Given a ship, return True if it fits without overlapping others or borders."""
        for coord in ship.ship_coords:
            if (coord.y, coord.x) in self.taken_coords:
                # Overlaps other ship
                return False
            if (coord.x >= GRID_SIZE) or (coord.y >= GRID_SIZE):
                # Reaches off grid
                return False
        return True

    def next_valid_ship(self, ship: Ship, direction: Direction) -> Ship:
        """Given a ship and a direction to move, return next valid ship, or same."""
        start = ship.ship_start
        cardinals = {Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        while point_valid(start):
            if direction in cardinals:
                start = point_moved(start, direction)
                if point_valid(start):
                    test = Ship(
                        ship.ship_type,
                        ship.ship_size,
                        start,
                        ship.ship_horiz,
                        ship.ship_temp,
                    )
                    if self.valid_anchor(test):
                        return test
            elif direction == Direction.FLIP:
                test = Ship(
                    ship.ship_type,
                    ship.ship_size,
                    start,
                    not ship.ship_horiz,
                    ship.ship_temp,
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
        """Generate randomly placed Fleet for the computer side."""
        for ship_type in ship_sizes.keys():
            while True:
                ship = Ship(
                    ship_type=ship_type,
                    ship_size=ship_sizes[ship_type],
                    ship_start=Point(
                        randint(0, GRID_SIZE - 1), randint(0, GRID_SIZE - 1)
                    ),
                    ship_horiz=choice((True, False)),
                )
                if self.valid_anchor(ship):
                    self.add_ship(ship)
                    break
