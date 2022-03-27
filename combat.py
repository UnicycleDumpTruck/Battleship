from abc import ABC
from random import randint, choice
from curses import wrapper
from time import sleep
from rich.traceback import install
from loguru import logger

# from fleet import Ship, Fleet, headings, GRID_SIZE, ship_sizes, Direction, Point
import fleet
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
        self.computer_fleet = fleet.Fleet("Computer Fleet")
        self.computer_fleet.deploy_computer_fleet()
        self.view.display_grid(self.computer_fleet.ships_grid(False), Areas.BG)
        self.view.display_grid(self.computer_fleet.ships_grid(True), Areas.AS)
        self.human_fleet = fleet.Fleet("Human Fleet")
        self.view.display_grid(self.human_fleet.ships_grid(False), Areas.AG)

    def input_human_ships(self):
        for ship_type in fleet.ship_sizes.keys():
            next_direction = fleet.Direction.NONE
            ship = fleet.Ship(
                ship_type=ship_type,
                ship_size=fleet.ship_sizes[ship_type],
                ship_start=fleet.Point(x=0, y=0),
                ship_horiz=choice((True, False)),
                # ship_temp=True,
            )

            while True:
                if not self.human_fleet.valid_anchor(ship):
                    next_direction = choice(list(fleet.Direction))
                ship = self.human_fleet.next_valid_ship(ship, next_direction)
                if self.human_fleet.valid_anchor(ship):
                    self.human_fleet.add_tentative_ship(ship)
                    cmds = {
                        "w": fleet.Direction.UP,
                        "s": fleet.Direction.DOWN,
                        "a": fleet.Direction.LEFT,
                        "d": fleet.Direction.RIGHT,
                        "f": fleet.Direction.FLIP,
                    }
                    self.view.display_grid(self.human_fleet.ships_grid(True), Areas.BS)
                    self.view.display_text(
                        f"New {ship.ship_type}:\n wasd to move,\n f to flip \n enter to anchor",
                        Areas.BT,
                    )
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
                        next_direction = cmds.get(chr_in, fleet.Direction.NONE)
                        self.view.display_grid(
                            self.human_fleet.ships_grid(True), Areas.BS
                        )
                        continue
                # else:
                #     ship = self.human_fleet.next_valid_ship(ship, next_direction)

    def computer_a_turn(self):
        game_over = False
        coords = fleet.Point(
            y=randint(0, fleet.GRID_SIZE - 1), x=randint(0, fleet.GRID_SIZE - 1)
        )
        results = self.human_fleet.take_fire(coords)
        if results[2]:
            feedback = f"You sunk my {results[1]} and WON THE GAME!"
            game_over = True
        elif results[0] and results[1]:
            feedback = f"You sunk my {results[1]}!"
        elif results[0]:
            feedback = "Hit!"
        else:
            feedback = "Miss!"
        self.view.display_text(feedback, Areas.AF)
        self.view.display_grid(self.human_fleet.ships_grid(False), Areas.AG)
        self.view.display_grid(self.human_fleet.ships_grid(True), Areas.BS)
        return game_over

    def player_b_turn(self):
        game_over = False
        coords = self.view.get_fire_coords()
        results = self.computer_fleet.take_fire(coords)
        if results[2]:
            feedback = f"You sunk my {results[1]} and WON THE GAME!"
            game_over = True
        elif results[0] and results[1]:
            feedback = f"You sunk my {results[1]}!"
        elif results[0]:
            feedback = "Hit!"
        else:
            feedback = "Miss!"
        self.view.display_text(feedback, Areas.BF)
        # self.view.display_text(feedback, Areas.BT)
        self.view.display_grid(self.computer_fleet.ships_grid(False), Areas.BG)
        self.view.display_grid(self.computer_fleet.ships_grid(True), Areas.AS)
        return game_over

    def run(self):
        self.view.display_grid(self.computer_fleet.ships_grid(True), Areas.AS)
        self.view.display_grid(self.computer_fleet.ships_grid(False), Areas.BG)
        self.input_human_ships()
        while True:
            if self.player_b_turn():
                # Player a won!
                pass
            if self.computer_a_turn():
                # Player b won!
                pass
