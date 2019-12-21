import pygame
import random
import os
import pickle
import time

pygame.init()
gameWidth = 552
gameHeight = 820
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

#Class for the two player tokens
class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,sprite,pid):
        pygame.sprite.Sprite.__init__(self)

        self.x = x
        self.y = y
        self.id = pid
        if self.id == 1:
            self.winy = 8
        else:
            self.winy = 0

        self.image = loadImage(sprite)
        self.rect = self.image.get_rect()
        self.rect.x = (self.x*48)+(12*(self.x+1))
        self.rect.y = (self.y*48)+(12*(self.y+1))

        self.cell().state = self.id

        self.walls = 10

    def cell(self):
        for cell in cellSprites:
            if cell.x == self.x and cell.y == self.y:
                return cell

    def collide(self,direction,value=1):
        hasCollidedWithWall = False
        if self.x < 0 or self.y < 0 or self.x > 8 or self.y > 8:
            return True
 
        if direction == 0:
            self.rect.y += 5+(50*value-1)
        elif direction == 1:
            self.rect.x += 5+(50*value-1)
        elif direction == 2:
            self.rect.y -= 5+(50*value-1)
        elif direction == 3:
            self.rect.x -= 5+(50*value-1)

        
        if pygame.sprite.spritecollide(self,wallSprites,False):
            hasCollidedWithWall = True

        if direction == 0:
            self.rect.y -= 5
        elif direction == 1:
            self.rect.x -= 5
        elif direction == 2:
            self.rect.y += 5
        elif direction == 3:
            self.rect.x += 5
                
        if hasCollidedWithWall:
            return True
        
    def move(self,direction,value=1):
        if value==1:
            self.cell().state = 0
        if direction == 0:
            self.y += 1
        elif direction == 1:
            self.x += 1
        elif direction == 2:
            self.y -= 1
        elif direction == 3:
            self.x -= 1

        flag = True
        if self.collide(direction,value):
            flag = False
            if direction == 0:
                self.y -= 1
            elif direction == 1:
                self.x -= 1
            elif direction == 2:
                self.y += 1
            elif direction == 3:
                self.x += 1

        self.rect.x = (self.x*48)+(12*(self.x+1))
        self.rect.y = (self.y*48)+(12*(self.y+1))
        self.cell().state = self.id

        return flag

    def checkWalls(self):
        global textSprites
        search = True
        found = False
        for cell in cellSprites:
            cell.searched = False
            cell.dist = 999999999

        self.cell().searched = True
        self.cell().dist = 0
        while search:

            events =  pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN and showPath == True:
                    if event.key == pygame.K_RETURN:
                        search = False
                        
            for cell in cellSprites:
                if cell.y == self.winy and cell.searched == True:
                    if showPath:
                        cell.image = loadImage("p1found.png")
                        effectSprites.add(Effect(cell.rect.x,cell.rect.y,str(cell.dist),1))
                        cellSprites.draw(gameDisplay)
                        wallSprites.draw(gameDisplay)
                        effectSprites.update()
                        effectSprites.draw(gameDisplay)
                        for text in textSprites:
                            text1=font.render(text[0], 1,(0,0,0))
                            gameDisplay.blit(text1,(text[1],text[2]))
                        screen.blit(gameDisplay,(0,0))
                        pygame.display.update()

                        if showFull != True:
                            time.sleep(2)
                            found = True
                            search = False
                            break
                        
                    found = True
                    
                if cell.searched == True:
                    if cell.checkWalls() == True:
                        search = True

        for cell in cellSprites:
            cell.image = loadImage(cell.oimage)

        effectSprites.empty()
        textSprites = []

        return found
            

                    

class Cell(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        
        #Different colours for top and bottom row
        if y == 0:
            self.oimage = "pl1side.png"
        elif y == 8:
            self.oimage = "pl2side.png"
        else:
            self.oimage = "smooth.png"
        self.image = loadImage(self.oimage)
        
        self.rect = self.image.get_rect()
        self.rect.x = 12+x*60
        self.rect.y = 12+y*60
        self.x = x
        self.y = y
        
        self.state = 0
        self.dist = 0

    #Min function for distance
    def distc(self,amount):
        if amount < self.dist:
            self.dist = amount

    def move(self,direction):
        if direction == 0:
            self.velx = 0
            self.vely = 1
        elif direction == 1:
            self.velx = 1
            self.vely = 0
        elif direction == 2:
            self.velx = 0
            self.vely = -1
        elif direction == 3:
            self.velx = -1
            self.vely = 0
        self.rect.x += self.velx*5
        self.rect.y += self.vely*5
        
        if pygame.sprite.spritecollide(self,wallSprites,False):
            new = False
        else:
            try:
                if gCell(self.x+self.velx,self.y+self.vely).searched == False:
                    gCell(self.x+self.velx,self.y+self.vely).searched = True
                    gCell(self.x+self.velx,self.y+self.vely).image = loadImage("p1checked.png")
                    gCell(self.x+self.velx,self.y+self.vely).distc(self.dist + 1)
                    new = True
                else:
                    new = False
            except:
                new = False
        self.rect.x -= self.velx*5
        self.rect.y -= self.vely*5
        return new

    def checkWalls(self):
        new = False
        for i in range(4):
            if self.move(i) == True:
                new = True
            if self.searched != "done":
                if showPath:
                    
                    effectSprites.add(Effect(self.rect.x,self.rect.y,str(self.dist),1))
                    cellSprites.draw(gameDisplay)
                    wallSprites.draw(gameDisplay)
                    effectSprites.update()
                    effectSprites.draw(gameDisplay)
                    for text in textSprites:
                        text1=font.render(text[0], 1,(0,0,0))
                        gameDisplay.blit(text1,(text[1],text[2]))
                    screen.blit(gameDisplay,(0,0))
                    pygame.display.update()
                    time.sleep(0.01)
            self.searched = "done"
            


        return new

#Class for displaying animations or temporary sprites
class Effect(pygame.sprite.Sprite):
    def __init__(self,x,y,images,duration,velx=0,vely=0):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        if type(self.images) == str:
            self.image = loadImage("pixel.png")
        else:
            self.image = loadImage(self.images[0][0])
        self.imageindex = 0
        self.tick = 0
        self.totaltick = 0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velx = velx
        self.vely = vely
        self.duration = duration

    def update(self):
        if type(self.images) == str:
            textSprites.append([self.images,self.rect.x,self.rect.y,1])
        else:
            if self.tick > self.images[self.imageindex][1]:
                self.imageindex += 1
                if self.imageindex == len(self.images):
                    self.imageindex = 0
                self.image = loadImage(self.images[self.imageindex][0])
                self.tick = -1
        self.tick += 1
        self.totaltick += 1
        

        self.rect.x += self.velx
        self.rect.y += self.vely

        self.effect()
        if self.totaltick > self.duration:
            self.kill()
            del self

    def effect(self):
        pass
            

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        pygame.sprite.Sprite.__init__(self)
        self.image = loadImage(image)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x*60
        self.rect.y = y*60
        
        #Different offsets if the wall is a wall placed by a Player
        if image == "wallth.png" or image == "wallh.png":
            self.rect.x += 12
            self.typ = 1
        else:
            self.rect.y += 12
            self.typ = 2

#Returns a cell at a given co-ordinate
def gCell(x,y):
    for cell in cellSprites:
        if cell.x == x and cell.y == y:
            return cell
    print("No cell exists at this co-ordinate!");
            
#Tests placing a Player Wall of given rotation (state?) at a given location
def testPos(x,y,state):
    global string
    
    if x < 0 or y < 0 or x > 8 or y > 8 or state == 1 and x > 7 or state == 2 and y > 7:
        print("Invalid Location")
    else:
        isWallPlaced = False
        if state == 1:
            if string[y*2][((x*2)+1):(x*2)+4] == "=.=":
                string[y*2] = string[y*2][0:(x*2)+1]+"---"+string[y*2][(x*2)+4:]
                wallSprites.add(Wall(x,y,"wallh.png"))
                isWallPlaced = True
        elif state == 2:
            if string[(y*2)+1][((x*2)):(x*2)+1] == "=" and string[(y*2)+2][((x*2)):(x*2)+1] == "." and string[(y*2)+3][((x*2)):(x*2)+1] == "=":
                string[(y*2)+1] = string[(y*2)+1][0:(x*2)+0]+"|"+string[(y*2)+1][(x*2)+1:]
                string[(y*2)+2] = string[(y*2)+2][0:(x*2)+0]+"|"+string[(y*2)+2][(x*2)+1:]
                string[(y*2)+3] = string[(y*2)+3][0:(x*2)+0]+"|"+string[(y*2)+3][(x*2)+1:]
                wallSprites.add(Wall(x,y,"wallv.png"))
                isWallPlaced = True

        isInvalidLocation = False
        for player in playerSprites:
            if player.checkWalls() == False:
                isInvalidLocation = True

        if isInvalidLocation:
            isWallPlaced = False
            if state == 1:
                string[y*2] = string[y*2][0:(x*2)+1]+"=.="+string[y*2][(x*2)+4:]
                
            elif state == 2:
                    string[(y*2)+1] = string[(y*2)+1][0:(x*2)+0]+"="+string[(y*2)+1][(x*2)+1:]
                    string[(y*2)+2] = string[(y*2)+2][0:(x*2)+0]+"."+string[(y*2)+2][(x*2)+1:]
                    string[(y*2)+3] = string[(y*2)+3][0:(x*2)+0]+"="+string[(y*2)+3][(x*2)+1:]


            for wall in wallSprites:
                    if wall.x == x and wall.y == y and wall.typ == state:
                        wall.kill()
                        del wall
        return isWallPlaced

def initialiseGame():
    global players
    global string
    string = []
    players = []
    playerSprites.empty()
    cellSprites.empty()
    wallSprites.empty()
    for y in range(19):
        string.append("")
        for x in range(19):
            if (y+1)%2 == 0 and (x+1)%2 == 0:
                char = "O"
            elif (y+1)%2 == 0 and (x+1)%2 != 0 or (x+1)%2 == 0 and (y+1)%2 != 0:
                char = "="
            else:
                char = "."
            string[y] += char
                       
    for y in range(9):
        for x in range(9):
            cellSprites.add(Cell(x,y))
    player1 = Player(4,0,"ball.png",1)
    player2 = Player(4,8,"fireball.png",2)

    playerSprites.add(player1)
    playerSprites.add(player2)
    players.append(player1)
    players.append(player2)
    
    
players = []
string = []

showPath = False
showFull = False

def mainLoop():
    global players
    global showPath
    global showFull
    running = True
    initialiseGame()
    
    activePlayer = players[0]
    state = 0
    while running:
        tempWallSprites.empty()

        x = round((pygame.mouse.get_pos()[0])//60,1)
        y = round((pygame.mouse.get_pos()[1])//60,1)
            
        if x <= 0 and state == 2 or y <= 0 and state == 1 or x > 8 or y > 8 or state == 1 and x > 7 or state == 2 and y > 7:
            pass
        else:
            if state == 1:
                tempWallSprites.add(Wall(x,y,"wallth.png"))
            elif state == 2:
                tempWallSprites.add(Wall(x,y,"walltv.png"))

        gameDisplay.fill((255,255,255))
        flag = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_n:
                    initialiseGame()
                    state = 0
                    activePlayer = players[0]

                if state < 4:
                    
                    if event.key == pygame.K_w and activePlayer == players[0] or event.key == pygame.K_UP and activePlayer == players[1]:
                        flag = activePlayer.move(2)
                    elif event.key == pygame.K_a and activePlayer == players[0] or event.key == pygame.K_LEFT and activePlayer == players[1]:
                        flag = activePlayer.move(3)
                    elif event.key == pygame.K_s and activePlayer == players[0] or event.key == pygame.K_DOWN and activePlayer == players[1]:
                        flag = activePlayer.move(0)
                    elif event.key == pygame.K_d and activePlayer == players[0] or event.key == pygame.K_RIGHT and activePlayer == players[1]:
                        flag = activePlayer.move(1)
                    

                    elif event.key == pygame.K_q and activePlayer == players[0] or event.key == pygame.K_SLASH and activePlayer == players[1] or event.key == pygame.K_1:
                        state = 1
                    elif event.key == pygame.K_e and activePlayer == players[0] or event.key == pygame.K_RSHIFT and activePlayer == players[1] or event.key == pygame.K_2:
                        state = 2
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and state < 4:
                if state != 0 and activePlayer.walls > 0:
                    if testPos(pygame.mouse.get_pos()[0]//60,pygame.mouse.get_pos()[1]//60,state) == True:
                        flag = True
                        activePlayer.walls -= 1
            if event.type == pygame.MOUSEBUTTONUP:
                if pygame.mouse.get_pos()[0] > 20 and pygame.mouse.get_pos()[0] <= 50 and pygame.mouse.get_pos()[1] >= 720 and pygame.mouse.get_pos()[1] <= 750:
                    if showPath:
                        showPath = False
                    else:
                        showPath = True
                elif showPath == True and pygame.mouse.get_pos()[0] > 20 and pygame.mouse.get_pos()[0] <= 50 and pygame.mouse.get_pos()[1] >= 780 and pygame.mouse.get_pos()[1] <= 810:
                    if showFull:
                        showFull = False
                    else:
                        showFull = True
                        

        if flag == True:
            state = 0
            if activePlayer.id == 1 and activePlayer.y == 8:
                state = 4
            elif activePlayer.id == 2 and activePlayer.y == 0:
                state = 5
            
            if activePlayer == players[0]:
                activePlayer = players[1]
            else:
                activePlayer = players[0]
                

        wallSprites.draw(gameDisplay)
        tempWallSprites.draw(gameDisplay)

        cellSprites.draw(gameDisplay)

        playerSprites.update()
        playerSprites.draw(gameDisplay)

        effectSprites.update()
        effectSprites.draw(gameDisplay)

        if state < 4:
            text=font.render("It is player "+str(activePlayer.id)+"'s turn!", 1,(0,0,0))
        elif state == 4:
            text=font.render("Player 1 wins!", 1,(244, 212, 66))
        elif state == 5:
            text=font.render("Player 2 wins!", 1,(244, 212, 66))
        gameDisplay.blit(text,(20,600))
        text=font.render("Player 1 has "+str(players[0].walls)+" walls left!", 1,(0,0,0))
        gameDisplay.blit(text,(20,640))
        text=font.render("Player 2 has "+str(players[1].walls)+" walls left!", 1,(0,0,0))
        gameDisplay.blit(text,(20,660))

        if showPath:
            colour = (0,200,0)
        else:
            colour = (200,0,0)
        if showFull:
            colour2 = (0,200,0)
        else:
            colour2 = (200,0,0)
        pygame.draw.rect(gameDisplay,colour,[20,720,30,30])
        text=font.render("Show path validation? ", 1,(0,0,0))
        gameDisplay.blit(text,(60,720))

        if showPath:
            pygame.draw.rect(gameDisplay,colour2,[20,780,30,30])
            text=font.render("Show full path? ", 1,(0,0,0))
            gameDisplay.blit(text,(60,780))

        screen.blit(gameDisplay,(0,0))
        clock.tick(60)
        pygame.display.update()

font=pygame.font.Font('ReturnOfGanon.ttf',18)

playerSprites = pygame.sprite.Group()
cellSprites = pygame.sprite.Group()
wallSprites = pygame.sprite.Group()
tempWallSprites = pygame.sprite.Group()
effectSprites = pygame.sprite.Group()
textSprites = []

mainLoop()
pygame.quit()
quit()
