from blessed import Terminal
from views import RichView
from combat import HVCCombat
from rich.traceback import install

install(show_locals=True)

term = Terminal()


def main():
    view = RichView(term)
    ctrl = HVCCombat(view)
    ctrl.run()


if __name__ == "__main__":
    with term.hidden_cursor():
        main()
