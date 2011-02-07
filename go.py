# TODO support board sizes other than 19
# TODO support marking dead stones after both players pass
# TODO add handicaps
# TODO add an indicator of last play

from Tkinter import *
import copy

class App():
    def __init__(self,master):
        """
        Creates the initial window. Note that the board isn't created here,
        instead that happens in resize(), which is called any time the window
        size changes (including it's initial creation)
        """
        menubar = Menu(master)
        filemenu = Menu(menubar,tearoff=0)
        filemenu.add_command(label="Quit",command=self.quit)
        playermenu = Menu(menubar,tearoff=0)
        playermenu.add_command(label="Pass",command=self.playerpass)
        playermenu.add_command(label="Undo",command=self.undo)
        menubar.add_cascade(label="File",menu=filemenu)
        menubar.add_cascade(label="Player",menu=playermenu)
        master.config(menu=menubar)        

        self.statusbar = Frame(master)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.score = Label(self.statusbar,text="B: 0 W: 0")
        self.score.pack(side=LEFT)
        self.status = Label(self.statusbar, text="", bd=1)
        self.status.pack(side=RIGHT, fill=X)
        self.c=Canvas(master,width=570,height=570)
        self.c.pack(side=TOP,fill=BOTH,expand=YES)

        self.c.bind('<Configure>',self.resize)

        self.c.bind('<Button-1>',self.click)
        self.c.bind('<Button-3>',self.undo)

        #Make turn black
        self.turn = True

        self.passCount = 0
        self.wPrisoners = 0
        self.bPrisoners = 0

        self.state = []
        for x in xrange(19):
            self.state.append([])
            for y in xrange(19):
                self.state[x].append("E")

        #Used for Undo
        self.stateHistory = []
        self.stateHistory.append({'state':copy.deepcopy(self.state),
                                  'pass':self.passCount, 
                                  'wPrisoners':self.wPrisoners,
                                  'bPrisoners':self.bPrisoners,
                                  'turn':self.turn})

    def printBoard(self,state=None):
        """ 
        Helper function to print board state to console, not used in normal play 
        
        Note the default assignment of state to None. This is done so that
        we could potentially use this function to print a board other than this one.
        You can't simply use state=self.state, as self isn't available yet.
        """
        if state == None:
            state = self.state
        for x in xrange(19):
            for y in xrange(19):
                print state[y][x],
            print
        print

    def resize(self,event=None):
        """ Create/Resize the Board """
        self.c.delete(ALL)
        w=root.winfo_width()
        h=root.winfo_height()

        #Prevents an error - if h or w gets too small, there's an exception raised when we try to pass 0 as a step to xrange
        #42 is pretty arbitrary, but if it's 42x42, you can't really see the pieces anyway...
        if w<42 or h<42:
            return
        self.wf = w/19
        self.hf=h/19-1  #-1 lets us fit the statusbar label on the bottom w/o overflowing onto it
        self.c.create_rectangle(0,0,w,h,fill="#f2b06d")
        for x in xrange(self.wf/2,19*self.wf,self.wf):
            self.c.create_line(x,self.hf/2,x,(self.hf/2)+self.hf*18)
        for y in xrange(self.hf/2,19*self.hf,self.hf):
            self.c.create_line(self.wf/2,y,(self.wf/2)+self.wf*18,y)
        #Draw little dots on the powerful plays
        #TODO this should probably be adjusted so that these dots don't get unnaturally tiny at small screen sizes
        for x in xrange((self.wf/2)+(3*self.wf),19*self.wf,self.wf*6):
            for y in xrange((self.hf/2)+(3*self.hf),19*self.hf,self.hf*6):
                self.c.create_oval(x-3,y-3,x+3,y+3,fill="black")

        #redraw the actual pieces
        for x in xrange(19):
            for y in xrange(19):
                if self.state[x][y] == "b":
                    self.c.create_oval(self.wf*(x),self.hf*(y),self.wf*(x+1),self.hf*(y+1),fill="black",outline="white")

                elif self.state[x][y] == "w":
                    self.c.create_oval(self.wf*(x),self.hf*(y),self.wf*(x+1),self.hf*(y+1),fill="white",outline="black")

    def undo(self,event=None):
        """ 
        Undo most recent move by popping last player's state and restoring it
        Resize (redraw) the board

        event defaults to None so that this function can be used either with the right click event or with the undo menu item
        """
        if len(self.stateHistory) <= 1:
            self.status.config(text="You can't undo! There's nothing on the board!")
            return

        self.stateHistory.pop()
        last = copy.deepcopy(self.stateHistory[len(self.stateHistory)-1])
        self.state = last['state']
        self.turn = last['turn']
        self.passCount = last['pass']
        self.wPrisoners = last['wPrisoners']
        self.bPrisoners = last['bPrisoners']
        self.score.config(text="B: %d W: %d" % (self.bPrisoners, self.wPrisoners))
        self.resize()
    def validPlay(self,x,y):
        """ 
        Determines if play is valid this way:
        if space != empty, disallow play
        if neighbor == empty, allow play
        if we can capture a neighbor, allow play
        if our play leaves us with any liberties, allow play
        else restore board state and return False
        """
        ourColor = 'b' if self.turn else 'w'

        if self.state[x][y] != "E":
            self.status.config(text="You need to play on an empty square")
            return False

        if x>0 and self.state[x-1][y]=="E":
            return True
        if x<18 and self.state[x+1][y]=="E":
            return True
        if y>0 and self.state[x][y-1]=="E":
            return True
        if y<18 and self.state[x][y+1]=="E":
            return True

        #assume we're going to make the play
        backup = copy.deepcopy(self.state)
        self.state[x][y] = ourColor

        #can we make a capture at this play? if yes, allow
        if self.captureHelper(x,y,self.turn):
            self.state = copy.deepcopy(backup)
            return True

        #does our group have any liberties? if yes, allow
        if self.hasLiberties(x,y,self.turn):
            self.state = copy.deepcopy(backup)
            return True
        
        self.status.config(text="That's playing into suicide!")
        self.state = copy.deepcopy(backup)
        return False

    def hasLiberties(self,x,y,turn):
        """
        Checks if a group at x,y has any liberties (open spaces).
        Because it marks places it's already been as the enemy, undo needs to be called after this function finishes
        """
        ourColor = 'b' if turn else 'w'

        if x<0 or x>18 or y<0 or y>18:
            return False
        if self.state[x][y] == "E":
            return True
        if self.state[x][y] != ourColor:
            return False
        #mark ourselves as the enemy, so that we don't recurse forever
        #this change must be reverted outside this function
        self.state[x][y] = 'w' if turn else 'b'

        return self.hasLiberties(x-1,y,turn) or self.hasLiberties(x+1,y,turn) or self.hasLiberties(x,y-1,turn) or self.hasLiberties(x,y+1,turn)

    def click(self,event):
        """Handles normal play"""
        self.status.config(text="")

        #figure out what square we clicked on
        x = (event.x+self.wf)- event.x%self.wf
        y = (event.y+self.hf)- event.y%self.hf
        stateX = event.x/self.wf
        stateY = event.y/self.hf
        
        if not self.validPlay(stateX,stateY):
            return False

        backup = copy.deepcopy(self.state)
        self.state[stateX][stateY] = 'b' if self.turn else 'w'

        #check for captures
        self.captureHelper(stateX,stateY,self.turn)
        preb = self.bPrisoners
        prew = self.wPrisoners

        #Check for ko
        if self.state == self.stateHistory[len(self.stateHistory)-2]['state']:
            self.state = copy.deepcopy(backup)
            self.bPrisoners = preb
            self.wPrisoners = prew
            self.score.config(text="B: %d W: %d" % (self.bPrisoners, self.wPrisoners))
            self.status.config(text="That would be a violation of Ko")
            return False
        self.turn = not self.turn
        self.stateHistory.append({'state':copy.deepcopy(self.state),'pass':self.passCount,\
                                      'wPrisoners':self.wPrisoners,'bPrisoners':self.bPrisoners,'turn':self.turn})
        #reset passcount, as they'll need to pass twice in a row in order to end
        self.passCount=0
        self.resize()
        
    def captureHelper(self,clickedX,clickedY,turn):
        #Checks to see if turn is making a capture through this play
        capped = False
        if turn:
            target = 'w'
        else:
            target = 'b'
        backupState = copy.deepcopy(self.state)
        self.curCaps =0

        if (1<=clickedX<19) and (0<=clickedY<19) and self.state[clickedX-1][clickedY] == target \
                and self.capture(clickedX-1,clickedY):
            capped = True
            if target =='w':
                self.bPrisoners+=self.curCaps
            else:
                self.wPrisoners+=self.curCaps
        else:
            self.state = copy.deepcopy(backupState)
        self.curCaps =0

        backupState = copy.deepcopy(self.state)

        if (0<=clickedX<18) and (0<=clickedY<19) and self.state[clickedX+1][clickedY] == target \
                and self.capture(clickedX+1,clickedY):
            capped = True
            if target=='w':
                self.bPrisoners+=self.curCaps
            else:
                self.wPrisoners+=self.curCaps
        else:
            self.state = copy.deepcopy(backupState)
        self.curCaps =0
        backupState = copy.deepcopy(self.state)

        if (0<=clickedX<19) and (1<=clickedY<19) and self.state[clickedX][clickedY-1] == target \
                and self.capture(clickedX,clickedY-1):
            capped = True
            if target=='w':
                self.bPrisoners+=self.curCaps
            else:
                self.wPrisoners+=self.curCaps
        else:
            self.state = copy.deepcopy(backupState)
        self.curCaps =0
        backupState = copy.deepcopy(self.state)

        if (0<=clickedX<19) and (0<=clickedY<18) and self.state[clickedX][clickedY+1] == target \
                and self.capture(clickedX,clickedY+1):
            capped = True
            if target=='w':
                self.bPrisoners+=self.curCaps
            else:
                self.wPrisoners+=self.curCaps
        else:
            self.state = copy.deepcopy(backupState)
        self.curCaps =0
        self.score.config(text="B: %d W: %d" % (self.bPrisoners,self.wPrisoners))

        #get rid of all those c's we set up back when we were capturing
        for x in xrange(19):
            for y in xrange(19):
                if self.state[x][y] == 'c':
                    self.state[x][y] = "E"
        return capped


    def capture(self,x,y):
        if self.turn:
            ourColor = 'b'
        else:
            ourColor = 'w'
        if not (0<=x<19) or not (0<=y<19):
            return True
        elif self.state[x][y] == 'E':
            return False
        #we've eliminated the possibility of us calling this function on our own color when adjascent to 
        #something we clicked on (see above) so if we find ourselves, then we must have reached the edge of a group
        elif self.state[x][y] == ourColor:
            return True
        elif self.state[x][y] == 'c':
            return True
        #Presumibly the only other option is for us to be on the enemy's square. Try marking it dead.
        self.state[x][y] = 'c'
        self.curCaps+=1
        if not self.capture(x-1,y):
            return False
        if not self.capture(x+1,y):
            return False
        if not self.capture(x,y+1):
            return False
        if not self.capture(x,y-1):
            return False
        return True
        
    def playerpass(self):
        if self.passCount == 0:
            self.passCount+=1
            if self.turn:
                self.status.config(text="Black passes!")
            else:
                self.status.config(text="White passes!")
            self.turn = not self.turn
        else:
            self.status.config(text="Game Over!")
            self.findscore()

    def quit(self):
        global root
        root.destroy()

    def reset(self):
        self.status.config(text="")
        self.turn = True
        self.passCount = 0
        self.wPrisoners = 0
        self.bPrisoners = 0

        self.state = []
        for x in xrange(19):
            self.state.append([])
            for y in xrange(19):
                self.state[x].append("E")
        self.stateHistory = []
        self.stateHistory.append({'state':copy.deepcopy(self.state),'pass':self.passCount,\
                                      'wPrisoners':self.wPrisoners,'bPrisoners':self.bPrisoners,'turn':self.turn})
        self.resize()
        self.top.destroy()

    #Scoring function
    def findscore(self):
        #See if there's more than one piece on the board
        #otherwise when we look for points, we'll automatically award all points to black
        #if no one else has played, or if there's only one piece on the board, we'll award to that piece
        anything = 0
        for x in xrange(19):
            for y in xrange(19):
                if self.state[x][y] != 'E':
                    anything+=1
            
        for x in xrange(19):
            for y in xrange(19):
                if self.state[x][y] != 'E':
                    continue
                self.lastfound = ''
                backup = copy.deepcopy(self.state)
                if not self.checkScore(x,y):
                    #then it was all neutral, so restore the backup to get rid of p's
                    self.state = copy.deepcopy(backup)
                else:
                    self.printBoard()
                    for a in xrange(19):
                        for b in xrange(19):
                            if self.lastfound == 'w':
                                point = 'W'
                            else:
                                point = 'B'
                            if self.state[a][b] == 'p':
                                self.state[a][b] = point
        #Now we're all done checking points. So print scores
        wTerr =0
        bTerr =0
        for x in xrange(19):
            for y in xrange(19):
                if self.state[x][y] == 'W':
                    wTerr+=1
                elif self.state[x][y] == 'B':
                    bTerr+=1
        self.top = Toplevel()
        self.top.title("Game Over!")
        #If there was nothing in our original board, we reset territories to 0, as otherwise it's all points for black
        if anything <=1:
            wTerr =0
            bTerr =0
        #TODO add Komi stuff here
        if wTerr+self.wPrisoners > bTerr+self.bPrisoners:
            winner= "White"
        elif wTerr+self.wPrisoners < bTerr+self.bPrisoners:
            winner="Black"
        else:
            winner="Draw"
        msg = Message(self.top, text= "White\n\tTerritory: %d\n\tPrisoners:%d\nBlack\n\tTerritory: %d\n\tPrisoners:%d\nFinal:\nWhite: %d \tBlack:%d\nWinner: %s" %(wTerr,self.wPrisoners,bTerr,self.bPrisoners,wTerr+self.wPrisoners,bTerr+self.bPrisoners,winner))
        msg.pack()
        quitB = Button(self.top, text="Quit", command=self.quit)
        quitB.pack(side=LEFT)
        resetB = Button(self.top, text="Again", command=self.reset)
        resetB.pack(side=RIGHT)

    def checkScore(self,x,y):
        if not (0<=x<19) or not (0<=y<19):
            return True
        if self.state[x][y] == 'p':
            return True
        elif self.state[x][y] != 'E':
            #we need to see if our cur last found == our last one. if no, then this is neutral territory
            if self.lastfound !='' and self.lastfound!=self.state[x][y]:
                return False
            else:
                self.lastfound=self.state[x][y]
                return True
        self.state[x][y] = 'p'
        if not self.checkScore(x-1,y):
            return False
        if not self.checkScore(x+1,y):
            return False
        if not self.checkScore(x,y-1):
            return False
        if not self.checkScore(x,y+1):
            return False
        return True
        
root=Tk()
root.title("Tk Go!")
myapp=App(root)
root.mainloop()
