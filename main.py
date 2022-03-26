from views import CursesView
from combat import HVCCombat
from curses import wrapper


def main(stdscr):
    view = CursesView(stdscr)
    ctrl = HVCCombat(view)
    ctrl.run()


if __name__ == "__main__":
    wrapper(main)  # Curses wrapper to return terminal to normal after exceptions
