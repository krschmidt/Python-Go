import copy
import math
#global copy of state, handy for recursing with
s = 0


def inBounds(state, x, y):
    """
    Tests if the coordinate x, y is inbounds
    """
    size = len(state[0])
    if x < 0 or y < 0:
        return False
    if x >= size or y >= size:
        return False
    return True


def validPlay(state, turn, x, y):
    """
    Determines if play is valid this way:
    if space != empty, disallow play
    if neighbor == empty, allow play
    if we can capture a neighbor, allow play
    if our play leaves us with any liberties, allow play
    else restore board state and return False
    """
    ourColor = 'b' if turn else 'w'
    size = len(state[0])
    if not inBounds(state, x, y):
        return (False, "That's out of Bounds")
    if state[x][y] != "e":
        return (False, "You need to play on an empty square")
    if x > 0 and state[x - 1][y] == "e":
        return (True, "")
    if x < size - 1 and state[x + 1][y] == "e":
        return (True, "")
    if y > 0 and state[x][y - 1] == "e":
        return (True, "")
    if y < size - 1 and state[x][y + 1] == "e":
        return (True, "")

    #assume we're going to make the play
    backup = copy.deepcopy(state)
    state[x][y] = ourColor

    #can we make a capture at this play? if yes, allow
    newState, possibleToCap, prisoners = \
        captureHelper(copy.deepcopy(state), x, y, turn)
    if possibleToCap:
        return (True, "")

    #does our group have any liberties? if yes, allow
    if hasLiberties(copy.deepcopy(state), x, y, turn):
        return (True, "")
    else:
        return (False, "That's playing into suicide!")
    print "Weird situation"


def getInfluenceMap(state):
    size = len(state[0])

    def distance(x, y, px, py):
        dis = math.sqrt((x - px) ** 2 + (y - py) ** 2)
        if state[px][py] == 'b' and dis > 0:
            return (-1 / (dis / 50))
        elif state[px][py] == 'w' and dis > 0:
            return (1 / (dis / 50))
        return 0

    influence = []
    for x in xrange(size):
        influence.append([])
        for y in xrange(size):
            influence[x].append(127.5)

    # TODO if this ever gets profiled as slow, note that we're calculating
    # a lot of things multiple times. dist from a to be gets stored at a,
    # but could also get stored at b. so n ops becomes n/2
    #loop through the influence map, calculate distance to each piece
    for x in xrange(size):
        for y in xrange(size):
            for px in xrange(size):
                for py in xrange(size):
                    influence[x][y] += distance(x, y, px, py)
    return influence


def captureHelper(state, clickedX, clickedY, turn):
    """
    Attempts to capture each adjacent square
    Consists of four if statements, each of the form:
    if you can do a capture, store the points, else roll back the capture
    """

    # then we don't need to worry about if it's posisble to make a capture,
    # becasue we're only calling it if it is possible
    size = len(state[0])
    capped = False
    target = 'w' if turn else 'b'
    prisoners = 0
    global s
    s = state

    #look left
    backupState = copy.deepcopy(s)
    if (1 <= clickedX < size) and (0 <= clickedY < size) \
            and s[clickedX - 1][clickedY] == target:
        liberties = hasLiberties(s, clickedX - 1, clickedY, not turn)
        s = copy.deepcopy(backupState)
        if not liberties:
            prisoners += capture(turn, clickedX - 1, clickedY)
        else:
            s = copy.deepcopy(backupState)
    #look right
    backupState = copy.deepcopy(s)
    if (0 <= clickedX < size - 1) and (0 <= clickedY < size) \
            and s[clickedX + 1][clickedY] == target:
        liberties = hasLiberties(s, clickedX + 1, clickedY, not turn)
        s = copy.deepcopy(backupState)
        if not liberties:
            prisoners += capture(turn, clickedX + 1, clickedY)
        else:
            s = copy.deepcopy(backupState)
    #look up
    backupState = copy.deepcopy(s)
    if (0 <= clickedX < size) and (1 <= clickedY < size) \
            and s[clickedX][clickedY - 1] == target:
        liberties = hasLiberties(s, clickedX, clickedY - 1, not turn)
        s = copy.deepcopy(backupState)
        if not liberties:
            prisoners += capture(turn, clickedX, clickedY - 1)
        else:
            s = copy.deepcopy(backupState)
    #look down
    backupState = copy.deepcopy(s)
    if (0 <= clickedX < size) and (0 <= clickedY < size - 1) \
            and s[clickedX][clickedY + 1] == target:
        liberties = hasLiberties(s, clickedX, clickedY + 1, not turn)
        s = copy.deepcopy(backupState)
        if not liberties:
                prisoners += capture(turn, clickedX, clickedY + 1)
        else:
            s = copy.deepcopy(backupState)
    possibleToCap = True if prisoners > 0 else False
    return (s, possibleToCap, prisoners)


def capture(turn, x, y):
    """
    mark captures as e, add 1 and try to cap adjascent
    """
    global s
    ourColor = 'b' if turn else 'w'
    size = len(s[0])

    #if out of bounds
    if not (0 <= x < size) or not (0 <= y < size):
        return 0
    #if we're on empty, then we've already captured this one
    elif s[x][y] == 'e':
        return 0

    #we've eliminated the possibility of us calling this function on our
    #own color when adjacent to something we clicked on (see above) so if
    #we find ourselves, then we must have reached the edge of a group
    elif s[x][y] == ourColor:
        return 0
    #The only other option is that we're on an enemy square. Mark it dead
    s[x][y] = 'e'

    #call capture, get what we need, if empty return
    return 1 + capture(turn, x + 1, y) + capture(turn, x - 1, y) \
        + capture(turn, x, y + 1) + capture(turn, x, y - 1)


def hasLiberties(state, x, y, turn):
    """
    Checks if a group at x,y has any liberties (open spaces).
    Because it marks places it's already been as the enemy, undo
    needs to be called after this function finishes
    """
    ourColor = 'b' if turn else 'w'
    size = len(state[0])

    if x < 0 or x > size - 1 or y < 0 or y > size - 1:
        return False
    if state[x][y] == "e":
        return True
    if state[x][y] != ourColor:
        return False
    #mark ourselves as the enemy, so that we don't recurse forever
    #this change must be reverted outside this function
    state[x][y] = 'w' if turn else 'b'

    return hasLiberties(state, x - 1, y, turn) or \
        hasLiberties(state, x + 1, y, turn) or \
        hasLiberties(state, x, y - 1, turn) or \
        hasLiberties(state, x, y + 1, turn)


def printBoard(self, state=None):
    """
    Helper function to print board state to console, not used in normal
    play.

    Note the default assignment of state to None. This is done so that
    we could potentially use this function to print a board other than
    this one.

    You can't simply use state=self.state, as self isn't available yet.
    """
    if state == None:
        state = self.state
    for x in xrange(self.size):
        for y in xrange(self.size):
            print state[y][x],
        print
    print
