import random


def play(state):
    """
    This function receives a board state, and returns a play as a tuple (x,y)
    """

    x = random.randint(0, len(state[0]) - 1)
    y = random.randint(0, len(state[0]) - 1)
    while state[x][y] != 'e':
        x = random.randint(0, len(state[0]) - 1)
        y = random.randint(0, len(state[0]) - 1)
    return (x, y)
