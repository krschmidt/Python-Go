# TODO support marking dead stones after both players pass
from functions import *
from Tkinter import *
import copy
import ai


class App():
    def __init__(self, master):
        """
        Creates the initial window. Note that the board isn't created here,
        instead that happens in resize(), which is called any time the window
        size changes (including it's initial creation)
        """
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New",
                             command=lambda: self.confirm(self.reset))
        filemenu.add_command(label="Quit", command=self.quit)

        playermenu = Menu(menubar, tearoff=0)
        playermenu.add_command(label="Pass", command=self.playerpass)
        playermenu.add_command(label="Undo", command=self.undo)
        playermenu.add_separator()
        playermenu.add_checkbutton(label="Play against Computer (Beta)",
                                   command=lambda:
                                   self.confirm(self.setComputer))

        boardmenu = Menu(menubar, tearoff=0)
        handicapmenu = Menu(boardmenu, tearoff=0)
        handicapmenu.add_command(label="0",
                                 command=lambda: self.confirm(self.reset))
        for i in xrange(1, 10):
            handicapmenu.add_command(label=i,
                                     command=lambda x=i:
                                     self.confirm(self.handicap, x))

        sizeMenu = Menu(boardmenu, tearoff=0)
        sizeMenu.add_command(label="9",
                             command=lambda x=9:
                             self.confirm(self.setSize, 9))
        sizeMenu.add_command(label="13",
                             command=lambda x=9:
                             self.confirm(self.setSize, 13))
        sizeMenu.add_command(label="19",
                             command=lambda x=9:
                             self.confirm(self.setSize, 19))

        boardmenu.add_cascade(label="Handicap", menu=handicapmenu)
        boardmenu.add_cascade(label="Size", menu=sizeMenu)
        boardmenu.add_separator()
        boardmenu.add_checkbutton(label="Influence Map",
                              command=self.infHelp)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Player", menu=playermenu)
        menubar.add_cascade(label="Board", menu=boardmenu)
        master.config(menu=menubar)

        self.statusbar = Frame(master)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.score = Label(self.statusbar, text="B: 0 W: 0")
        self.score.pack(side=LEFT)
        self.status = Label(self.statusbar, text="", bd=1)
        self.status.pack(side=RIGHT, fill=X)
        self.c = Canvas(master, width=570, height=570)
        self.c.pack(side=TOP, fill=BOTH, expand=YES)
        self.c.bind('<Configure>', self.resize)
        self.c.bind('<Button-1>', self.click)
        self.c.bind('<Button-3>', self.undo)

        #Make turn black
        self.turn = True

        self.passCount = 0
        self.wPrisoners = 0
        self.bPrisoners = 0
        self.influence = False
        self.size = 19
        self.playComputer = False

        #used for noting most recent piece
        self.lastX = None
        self.lastY = None

        self.state = []
        for x in xrange(self.size):
            self.state.append([])
            for y in xrange(self.size):
                self.state[x].append("e")

        #Used for Undo
        self.stateHistory = []
        self.stateHistory.append({'state': copy.deepcopy(self.state),
                                  'pass': self.passCount,
                                  'wPrisoners': self.wPrisoners,
                                  'bPrisoners': self.bPrisoners,
                                  'turn': self.turn,
                                  'lastX': None,
                                  'lastY': None})

    def setComputer(self):
        self.playComputer = not self.playComputer
        self.reset()

    def setSize(self, size):
        self.size = size
        self.reset()

    def infHelp(self):
        """ Turns influence on/off, redraws board """
        self.influence = not self.influence
        self.resize()

    def confirm(self, function, arg=None):
        """
        Presents the user with a confirm dialog if board isn't empty
        """
        foundSomeone = False
        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.state[x][y] != 'e':
                    foundSomeone = True
        if not foundSomeone:
            if arg is None:
                function()
            else:
                function(arg)
            return

        #board has someone
        self.confirmW = Toplevel()
        self.confirmW.title("Sure?")
        msg = Message(self.confirmW,
            text="Are you sure?\nThat will end the current game!",
            width=200)
        msg.pack()
        YesB = Button(self.confirmW, text="Yes", \
            command=lambda: self.doAndClose(function, arg))
        YesB.pack(side=LEFT)
        NoB = Button(self.confirmW, text="No", command=self.confirmW.destroy)
        NoB.pack(side=RIGHT)

    def doAndClose(self, function, arg=None):
        """
        Helper function for confirm() executes function and closes confirmW
        """
        if arg is None:
            function()
        else:
            function(arg)
        self.confirmW.destroy()

    def resize(self, event=None):
        """ Create/Resize the Board """
        self.c.delete(ALL)
        w = root.winfo_width()
        h = root.winfo_height()

        #Prevents an error - if h or w gets too small, there's an exception
        #raised when we try to pass 0 as a step to xrange. 42 is pretty
        #arbitrary, but if it's 42x42, you can't see the pieces anyway.
        if w < 42 or h < 42:
            return

        self.wf = w / self.size
        #-1 lets the statusbar label fit on the bottom w/o overflowing
        #Leaving 19 - 1 in here for when we add a board size parameter
        self.hf = h / self.size - 1

        #board background
        self.c.create_rectangle(0, 0, w, h, fill="#f2b06d")

        if self.influence:
            influences = getInfluenceMap(self.state)

            #draw influence rectangles across the board
            for x in xrange(self.size):
                for y in xrange(self.size):
                    if influences[x][y] > 255:
                        influences[x][y] = 255
                    elif influences[x][y] < 0:
                        influences[x][y] = 0
                    rgb = 128, int(influences[x][y]), int(influences[x][y])
                    hex = '#%02x%02x%02x' % rgb
                    self.c.create_rectangle(self.wf * x, self.hf * y,
                                            self.wf * (x + 1),
                                            self.hf * (y + 1),
                                            fill=hex, outline="")

        for x in xrange(self.wf / 2, self.size * self.wf, self.wf):
            self.c.create_line(x, self.hf / 2, x,
                               (self.hf / 2) + self.hf * (self.size - 1))
        for y in xrange(self.hf / 2, self.size * self.hf, self.hf):
            self.c.create_line(self.wf / 2, y,
                               (self.wf / 2) + self.wf * (self.size - 1), y)

        #Draw little dots on the powerful plays
        #TODO Adjust so the dots don't get too tiny in small windows
        if self.size == 19:
            for x in xrange((self.wf / 2) + (3 * self.wf),
                            self.size * self.wf, self.wf * 6):
                for y in xrange((self.hf / 2) + (3 * self.hf),
                                self.size * self.hf, self.hf * 6):
                    self.c.create_oval(x - 3, y - 3,
                                       x + 3, y + 3, fill="black")
        elif self.size == 13:
            for x in xrange((self.wf / 2) + (3 * self.wf),
                            (self.size - 1) * self.wf, self.wf * 3):
                for y in xrange((self.hf / 2) + (3 * self.hf),
                                (self.size - 1) * self.hf, self.hf * 3):
                    self.c.create_oval(x - 3, y - 3,
                                       x + 3, y + 3, fill="black")
        elif self.size == 9:
            for x in xrange((self.wf / 2) + (2 * self.wf),
                            (self.size - 1) * self.wf, self.wf * 2):
                for y in xrange((self.hf / 2) + (2 * self.hf),
                                (self.size - 1) * self.hf, self.hf * 2):
                    self.c.create_oval(x - 3, y - 3,
                                       x + 3, y + 3, fill="black")
        #redraw the actual pieces
        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.state[x][y] == "b":
                    self.c.create_oval(self.wf * (x), self.hf * (y),
                                       self.wf * (x + 1), self.hf * (y + 1),
                                       fill="black", outline="white")
                elif self.state[x][y] == "w":
                    self.c.create_oval(self.wf * (x), self.hf * (y),
                                       self.wf * (x + 1), self.hf * (y + 1),
                                       fill="white", outline="black")

        #Draw a red square around the most recent piece
        if self.lastX != None and self.lastY != None:
            xStart = (self.lastX * self.wf) + (0.2 * self.wf)
            yStart = (self.lastY * self.hf) + (0.2 * self.hf)
            self.c.create_rectangle(xStart, yStart,
                                    (.6 * self.wf) + xStart,
                                    (.6 * self.hf) + yStart,
                                    outline="red")

    def handicap(self, number):
        """
        Adds up to 9 handicap stones
        """
        self.reset()
        if self.size == 19:
            self.state[15][3] = 'b'
            if number == 5 or number == 7 or number == 9:
                self.state[9][9] = 'b'
            if number > 1:
                self.state[3][15] = 'b'
            if number > 2:
                self.state[15][15] = 'b'
            if number > 3:
                self.state[3][3] = 'b'
            if number > 5:
                self.state[3][9] = 'b'
                self.state[15][9] = 'b'
            if number > 7:
                self.state[9][3] = 'b'
                self.state[9][15] = 'b'

        elif self.size == 13:
            self.state[9][3] = 'b'
            if number == 5 or number == 7 or number == 9:
                self.state[6][6] = 'b'
            if number > 1:
                self.state[3][9] = 'b'
            if number > 2:
                self.state[9][9] = 'b'
            if number > 3:
                self.state[3][3] = 'b'
            if number > 5:
                self.state[3][6] = 'b'
                self.state[9][6] = 'b'
            if number > 7:
                self.state[6][3] = 'b'
                self.state[6][9] = 'b'

        elif self.size == 9:
            self.state[6][2] = 'b'
            if number == 5 or number == 7 or number == 9:
                self.state[4][4] = 'b'
            if number > 1:
                self.state[2][6] = 'b'
            if number > 2:
                self.state[6][6] = 'b'
            if number > 3:
                self.state[2][2] = 'b'
            if number > 5:
                self.state[2][4] = 'b'
                self.state[6][4] = 'b'
            if number > 7:
                self.state[4][2] = 'b'
                self.state[4][6] = 'b'

        self.resize()

    def undo(self, event=None):
        """
        Undo most recent move by popping last player's state and restoring it
        Resize (redraw) the board

        event defaults to None so that this function can be used either with
        the right click event or with the undo menu item
        """
        if len(self.stateHistory) <= 1:
            self.status.config(text="You can't undo! \
                There's nothing on the board!")
            return
        self.stateHistory.pop()
        if self.playComputer:
            self.stateHistory.pop()
        last = copy.deepcopy(self.stateHistory[len(self.stateHistory) - 1])
        self.state = last['state']
        self.turn = last['turn']
        self.passCount = last['pass']
        self.wPrisoners = last['wPrisoners']
        self.bPrisoners = last['bPrisoners']
        self.lastX = last['lastX']
        self.lastY = last['lastY']
        self.score.config(text="B: %d W: %d"
            % (self.bPrisoners, self.wPrisoners))
        self.resize()

    def click(self, event=None, cx=None, cy=None):
        """
        Handles normal play
        Verifies that play is allowable
        Makes any possible captures
        Checks for Ko rule. This is not done in ValidPlay(), as we've got
        to make captures first, and there's no real reason to do that twice.
        Finish by redrawing board
        """
        self.status.config(text="")

        if event == None:
            stateX = cx
            stateY = cy
        else:
            #figure out what square we clicked on
            x = (event.x + self.wf) - event.x % self.wf
            y = (event.y + self.hf) - event.y % self.hf
            stateX = event.x / self.wf
            stateY = event.y / self.hf

        possible, message = validPlay(copy.deepcopy(self.state),
                                      self.turn, stateX, stateY)
        self.status.config(text=message)
        if not possible:
            return False

        backup = copy.deepcopy(self.state)
        self.state[stateX][stateY] = 'b' if self.turn else 'w'

        #check for captures
        #store existing prisoners in case we need to roll back
        preb = self.bPrisoners
        prew = self.wPrisoners
        newState, possible, captures = captureHelper(copy.deepcopy(self.state),
                                                     stateX, stateY, self.turn)
        if possible:
            self.state = copy.deepcopy(newState)
            if self.turn:
                self.bPrisoners += captures
            else:
                self.wPrisoners += captures
        self.score.config(text="B: %d W: %d" \
                              % (self.bPrisoners, self.wPrisoners))

        #Check for ko
        if self.state == \
                self.stateHistory[len(self.stateHistory) - 2]['state']:
            self.state = copy.deepcopy(backup)
            self.bPrisoners = preb
            self.wPrisoners = prew
            self.score.config(text="B: %d W: %d" \
                % (self.bPrisoners, self.wPrisoners))
            self.status.config(text="That would be a violation of Ko")
            return False

        self.turn = not self.turn
        self.lastX = stateX
        self.lastY = stateY
        self.stateHistory.append({'state': copy.deepcopy(self.state),
                                  'pass': self.passCount,
                                  'wPrisoners': self.wPrisoners,
                                  'bPrisoners': self.bPrisoners,
                                  'turn': self.turn,
                                  'lastX': stateX,
                                  'lastY': stateY})
        #reset passcount - they'll need to pass twice in a row in order to end
        self.passCount = 0

        #redraw board
        self.resize()
        root.update()

        #if it's whites turn, then do ai stuff
        if not self.turn and self.playComputer:
            stateX, stateY = ai.play(copy.deepcopy(self.state))
            if stateX == -1 and stateY == -1:
                self.playerpass()
            else:
                self.click(None, stateX, stateY)

    def playerpass(self):
        """
        Allows a player to pass. If both players pass, ends the game
        """
        if self.passCount == 0:
            self.passCount += 1
            if self.turn:
                self.status.config(text="Black passes!")
            else:
                self.status.config(text="White passes!")
            self.turn = not self.turn
            if not self.turn and self.playComputer:
                #black passed, so white needs to know to go
                stateX, stateY = ai.play(copy.deepcopy(self.state))
                if stateX == -1 and stateY == -1:
                    self.playerpass()
                else:
                    self.click(None, stateX, stateY)

        else:
            self.status.config(text="Game Over!")
            self.findscore()

    def quit(self):
        """ Destorys the root window, and terminates the program """
        global root
        root.destroy()

    def reset(self):
        """ Resets the program, giving us a new game """
        self.status.config(text="")
        self.turn = True
        self.passCount = 0
        self.wPrisoners = 0
        self.bPrisoners = 0
        self.lastX = None
        self.lastY = None

        self.state = []
        for x in xrange(self.size):
            self.state.append([])
            for y in xrange(self.size):
                self.state[x].append("e")
        self.stateHistory = []
        self.stateHistory.append({'state': copy.deepcopy(self.state),
                                  'pass': self.passCount,
                                  'wPrisoners': self.wPrisoners,
                                  'bPrisoners': self.bPrisoners,
                                  'turn': self.turn,
                                  'lastX': None,
                                  'lastY': None})
        self.resize()
        #Error generated if user calls redo from the menu
        try:
            self.top.destroy()
        except AttributeError:
            pass

    def findscore(self):
        """
        Scores the game, creates a topLevel window to notify players of score

        First checks that there's more than one piece on the board, to
        avoid awarding all points to black (the first player)
        Fills in each empty space with p's by calling checkScore() on
        those coordinates.
        After checkScore() has returned, converts p's to the capital
        version of the point's owner, so that we won't call checkScore()
        multiple times for each area we score
        Finally counts all the capital letters (points) and creates a
        TopLevel window for the player to see
        """
        anything = 0
        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.state[x][y] != 'e':
                    anything += 1
        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.state[x][y] != 'e':
                    continue
                self.lastfound = ''
                backup = copy.deepcopy(self.state)
                if not self.checkScore(x, y):
                    #it was neutral, restore the backup to get rid of p's
                    self.state = copy.deepcopy(backup)
                else:
                    #go through board, filling in p's with the capital
                    #letter of the point's owner
                    #we'll count these later
                    for a in xrange(self.size):
                        for b in xrange(self.size):
                            if self.lastfound == 'w':
                                point = 'W'
                            else:
                                point = 'B'
                            if self.state[a][b] == 'p':
                                self.state[a][b] = point
        #Now we're all done checking points. So print scores
        wTerr = 0
        bTerr = 0
        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.state[x][y] == 'W':
                    wTerr += 1
                elif self.state[x][y] == 'B':
                    bTerr += 1
        self.top = Toplevel()
        self.top.title("Game Over!")
        #If there was nothing in our original board, we reset territories
        #to 0, as otherwise it's all points for black
        if anything <= 1:
            wTerr = 0
            bTerr = 0
        #TODO add Komi stuff here
        if wTerr + self.wPrisoners > bTerr + self.bPrisoners:
            winner = "White"
        elif wTerr + self.wPrisoners < bTerr + self.bPrisoners:
            winner = "Black"
        else:
            winner = "Draw"
        msg = Message(self.top, text="White\n\tTerritory: %d\n\
          \tPrisoners:%d\nBlack\n\tTerritory: %d\n\tPrisoners:%d\n\
          Final:\nWhite: %d \tBlack:%d\nWinner: %s" \
          % (wTerr, self.wPrisoners, bTerr, self.bPrisoners, \
          wTerr + self.wPrisoners, bTerr + self.bPrisoners, winner))
        msg.pack()
        quitB = Button(self.top, text="Quit", command=self.quit)
        quitB.pack(side=LEFT)
        resetB = Button(self.top, text="Again", command=self.reset)
        resetB.pack(side=RIGHT)

    def checkScore(self, x, y):
        """
        Searches x,y to fill all adjacent squares with p's. Returns false
        if it finds a place where black and white both border empty squares
        (that territory should be neutral and not scored)
        """
        if not (0 <= x < self.size) or not (0 <= y < self.size):
            return True
        if self.state[x][y] == 'p':
            return True
        elif self.state[x][y] != 'e':
            #we need to see if our cur last found == our last one.
            #if no, then this is neutral territory
            if self.lastfound != '' and self.lastfound != self.state[x][y]:
                return False
            else:
                self.lastfound = self.state[x][y]
                return True
        self.state[x][y] = 'p'
        if not self.checkScore(x - 1, y):
            return False
        if not self.checkScore(x + 1, y):
            return False
        if not self.checkScore(x, y - 1):
            return False
        if not self.checkScore(x, y + 1):
            return False
        return True

if __name__ == '__main__':
    root = Tk()
    root.title("Tk Go!")
    myapp = App(root)
    root.mainloop()
