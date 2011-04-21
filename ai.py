import random
import functions
import copy

size = 19


# TODO this doesn't ever seem to take KO into account
# TODO bug in searching for a rescue if the group is large
def play(state):
    """
    This function receives a board state, and returns a play as a tuple (x,y)
    """
    global size
    size = len(state[0])

    #look for a capture first. This is, of course, a very bad idea.
    x, y = huntForCaptures(copy.deepcopy(state))
    if functions.inBounds(state, x, y):
        print "White will capture"
        return (x, y)

    #check to see if any of our pieces are about to die:
    #also a bad plan
    for x in xrange(size):
        for y in xrange(size):
            if state[x][y] == 'w' \
                    and functions.hasLiberties(copy.deepcopy(state), x, y, False) == 1:
                if functions.inBounds(state, x - 1, y) and state[x - 1][y] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x - 1, y)
                    if valid and not playIntoAtari(copy.deepcopy(state), x - 1, y):
                        print "White tries to save"
                        return (x - 1, y)
                if functions.inBounds(state, x + 1, y) and state[x + 1][y] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x + 1, y)
                    if valid and not playIntoAtari(copy.deepcopy(state), x + 1, y):
                        print "White tries to save"
                        return (x + 1, y)
                if functions.inBounds(state, x, y - 1) and state[x][y - 1] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y - 1)
                    if valid and not playIntoAtari(copy.deepcopy(state), x, y - 1):
                        print "White tries to save"
                        return (x, y - 1)
                if functions.inBounds(state, x, y + 1) and state[x][y + 1] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y + 1)
                    if valid and not playIntoAtari(copy.deepcopy(state), x, y + 1):
                        print "White tries to save"
                        return (x, y + 1)

    #check to see if any of black's groups only have 2 liberties. If so, play to set up atari
    for x in xrange(size):
        for y in xrange(size):
            if state[x][y] == 'b' \
                    and functions.hasLiberties(copy.deepcopy(state), x, y, True) == 2:
                if functions.inBounds(state, x - 1, y) and state[x - 1][y] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x - 1, y)
                    if valid and not playIntoAtari(copy.deepcopy(state), x - 1, y):
                        print "White sets up atari"
                        return (x - 1, y)
                if functions.inBounds(state, x + 1, y) and state[x + 1][y] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x + 1, y)
                    if valid and not playIntoAtari(copy.deepcopy(state), x + 1, y):
                        print "White sets up atari"
                        return (x + 1, y)
                if functions.inBounds(state, x, y - 1) and state[x][y - 1] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y - 1)
                    if valid and not playIntoAtari(copy.deepcopy(state), x, y - 1):
                        print "White sets up atari"
                        return (x, y - 1)
                if functions.inBounds(state, x, y + 1) and state[x][y + 1] == 'e':
                    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y + 1)
                    if valid and not playIntoAtari(copy.deepcopy(state), x, y + 1):
                        print "White sets up atari"
                        return (x, y + 1)

    #find spot least influenced by anyone that is also at least two from the edge?
    cx = -1
    cy = -1
    c = 5000
    infMap = functions.getInfluenceMap(copy.deepcopy(state))

    for x in xrange(2, size - 2):
        for y in xrange(2, size - 2):
            valid, message = functions.validPlay(copy.deepcopy(state), False, x, y)
            if valid and abs(infMap[x][y] - 128) < c \
                    and not inAnEye(copy.deepcopy(state), x, y) \
                    and not playIntoAtari(copy.deepcopy(state), x, y):
                cx = x
                cy = y
                c = abs(infMap[x][y] - 128)
    if cx != -1 and cy != -1:
        print "White attemps to influence the most neutral area"
        return (cx, cy)

    #see which play maximizes the amount of influence we have on the board
    #three temp variables to keep track of what is best

    #since that'll obviously increase average fitness the most.
    #maybe if len(stateHistory) < 5 then we should try to maximize our distance from ourselves
    #while still being at least 2 from the edge?
    bx = -1
    by = -1
    best = 0
    infMap = functions.getInfluenceMap(copy.deepcopy(state))
    curInf = sum(map(sum, zip(*infMap))) / (size * size)
    for x in xrange(size):
        for y in xrange(size):
            if state[x][y] == 'w':
                pass
            elif state[x][y] == 'e':
                valid, message = functions.validPlay(copy.deepcopy(state), False, x, y)
                if valid:
                    if not inAnEye(copy.deepcopy(state), x, y) and not playIntoAtari(copy.deepcopy(state), x, y):
                        backup = copy.deepcopy(state)
                        backup[x][y] = 'w'
                        infMap = functions.getInfluenceMap(backup)
                        #find average influence
                        avgInf = sum(map(sum, zip(*infMap))) / (size * size)
                        if avgInf > best:
                            best = avgInf
                            bx = x
                            by = y
    #calculate an existing influence level first? only play if we improve by a ranodm maount?
    if bx != -1 and by != -1:
        print "white tries to maximize influence"
        return (bx, by)

    #play randomly
    x = random.randint(0, size - 1)
    y = random.randint(0, size - 1)
    valid, message = functions.validPlay(copy.deepcopy(state), False, x, y)
    counter = 0
    #TODO fix this counter crap. Maintain a list of locations? Remove every play?
    while (not valid or inAnEye(copy.deepcopy(state), x, y) \
            or playIntoAtari(copy.deepcopy(state), x, y)) \
            and counter < size * size * 3:
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        valid, message = functions.validPlay(copy.deepcopy(state), False, x, y)
        counter += 1
    if counter >= size * size * 3:
        # return two -1's to pass. This should be improved.
        # we don't want to only pass when there's nowhere for us to play
        print "white passes"
        return (-1, -1)
    print "white plays randomly"
    return (x, y)


def playIntoAtari(state, x, y):
    state[x][y] = 'w'
    if functions.hasLiberties(copy.deepcopy(state), x, y, False) == 1:
        return True
    return False

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

def inAnEye(state, x, y):
    """
    returns True if x, y is inside of an eye.
    Useful becuase we probably don't want to play there if this is true
    TODO we'll also probably want to modify this, because it doesn't take into
    account double eyes
    """
    if not functions.inBounds(state, x, y):
        return True
    if state[x][y] == 'b':
        return False
    if state[x][y] == 'w':
        return True
    if state[x][y] == 'x':
        #we've already looked here
        return True
    if state[x][y] == 'e':
        state[x][y] = 'x'
        return inAnEye(state, x - 1, y) and \
            inAnEye(state, x + 1, y) and \
            inAnEye(state, x, y - 1) and \
            inAnEye(state, x, y + 1)
