import curses
from views import View
import fleet


class CursesView(View):
    def __init__(self, controller, model):
        self.controller = controller
        self.model = model
        # model.register_observer()

    def display_ships(self, fleet: fleet.Fleet, location):
        print(fleet.grid_ships())

    def display_fire(self, fleet: fleet.Fleet, location):
        print(fleet.grid_incoming_fire())
