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
        self.grid = [["w" for i in range(GRID_SIZE)]
                     for j in range(GRID_SIZE)]

    def printGrid(self):
        print(self.name)
        for row in self.grid:
            for column in row:
                print(column + " ", end="")
            print("")
        print("")

    def addShip(self, coords):
        self.grid[coords[0]][coords[1]] = str(coords[2])
        self.printGrid()


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

    def deployShip(self):
        print(f"Deploying a {self.ship_type} of size {self.ship_size}:")
        orientation = ""
        while not (orientation == "h" or orientation == "v"):
            orientation = input("Horizontal or Vertical ('h' or 'v')? ")
        row = int(input("Row (1 through 10)? "))
        column = int(input("Column (1 through 10)? "))
        return (row, column, self.ship_size)


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
        self.fleetGrid = Grid(self.name + " Fleet")
        self.shotGrid = Grid(self.name + " Shots")

    def printPlayer(self):
        print(self.name)
        for ship in self.ships:
            ship.printShip()
        self.fleetGrid.printGrid()
        self.shotGrid.printGrid()

    def deployFleet(self):
        for ship in self.ships:
            self.fleetGrid.addShip(ship.deployShip())


class Game:
    def __init__(self):
        self.player_a = Player("Player A")
        self.player_b = Player("Player B")

    def setup_fleets(self):
        self.player_a.deployFleet()
        self.player_b.deployFleet()


game = Game()
game.setup_fleets()

# Game starts
# Player A places fleet: orientation, move with arrows
# Player B places fleet:
# Take turns taking shots
