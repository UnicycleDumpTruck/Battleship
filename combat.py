from abc import ABC
from random import randint, choice
from time import sleep
import concurrent.futures
from rich.traceback import install
from loguru import logger
from playsound import playsound
import threading
import fleet
import views

install(show_locals=True)


class HVCCombat:
    """Human vs computer combat controller."""

    def __init__(self, view, audio_on=True):
        self.view = view
        self.computer_fleet = fleet.Fleet("Computer Fleet")
        self.computer_fleet.deploy_computer_fleet()
        self.view.display_grid(self.computer_fleet.ships_grid(False), False, views.Areas.BG)
        self.view.display_grid(self.computer_fleet.ships_grid(True), True, views.Areas.AS)
        self.human_fleet = fleet.Fleet("Human Fleet")
        self.view.display_grid(self.human_fleet.ships_grid(False), False, views.Areas.AG)
        self.audio_on = audio_on

    def input_human_ships(self):
        for ship_type in fleet.ship_sizes.keys():
            self.play_nb(f"audio/deploy_your_{ship_type}.mp3")
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
                        "KEY_UP": fleet.Direction.UP,
                        "KEY_DOWN": fleet.Direction.DOWN,
                        "KEY_LEFT": fleet.Direction.LEFT,
                        "KEY_RIGHT": fleet.Direction.RIGHT,
                        "KEY_TAB": fleet.Direction.FLIP,
                    }
                    self.view.display_grid(
                        self.human_fleet.ships_grid(True), True, views.Areas.BS
                    )
                    self.view.display_text(
                        f"New {ship.ship_type}:\nArrows to move,\nTab to flip \nEnter to anchor",
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
                            self.human_fleet.ships_grid(True), True, views.Areas.BS
                        )
                        break
                    else:
                        self.human_fleet.remove_tentative_ship(ship)
                        next_direction = cmds.get(chr_in.name, fleet.Direction.NONE)
                        self.view.display_grid(
                            self.human_fleet.ships_grid(True), True, views.Areas.BS
                        )
                        continue
                # else:
                #     ship = self.human_fleet.next_valid_ship(ship, next_direction)

    # def hit_sound(self, side):
    #     hit_sound_thread = threading.Thread(
    #         target=playsound, args=(f"audio/explosion_{side}.wav",)
    #     )
    #     hit_sound_thread.start()

    def hit_sound(self, side):
        self.play_b(
            f"audio/explosion_{side}.wav",
        )

    def miss_sound(self, side):
        miss_sound_thread = threading.Thread(
            target=playsound, args=(f"audio/splash_{side}.wav",)
        )
        miss_sound_thread.start()

    def win_sound(self, side):
        hit_sound_thread = threading.Thread(
            target=playsound, args=(f"audio/explosion_{side}.wav",)
        )
        hit_sound_thread.start()
        sunk_sound_thread = threading.Thread(
            target=playsound, args=(f"audio/sunk_{side}.wav",)
        )
        sunk_sound_thread.start()
        # sunk_sound_thread.join()
        win_sound_thread = threading.Thread(
            target=playsound, args=(f"audio/win_{side}.wav",)
        )
        win_sound_thread.start()

    def sunk_sound(self, side):
        hit_sound_thread = threading.Thread(
            target=playsound, args=(f"audio/explosion_{side}.wav",)
        )
        hit_sound_thread.start()
        # hit_sound_thread.join()
        sunk_sound_thread = threading.Thread(
            target=playsound, args=(f"audio/sunk_{side}.wav",)
        )
        sunk_sound_thread.start()

    def play_b(self, *args):
        """Play audio in threads, but block and join."""
        if self.audio_on:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.map(playsound, args)

    def play_nb(self, *args):
        """Play non-blocking audio."""
        if self.audio_on:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.map(playsound, args)

    def computer_a_turn(self):
        sleep(0.5)
        game_over = False
        sounds = []
        if wounded := self.human_fleet.possible_hits():
            coords = wounded[0]
        else:
            coords = self.human_fleet.random_unshot_point()
        # self.play_b(
        #     "audio/c_firing.mp3",
        #     f"audio/{chr(coords.y + 97)}.mp3",
        #     f"audio/{coords.x+1}.mp3",
        # )
        results = self.human_fleet.take_fire(coords)
        self.view.display_grid(self.human_fleet.ships_grid(False), False, views.Areas.AG)
        self.view.display_grid(self.human_fleet.ships_grid(True), True, views.Areas.BS)

        if results[2]:
            self.win_sound("l")
            feedback = f"You sunk my {results[1]} and WON THE GAME!"
            game_over = True
        elif results[0] and results[1]:
            self.sunk_sound("l")
            feedback = f"A: You sunk my {results[1]}!"
            self.play_b(f"audio/your_{results[1]}_sunk.mp3")
        elif results[0]:
            self.hit_sound("l")
            feedback = f"Hit at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        else:
            self.miss_sound("l")
            feedback = f"Miss at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        self.view.display_text(feedback, views.Areas.AF)

        self.play_b(*sounds)
        return game_over

    def player_b_turn(self):
        game_over = False
        sounds = []
        # self.play_nb("audio/enter.mp3")
        coords = self.view.get_fire_coords(self.computer_fleet)
        # self.play_b(
        #     "audio/h_firing.mp3",
        #     f"audio/{chr(coords.y + 97)}.mp3",
        #     f"audio/{coords.x+1}.mp3",
        # )
        results = self.computer_fleet.take_fire(coords)
        self.view.display_grid(self.computer_fleet.ships_grid(False), False, views.Areas.BG)
        self.view.display_grid(self.computer_fleet.ships_grid(True), True, views.Areas.AS)

        if results[2]:
            self.win_sound("r")
            feedback = f"You sunk my {results[1]} and WON THE GAME!"
            game_over = True
        elif results[0] and results[1]:
            self.sunk_sound("r")
            feedback = f"B: You sunk my {results[1]}!"
            # playsound(f"audio/you_sunk_{results[1]}.mp3")
            self.play_b(f"audio/you_sunk_{results[1]}.mp3")
        elif results[0]:
            self.hit_sound("r")
            feedback = f"Hit at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        else:
            self.miss_sound("r")
            feedback = f"Miss at {fleet.headings[coords.y].upper()}-{coords.x + 1}!"
        self.view.display_text(feedback, views.Areas.BF)

        self.play_b(*sounds)
        return game_over

    def run(self):
        self.view.display_grid(self.computer_fleet.ships_grid(True), True, views.Areas.AS)
        self.view.display_grid(self.computer_fleet.ships_grid(False), False, views.Areas.BG)
        self.input_human_ships()
        while True:
            if self.player_b_turn():
                # Player a won!
                self.view.show_game_over("Human")
                playsound("audio/h_won.mp3")
                break
            if self.computer_a_turn():
                # Player b won!
                self.view.show_game_over("Computer")
                playsound("audio/c_won.mp3")
                break
