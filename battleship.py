# Battleship game simulator

GRID_SIZE = 10

#   1  2  3  4  5  6  7  8  9  10
# A
# B
# C
# D
# E
# F
# G
# H
# I
# J

# Aircraft Carrier: 5, battleship: 4, Sub: 3, Destroyer: 3, Patrol Boat: 2

# Initialize empty display grids
# player_a_fleet = [[['w'] for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
# player_b_fleet = [[['w'] for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
# player_a_shots = [[['n'] for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
# player_b_shots = [[['n'] for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]


class Grid:
    def __init__(self, name):
        self.name = name
        self.grid = [[[None] for i in range(GRID_SIZE)]
                     for j in range(GRID_SIZE)]


class Ship:
    ship_type = None
    ship_size = None
    ship_orientation = None
    ship_coords = None

    def __init__(self, t, s):
        self.ship_type = t
        self.ship_size = s

    def printShip(self):
        print(self.ship_type)


class Player:
    def __init__(self, name):
        self.name = name
        self.ships = [
            Ship("Aircraft Carrier", 5),
            Ship("Battleship", 4),
            Ship("Submarine", 3),
            Ship("Destroyer", 3),
            Ship("Patrol Boat", 2),
        ]

    def printPlayer(self):
        print(self.name)
        for ship in self.ships:
            ship.printShip()


player_a = Player("Player A")
player_b = Player("Player B")

player_a.printPlayer()
player_b.printPlayer()
