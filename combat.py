from abc import ABC
from random import randint, choice
from time import sleep
from rich.traceback import install
from loguru import logger

import fleet
import views

install(show_locals=True)


class HVCCombat:
    """Human vs computer combat controller."""

    def __init__(self, view):
        self.view = view
        self.computer_fleet = fleet.Fleet("Computer Fleet")
        self.computer_fleet.deploy_computer_fleet()
        self.view.display_grid(self.computer_fleet.ships_grid(False), views.Areas.BG)
        self.view.display_grid(self.computer_fleet.ships_grid(True), views.Areas.AS)
        self.human_fleet = fleet.Fleet("Human Fleet")
        self.view.display_grid(self.human_fleet.ships_grid(False), views.Areas.AG)

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
                    self.view.display_grid(
                        self.human_fleet.ships_grid(True), views.Areas.BS
                    )
                    self.view.display_text(
                        f"New {ship.ship_type}:\n wasd to move,\n f to flip \n enter to anchor",
                        views.Areas.BT,
                    )
                    chr_in = self.view.get_direction()
                    self.view.display_text("", views.Areas.BS)
                    # qu = f"Enter to anchor {ship.ship_type} wasd to move: "
                    # chr_in = input(qu).lower()
                    if chr_in == "\n":
                        self.human_fleet.remove_tentative_ship(ship)
                        self.human_fleet.add_ship(ship)
                        self.view.display_grid(
                            self.human_fleet.ships_grid(True), views.Areas.BS
                        )
                        break
                    else:
                        self.human_fleet.remove_tentative_ship(ship)
                        next_direction = cmds.get(chr_in, fleet.Direction.NONE)
                        self.view.display_grid(
                            self.human_fleet.ships_grid(True), views.Areas.BS
                        )
                        continue
                # else:
                #     ship = self.human_fleet.next_valid_ship(ship, next_direction)

    def computer_a_turn(self):
        game_over = False
        if wounded := self.human_fleet.possible_hits():
            coords = wounded[0]
        else:
            coords = self.human_fleet.random_unshot_point()
        results = self.human_fleet.take_fire(coords)
        if results[2]:
            feedback = f"You sunk my {results[1]} and WON THE GAME!"
            game_over = True
        elif results[0] and results[1]:
            feedback = f"You sunk my {results[1]}!"
        elif results[0]:
            feedback = f"Hit at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        else:
            feedback = f"Miss at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        self.view.display_text(feedback, views.Areas.AF)
        self.view.display_grid(self.human_fleet.ships_grid(False), views.Areas.AG)
        self.view.display_grid(self.human_fleet.ships_grid(True), views.Areas.BS)
        return game_over

    def player_b_turn(self):
        game_over = False
        coords = self.view.get_fire_coords(self.computer_fleet)
        results = self.computer_fleet.take_fire(coords)
        if results[2]:
            feedback = f"You sunk my {results[1]} and WON THE GAME!"
            game_over = True
        elif results[0] and results[1]:
            feedback = f"You sunk my {results[1]}!"
        elif results[0]:
            feedback = f"Hit at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        else:
            feedback = f"Miss at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        self.view.display_text(feedback, views.Areas.BF)
        self.view.display_grid(self.computer_fleet.ships_grid(False), views.Areas.BG)
        self.view.display_grid(self.computer_fleet.ships_grid(True), views.Areas.AS)
        return game_over

    def run(self):
        self.view.display_grid(self.computer_fleet.ships_grid(True), views.Areas.AS)
        self.view.display_grid(self.computer_fleet.ships_grid(False), views.Areas.BG)
        self.input_human_ships()
        while True:
            if self.player_b_turn():
                # Player a won!
                pass
            if self.computer_a_turn():
                # Player b won!
                pass
