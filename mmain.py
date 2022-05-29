from blessed import Terminal
from matrix_views import MatrixView
from combat import HVCCombat
from rich.traceback import install

install(show_locals=True)

term = Terminal()


def main():
    view = MatrixView(term)
    ctrl = HVCCombat(view, True)
    ctrl.run()


if __name__ == "__main__":
    with term.hidden_cursor():
        main()
