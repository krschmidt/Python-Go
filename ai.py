import random
import functions
import copy

size = 19


def play(state):
    """
    This function receives a board state, and returns a play as a tuple (x,y)
    """
    global size
    size = len(state[0])

    #look for a capture first. This is, of course, a very bad idea.
    x, y = huntForCaptures(copy.deepcopy(state))
    if functions.inBounds(state, x, y):
        return (x, y)

    #check to see if any of our pieces are about to die:
    #also a bad plan
    for x in xrange(size):
        for y in xrange(size):
            if state[x][y] == 'w' \
                    and functions.hasLiberties(copy.deepcopy(state), x, y, False) == 1:
                if functions.inBounds(state, x - 1, y) and state[x - 1][y] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x - 1, y)
                    if valid:
                        return (x - 1, y)
                if functions.inBounds(state, x + 1, y) and state[x + 1][y] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x + 1, y)
                    if valid:
                        return (x + 1, y)
                if functions.inBounds(state, x, y - 1) and state[x][y - 1] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y - 1)
                    if valid:
                        return (x, y - 1)
                if functions.inBounds(state, x, y + 1) and state[x][y + 1] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y + 1)
                    if valid:
                        return (x, y + 1)

    #play randomly
    x = random.randint(0, size - 1)
    y = random.randint(0, size - 1)
    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y)
    counter = 0
    while not valid and counter < size * size:
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        valid, message = functions.validPlay(copy.deepcopy(state), False, x, y)
        counter += 1
    if counter >= size * size:
        # return two -1's to pass. This should be improved.
        # we don't want to only pass when there's nowhere for us to play
        return (-1, -1)
    return (x, y)


def huntForCaptures(state):
    global size

    for x in xrange(size):
        for y in xrange(size):
            if state[x][y] == 'b':
                #look each way, see if we can cap:
                valid, message = functions.validPlay(copy.deepcopy(state),
                                                     False, x - 1, y)
                if valid:
                    oldValue = state[x - 1][y]
                    state[x - 1][y] = 'w'
                    newState, posCap, pris = \
                        functions.captureHelper(copy.deepcopy(state),
                                                x - 1, y, False)
                    if posCap:
                        return (x - 1, y)
                    else:
                        state[x - 1][y] = oldValue
                valid, message = functions.validPlay(copy.deepcopy(state),
                                                     False, x + 1, y)
                if valid:
                    oldValue = state[x + 1][y]
                    state[x + 1][y] = 'w'
                    newState, posCap, pris = \
                        functions.captureHelper(copy.deepcopy(state),
                                                x + 1, y, False)
                    if posCap:
                        return (x + 1, y)
                    else:
                        state[x + 1][y] = oldValue
                valid, message = functions.validPlay(copy.deepcopy(state),
                                                     False, x, y - 1)
                if valid:
                    oldValue = state[x][y - 1]
                    state[x][y - 1] = 'w'
                    newState, posCap, pris = \
                        functions.captureHelper(copy.deepcopy(state),
                                                x, y - 1, False)
                    if posCap:
                        return (x, y - 1)
                    else:
                        state[x][y - 1] = oldValue
                valid, message = functions.validPlay(copy.deepcopy(state),
                                                     False, x, y + 1)
                if valid:
                    oldValue = state[x][y + 1]
                    state[x][y + 1] = 'w'
                    newState, posCap, pris = \
                        functions.captureHelper(copy.deepcopy(state),
                                                x, y + 1, False)
                    if posCap:
                        return (x, y + 1)
                    else:
                        state[x][y + 1] = oldValue
    return (-1, -1)
