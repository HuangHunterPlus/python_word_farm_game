import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from game import Game
from menu import MenuManager


def main():
    game = Game()
    menu = MenuManager(game)
    while game.running:
        game.tick()
        menu.show_main_menu()


if __name__ == "__main__":
    main()
