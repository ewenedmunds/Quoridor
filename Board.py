#Class for representing the board
class Board():
    def __init__(self):
        
        #A board setup, represented by a matrix of characters
        #--
        # ["0.0.0.0.0.0.0.0.0",
        #  ".................",
        #          VVV
        #  "0.0.0.0.0.0.0.0.0"]
        #
        # Where '0' represents a cell, '.' represents a gap between cells

        self.boardRepresentation = []
        self.boardRepresentation.append("0.0.0.0.0.0.0.0.0")
        for i in range (8):
            self.boardRepresentation.append(".................")
            self.boardRepresentation.append("0.0.0.0.0.0.0.0.0")
            
    #Checks whether a player can make a legitimate move given a position and a direction
        #Returning true if they can, false otherwise
    def canMakeMove(self, xPos, yPos, direction):
        representedX = 2*xPos
        representedY = 2*yPos
        
        if direction == "right" and (xPos >= 8 or self.boardRepresentation[representedY][representedX+1] != '.'):
            return False
        elif direction == "left" and (xPos <= 0 or self.boardRepresentation[representedY][representedX-1] != '.'):
            return False
        elif direction == "up" and (yPos <= 0 or self.boardRepresentation[representedY-1][representedX] != '.'):
            return False
        elif direction == "down" and (yPos >= 8 or self.boardRepresentation[representedY+1][representedX] != '.'):
            return False
        
        return True
    
    
    def canPlaceWall(self, xPos, yPos, orientation, player1, player2, isShowingPathfinding):
        #Copy the board so we can make changes to it and revert
        self.tempBoard = []
        for i in range(17):
            self.tempBoard.append(self.boardRepresentation[i])
            
        if isShowingPathfinding == False:
            isLegitPlacement = self.canPlaceWallBoardCheck(xPos, yPos, orientation) 
            
            self.placeWall(xPos, yPos, orientation)
            
            player1.startPathfinding(self)
            isLegitPlacement = isLegitPlacement and player1.canReachWinningTile(self)
            
            player2.startPathfinding(self)
            isLegitPlacement = isLegitPlacement and player2.canReachWinningTile(self)

            self.boardRepresentation = self.tempBoard
            return isLegitPlacement
        
        else:
            if self.canPlaceWallBoardCheck(xPos, yPos, orientation):
                self.placeWall(xPos, yPos, orientation)
                return True
            return False
               
    
    #Check whether a player can place a wall of given orientation at a specific point
    def canPlaceWallBoardCheck(self, xPos, yPos, orientation):
        xRepresented = xPos*2 + 1
        yRepresented = yPos*2 + 1
        
        if orientation == 'h':
            for j in range(3):
                x = xRepresented + (j-1)
                
                if self.boardRepresentation[yRepresented][x] != '.':
                    return False
                
        else:
            for i in range(3):
                y = yRepresented + (i-1)
        
                if self.boardRepresentation[y][xRepresented] != '.':
                    return False
        return True
    
    #Update the board representation with a new player placed wall
    def placeWall(self, xPos, yPos, orientation):
        xRepresented = xPos*2 + 1
        yRepresented = yPos*2 + 1
        
        if orientation == 'h':
            for j in range(3):
                x = xRepresented + (j-1)
                self.boardRepresentation[yRepresented] = self.boardRepresentation[yRepresented][0:x]+'X'+self.boardRepresentation[yRepresented][x+1:]
                
        else:
            for i in range(3):
                y = yRepresented + (i-1)
        
                self.boardRepresentation[y] = self.boardRepresentation[y][0:xRepresented]+'X'+self.boardRepresentation[y][xRepresented+1:]
                
    #Reverts the representation to the previous state
    def revertBoard(self):
        self.boardRepresentation = self.tempBoard