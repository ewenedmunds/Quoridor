import pygame
import os
import time

pygame.init()
gameWidth = 552
gameHeight = 780
gameDisplay = pygame.Surface((gameWidth,gameHeight))
screen = pygame.display.set_mode((gameWidth,gameHeight))

pygame.display.set_caption("Quoridor")

clock = pygame.time.Clock()

def loadImage(image):
    return pygame.image.load(os.path.join('Sprites',image))

pygame.display.set_icon(loadImage("icon.png"))

def loadSound(name):
    sound = pygame.mixer.Sound(os.path.join('Sounds',name))
    return sound


#Class for the player tiles
class Player(pygame.sprite.Sprite):
    def __init__(self, playerID):
        pygame.sprite.Sprite.__init__(self)
        
        self.id = playerID
        
        self.x = 4
        
        self.wallCount = 10
        
        #Set position and sprite based on the player's id
        if playerID == 0:
            self.y = 0
            self.image = loadImage("fireball.png")
        else:
            self.y = 8
            self.image = loadImage("ball.png")
            
        self.winningY = 8-self.y
        
        self.rect = self.image.get_rect()
        self.updatePosition()
        
    def updatePosition(self, ):
        self.rect.x = 12 + (self.x*60)
        self.rect.y = 12 + (self.y*60)
        
    #Attempts to move the player tile in a specified direction
        #Returns whether the move was successful or not
    def move(self, direction, board):
        if board.canMakeMove(self.x, self.y, direction):
            
            if direction == "right":
                self.x += 1
            elif direction == "left":
                self.x -= 1
            elif direction == "up":
                self.y -= 1
            elif direction == "down":
                self.y += 1
                
            self.updatePosition()
            
            return True
        return False
    
    def startPathfinding(self, board):
        for cell in cellSprites:
            cell.distanceFromPlayer = 99
            cell.isSearchedYet = False
        
        startCell = getCellAt(self.x, self.y)
        startCell.distanceFromPlayer = 0
        startCell.isSearchedYet = True
        
        self.previousNewCells = [startCell]
        self.newCells = []
    
    
    #Goes through one 'step' of pathfinding - returning True if a successful path has been found, False if no path exists
    def nextPathfindingStep(self, board):
        
        #From each new cell, try to move in each cardinal direction and check whether this results in a new cell being found
        for cell in self.previousNewCells:
                if cell.y == self.winningY:
                    return True
                
                for i in range(4):
                    direction = ["right","left","up","down"][i]
                    
                    if board.canMakeMove(cell.x, cell.y, direction):
                        
                        if i < 2:
                            adjacentCell = getCellAt(cell.x+[1,-1][i], cell.y)
                        else:
                            adjacentCell = getCellAt(cell.x, cell.y+[0,0,-1,1][i])
                        
                        if adjacentCell != None:
                            adjacentCell.distanceFromPlayer = min(adjacentCell.distanceFromPlayer, cell.distanceFromPlayer+1)
                            
                            if (adjacentCell.isSearchedYet == False):
                                adjacentCell.isSearchedYet = True
                                
                                if adjacentCell.y == self.winningY:
                                    adjacentCell.image = loadImage("p1found.png")
                                else:
                                    adjacentCell.image = loadImage("p1checked.png")
                                
                                self.newCells.append(adjacentCell)
        
        #If no new cells were found, then no successful path exists
        if self.previousNewCells == []:
            return False
        
        self.previousNewCells = []
        for item in self.newCells:
            self.previousNewCells.append(item)
        self.newCells = []
    
    
    #Checks whether a successful path exists from this player to their winning position, returning True if so, False if not
    def canReachWinningTile(self, board):
        while self.previousNewCells != []:

            if self.nextPathfindingStep(board) == True:
                return True

        return False
        



#Class for the tiles that make up the game board
class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.x = x
        self.y = y
        
        #Used in pathfinding
        self.distanceFromPlayer = 99
        self.isSearchedYet = False
        
        #Set image based on the tile's height
        if y == 0:
            self.originalImage = loadImage("pl1side.png")
        elif y == 8:
            self.originalImage = loadImage("pl2side.png")
        else:
            self.originalImage = loadImage("smooth.png")
            
        self.image = self.originalImage
            
        #PyGame Rect information
        self.rect = self.originalImage.get_rect()
        self.rect.x = 12 + x*60
        self.rect.y = 12 + y*60
        
#Class for the walls that can be placed on the game board
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y,sprite):
        pygame.sprite.Sprite.__init__(self)
            
        self.image = loadImage(sprite)
            
        #PyGame Rect information
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        

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
 


#Class to handle most of the logic of running the game
class GameManager():
    def __init__(self, player1, player2, board):
        self.player1 = player1
        self.player2 = player2
        self.currentPlayer = player1
        
        self.board = board
        
        self.playerAction = "idle"
        
        self.gameState = "running"
        
        self.pathDisplayTimer = 3
        self.isShowingPathfinding = True
        self.currentPlayerPathfinding = player1
        
    #Switches the current player, and checks to see whether the victory condition is met
    def endPlayerTurn(self):
        self.playerAction = "idle"
        
        if self.currentPlayer.y == self.currentPlayer.winningY:
            if self.currentPlayer == self.player1:
                self.gameState = "p1victory"
            else:
                self.gameState = "p2victory"
        
        if self.currentPlayer == self.player1:
            self.currentPlayer = self.player2
        else:
            self.currentPlayer = self.player1
           
        
    #Attempts to place a wall object on the screen, and update the board display, based on mouse position
    def placeWall(self):
        if self.playerAction == "placing h wall":
            #Find co-ords of the wall to place, rounding to nearest square that is in the board range
            x = round((round((pygame.mouse.get_pos()[0]),1)-54)/60)
            x = min(max(0,x),7)
            y = round((round((pygame.mouse.get_pos()[1]),1)-6)/60)
            y = min(max(1,y),8)
            
            #Check whether the wall can be placed here 
            if self.currentPlayer.wallCount > 0 and self.board.canPlaceWall(x, y-1, 'h', self.player1, self.player2, self.isShowingPathfinding):
                if self.isShowingPathfinding == False:
                    self.addWallObject(x,y,'h')
                else:
                    self.proposedWall = Wall(x*60+12,y*60,"wallh.png")
                    wallSprites.add(self.proposedWall)
                    self.startPathfinding(x,y,'h')
                    

        elif self.playerAction == "placing v wall":
            x = round((round((pygame.mouse.get_pos()[0]),1))/60)
            x = min(max(1,x),8)
            y = round((round((pygame.mouse.get_pos()[1]),1)-60)/60)
            y = min(max(0,y),7)

            if self.currentPlayer.wallCount > 0 and self.board.canPlaceWall(x-1, y, 'v', self.player1, self.player2, self.isShowingPathfinding):
                if self.isShowingPathfinding == False:
                    self.addWallObject(x,y,'v')
                else:
                    self.proposedWall = Wall(x*60,y*60+12,"wallv.png")
                    wallSprites.add(self.proposedWall)
                    self.startPathfinding(x,y,'v')
                    
        for cell in cellSprites:
            cell.image = cell.originalImage
                
                
    #Creates and adds a wall object, and updates the board representation
    def addWallObject(self,x,y,orientation):
        if orientation == 'h':
            wallSprites.add(Wall(x*60+12,y*60,"wallh.png"))
            self.board.placeWall(x, y-1, 'h')
            self.currentPlayer.wallCount -= 1
            self.endPlayerTurn()
        else:
            wallSprites.add(Wall(x*60,y*60+12,"wallv.png"))
            self.board.placeWall(x-1, y, 'v')
            self.currentPlayer.wallCount -= 1
            self.endPlayerTurn()
            
            
    #Sets up information needed to display pathfinding
    def startPathfinding(self,x,y,orientation):
        print("Pathfinding!") 
        
        self.proposedWallX = x
        self.proposedWallY = y
        self.proposedWallOrientation = orientation
        self.gameState = "pathfinding"
        self.currentPlayerPathfinding = self.player1
        self.currentPlayerPathfinding.startPathfinding(self.board)
            
            
    def update(self, events):
        #Handle the input events for the player
        for event in events:
            if event.type == pygame.KEYDOWN and self.gameState == "running":
                if event.key == pygame.K_w:
                    if self.currentPlayer.move("up", self.board):
                        self.endPlayerTurn()
                elif event.key == pygame.K_a:
                    if self.currentPlayer.move("left", self.board):
                        self.endPlayerTurn()
                elif event.key == pygame.K_s:
                    if self.currentPlayer.move("down", self.board):
                        self.endPlayerTurn()
                elif event.key == pygame.K_d:
                    if self.currentPlayer.move("right", self.board):
                        self.endPlayerTurn()
                        
                elif event.key == pygame.K_1:
                    self.playerAction = "placing h wall"
                elif event.key == pygame.K_2:
                    self.playerAction = "placing v wall"
            
            if event.type == pygame.MOUSEBUTTONUP and self.gameState == "running":
                self.placeWall()
                if pygame.mouse.get_pos()[0] > 20 and pygame.mouse.get_pos()[0] <= 50 and pygame.mouse.get_pos()[1] >= 720 and pygame.mouse.get_pos()[1] <= 750:
                    self.isShowingPathfinding = not self.isShowingPathfinding
                        
                    
        #Handling the display of pathfinding when it is set to visible
        if self.gameState == "pathfinding":
            #Decrease timer for next step
            self.pathDisplayTimer -= 1
            
            if self.pathDisplayTimer <= 0:
                
                self.pathDisplayTimer = 3
                #Check whether the current pathfinding has reached a successful endpoint
                hasReachedEndPoint = self.currentPlayerPathfinding.nextPathfindingStep(self.board)
                if hasReachedEndPoint == True:
                    
                    #If this is the second player, then both finished successfully - commit and add the wall, revert to regular game state
                    if self.currentPlayerPathfinding == self.player2:
                        self.currentPlayer.wallCount -= 1
                        self.endPlayerTurn()
                        self.gameState = "running"
                        self.addWallObject(self.proposedWallX, self.proposedWallY, self.proposedWallOrientation)
                        for cell in cellSprites:
                            cell.image = cell.originalImage
                        self.proposedWall.kill()
                            
                    #Otherwise we need to check the wall for the second player
                    else:
                        for cell in cellSprites:
                            cell.image = cell.originalImage
                            
                        self.currentPlayerPathfinding = self.player2
                        self.currentPlayerPathfinding.startPathfinding(self.board)
                        
                        
                #If no path could be found, revert the game board - don't add wall, and don't swap player turn
                elif hasReachedEndPoint == False:
                    for cell in cellSprites:
                            cell.image = cell.originalImage
                            
                    self.proposedWall.kill()
                    self.gameState = "running"
                    self.board.revertBoard()
                    
        self.showGhostWall()
        
        self.updateText()
        
        
    #Show a ghost image of where the player is planning to place a wall, based on mouse position
    def showGhostWall(self):
        if self.playerAction == "placing h wall":
            x = round((round((pygame.mouse.get_pos()[0]),1)-54)/60)
            x = min(max(0,x),7)
            y = round((round((pygame.mouse.get_pos()[1]),1)-6)/60)
            y = min(max(1,y),8)
            
            wallSprites.add(Effect(x*60+12,y*60,"wallth.png",1))
        
        elif self.playerAction == "placing v wall":
            x = round((round((pygame.mouse.get_pos()[0]),1))/60)
            x = min(max(1,x),8)
            y = round((round((pygame.mouse.get_pos()[1]),1)-60)/60)
            y = min(max(0,y),7)
            
            wallSprites.add(Effect(x*60,y*60+12,"walltv.png",1))
        
    #Add text objects to the display
    def updateText(self):
        if self.gameState == "running":
            text=font.render("It is player "+str(self.currentPlayer.id+1)+"'s turn!", 1,(0,0,0))
        elif self.gameState == "p1victory":
            text=font.render("Player 1 wins!", 1,(244, 212, 66))
        elif self.gameState == "p2victory":
            text=font.render("Player 2 wins!", 1,(244, 212, 66))
        elif self.gameState == "pathfinding":
            text=font.render("Checking Paths", 1,(0,0,0))
        gameDisplay.blit(text,(20,600))
        
        text=font.render("Player 1 has "+str(self.player1.wallCount)+" walls left!", 1,(0,0,0))
        gameDisplay.blit(text,(20,640))
        text=font.render("Player 2 has "+str(self.player2.wallCount)+" walls left!", 1,(0,0,0))
        gameDisplay.blit(text,(20,660))
        
        
        if self.isShowingPathfinding:
            colour = (0,200,0)
        else:
            colour = (200,0,0)
            
        pygame.draw.rect(gameDisplay,colour,[20,720,30,30])
        text=font.render("Show path validation? ", 1,(0,0,0))
        gameDisplay.blit(text,(60,720))
        
        
        
        

#Class for displaying temporary sprites
class Effect(pygame.sprite.Sprite):
    def __init__(self,x,y,image,duration):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = loadImage(image)

        self.totaltick = 0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.duration = duration

    def update(self):
        self.totaltick += 1

        if self.totaltick >= self.duration:
            self.kill()
            del self

        
#Initial Setup - Creating Game Tiles, Players, Board
def initialiseGame():
    for y in range(9):
        for x in range(9):
            cellSprites.add(Cell(x,y))
            
    
def getCellAt(x, y):
    for cell in cellSprites:
        if cell.x == x and cell.y == y:
            return cell
        
    return None

def mainLoop():
    
    isGameRunning = True
    
    initialiseGame()
    
    player1 = Player(0)
    player2 = Player(1)
    playerSprites.add(player1)
    playerSprites.add(player2)
    
    board = Board()
    
    gameManager = GameManager(player1, player2, board)

    while isGameRunning:
        
        gameDisplay.fill((255,255,255))
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    isGameRunning = False
                
        
        gameManager.update(events)
                    
        cellSprites.draw(gameDisplay)
        
        wallSprites.draw(gameDisplay)
        wallSprites.update()

        playerSprites.update()
        playerSprites.draw(gameDisplay)

        

        screen.blit(gameDisplay,(0,0))
        clock.tick(60)
        pygame.display.update()

font=pygame.font.Font('ReturnOfGanon.ttf',18)

playerSprites = pygame.sprite.Group()
cellSprites = pygame.sprite.Group()
wallSprites = pygame.sprite.Group()



mainLoop()
pygame.quit()
quit()
