
from dataclasses import dataclass 
from copy import deepcopy
from random import randint
from Levels import LEVELS

# import and initilise pygame and pygame fonts 
import pygame 
pygame.init()
pygame.font.init()

TEXT = pygame.font.SysFont("pingfang",40) # Setting up font used for the buttons

class InputManager: # This object managed player inputs
    def __init__(self):
        self.quit_buffer = False # Flag signalling is the game should exit
        # Dictionaries detecting key presses
        self.held_keys = {pygame.K_LEFT : False , pygame.K_RIGHT : False , pygame.K_UP : False , pygame.K_0 : False , pygame.K_1 : False , pygame.K_2 : False , pygame.K_3 : False , pygame.K_4 : False}
        self.pressed_keys = {pygame.K_c : False , pygame.K_x : False , pygame.K_SPACE : False}

        # Holds mouse position and if its clicked
        self.mouse_pos = (0,0)
        self.mouse_clicked = False
        pass

    def update(self): # updates the player inputs 
        for key in self.pressed_keys: # Resets pressed keys
            self.pressed_keys[key] = False

        self.mouse_pos = pygame.mouse.get_pos() # get mouse position
        self.mouse_clicked = False # reset the mouse pressed 

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # sets the game to quit
                self.quit_buffer = True

            if event.type == pygame.MOUSEBUTTONDOWN: # updates mouse state
                self.mouse_clicked = True

            if event.type == pygame.KEYDOWN: # updates key presses
                if self.held_keys.get(event.key , "Not Found") != "Not Found":
                    self.held_keys[event.key] = True
                if self.pressed_keys.get(event.key , "Not Found") != "Not Found":
                    self.pressed_keys[event.key] = True

            if event.type == pygame.KEYUP: # updates key releases
                if self.held_keys.get(event.key , "Not Found") != "Not Found":
                    self.held_keys[event.key] = False

class GameManager: # object for running the game
    def __init__(self):
        self.display = pygame.display.set_mode((1400,800),pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.inputs = InputManager()

        self.gameloop = self.mainMenu

        self.currentpage = 0
        self.selectedlevel = 0

        self.editmode = 0
        self.editlevel = []

        self.player = Player()
        self.level = MakeLevel(LEVELS[0])
        self.currentlevel = 0
        self.playmode = ""
        self.exits = []

        self.screen_shake = 0
        self.screen_shake_duration = 0
        self.screen_freeze_duration = 0
    
    def exit(self): # Signals to quit the game
        self.inputs.quit_buffer = True
        return pygame.Surface((720,720))
    
    def startplayalllevels(self): # Sets the game ready to play through all the levels
        self.loadLevel(0)
        self.playmode = "A"
        self.gameloop = self.playLevel
        return pygame.Surface((720,720))
    
    def startplaysingleLevel(self): # Sets the game ready to play though a single level
        self.loadLevel(self.selectedlevel)
        self.playmode = "S"
        self.gameloop = self.playLevel
        return pygame.Surface((720,720))
    
    def loadLevel(self,levelindex): # Sets up the attributes for running a level
        self.currentlevel = levelindex
        self.level = MakeLevel(LEVELS[levelindex])
        self.player = Player(rect = self.level.start)
        self.exits = self.level.end
        pass

    def playLevel(self): # Gameloop for playing through levels
        # Updates the screen and players
        surf = pygame.Surface((720,720),pygame.SRCALPHA)
        surf.blit(self.level.Draw(),(0,0))
        surf.blit(self.player.update(self.inputs,self.level.physicsbodies),(0,0))

        # Updates screen modifiers 
        if self.player.freeze_buffer:
            self.screen_freeze_duration = self.player.freeze_buffer
            self.player.freeze_buffer = 0
        if self.player.shake_buffer != (0,0):
            self.screen_shake , self.screen_shake_duration = self.player.shake_buffer
            self.player.shake_buffer = (0,0)
        
        # Checks if player should die 
        for body in self.level.hostilebodies:
            if body.colliderect(self.player.rect):
                self.loadLevel(self.currentlevel)
        
        # Checks if player has reached an exit 
        for exit in self.exits:
            if not self.player.rect.colliderect(exit):
                continue
            if not self.playmode == "A": # If playing through all levels 
                self.gameloop = self.mainMenu
                continue
            self.currentlevel += 1
            if self.currentlevel >= len(LEVELS):
                self.gameloop = self.mainMenu
                return surf
            self.loadLevel(self.currentlevel)
        
        return surf

    def mainMenu(self): # Main menu gameloop
        surf = pygame.Surface((1400,800),pygame.SRCALPHA)
        buttons = [pygame.Rect(567,300,300,75),pygame.Rect(567,400,300,75),pygame.Rect(567,500,300,75),pygame.Rect(567,600,300,75)] # Button rects
        labels = ["Play","Select level","Edit level","Exit"] # The button labels 
        gameloops = [self.startplayalllevels,self.startSelectLevel,self.startLevelEdit,self.exit] # The gameloop according to button
        for i in range(len(buttons)):
            button = buttons[i] 
            pygame.draw.rect(surf,(255,255,255),button)
            if button.collidepoint(self.inputs.mouse_pos[0],self.inputs.mouse_pos[1]): # If hovering over button
                if self.inputs.mouse_clicked: # If button clicked
                    self.gameloop = gameloops[i]
                pygame.draw.rect(surf,(155,155,155),button)
            text = TEXT.render(labels[i],False,(0,0,0))
            surf.blit(text,(button.x,button.y))
        return surf
    
    def startSelectLevel(self): # sets the game ready to select a level 
        self.currentpage = 0
        self.gameloop = self.selectLevel
        return pygame.Surface((720,720))

    def selectLevel(self): # gameloop for selecting levels 
        surf = pygame.Surface((1400,800),pygame.SRCALPHA)
        levelsleft = len(LEVELS) - (self.currentpage * 4)
        rects , labels , actions = [] , [] , []
        for i in range(min(levelsleft,4)):
            rects.append(pygame.Rect(567,300 + (i*100),300,75))
            labels.append(str(i + 1 + (self.currentpage * 4)))
            actions.append(i + (self.currentpage * 4))
        if self.currentpage > 0: # adds previous page if not on the first
            rects.append(pygame.Rect(167,600,300,75))
            labels.append("Previous page")
            actions.append("Previous")
        if levelsleft > 4: # adds next page is not on the last 
            rects.append(pygame.Rect(967,600,300,75))
            labels.append("Next page")
            actions.append("Next")
        for i in range(len(rects)):
            if rects[i].collidepoint(self.inputs.mouse_pos[0],self.inputs.mouse_pos[1]):
                if self.inputs.mouse_clicked: # if the button is clicked 
                    self.selectlevelaction(actions[i])
                pygame.draw.rect(surf,(155,155,155),rects[i])
            else:
                pygame.draw.rect(surf,(255,255,255),rects[i])
            text = TEXT.render(labels[i],False,(0,0,0))
            surf.blit(text,(rects[i].x,rects[i].y))
        return surf

    def selectlevelaction(self,argument): # determines what to do depending on the action selected in select level
        if type(argument) == int:
            self.selectedlevel = argument
            self.gameloop = self.startplaysingleLevel
        elif argument == "Previous":
            self.currentpage -= 1
        elif argument == "Next":
            self.currentpage += 1

    def startLevelEdit(self): # sets up the game ready to edit levels 
        self.editmode = 0
        self.editlevel = [[0 for i in range(15)] for j in range(15)]
        self.gameloop = self.levelEdit
        return pygame.Surface((720,720))
    
    def levelEdit(self): # gameloop function for building levels
        surface = pygame.Surface((720,720))
        level = self.editlevel

        keys = [pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4]

        for i in range(5):
            if self.inputs.held_keys[keys[i]]:
                self.Editmode = i

        if self.inputs.pressed_keys[pygame.K_SPACE]:
            LEVELS.append(deepcopy(self.editlevel))
            self.gameloop = self.mainMenu
        
        if self.inputs.mouse_clicked:
            x,y = self.inputs.mouse_pos
            width , height = self.display.get_size()
            topleftx = (width - 720 )// 2
            toplefty = (height - 720) // 2
            x = x -topleftx
            y = y -toplefty
            if x > 0 and x < 720 and y > 0 and y < 720:
                level[y//48][x//48] = self.Editmode

        for i in range(len(level)):
            for j in range(len(level[i])):
                if level[j][i] == 0:
                    pygame.draw.rect(surface , (255,255,255) , pygame.Rect(i*48,j*48,48,48),width=2)
                elif level[j][i] == 1:
                    pygame.draw.rect(surface , (255,255,255), pygame.Rect(i*48,j*48,48,48))
                elif level[j][i] == 2:
                    pygame.draw.rect(surface , (231,84,75), pygame.Rect(i*48,j*48,48,48))
                elif level[j][i] == 3:
                    pygame.draw.rect(surface , (0,255,0), pygame.Rect(i*48,j*48,48,48))
                elif level[j][i] == 4:
                    pygame.draw.rect(surface , (255,255,0), pygame.Rect(i*48,j*48,48,48))
        return surface

    def run(self): # function for running the program 
        while not self.inputs.quit_buffer:
            self.clock.tick(60) # Keeps fps fixed

            if self.screen_freeze_duration: # screen freeze
                self.screen_freeze_duration -= 1
                continue

            self.inputs.update() # player inputs

            width , height = self.display.get_size() 
            surf = self.gameloop() # runs current game code which return surface
            self.display.fill((0,0,0))

            self.screen_shake_duration -= 1 # screen shake
            if self.screen_shake_duration == 0:
                self.screen_shake = 0
            displacementx , displacementy = randint(0,self.screen_shake) - self.screen_shake//2 , randint(0,self.screen_shake) - self.screen_shake//2
 
            self.display.blit(surf,((width-surf.get_width())//2 + displacementx,(height-surf.get_height())//2 + displacementy))
            pygame.display.update()
        
        pygame.quit()
        quit()

class Player: # object for controlling the player 
    def __init__(self,rect = pygame.Rect(0,0,48,48)):
        self.rect = rect
        self.colour = (49,204,195)

        self.walk_speed = 5
        self.gravity = 10
        self.y_jump_acc = -15
        self.x_jump_acc = 20
        self.y_dash_acc = -17
        self.x_dash_acc = 17

        self.y_acc = 0
        self.max_y_acc = 47
        self.x_acc = 0
        self.max_x_acc = 47

        self.on_ground = False
        self.on_wall = False
        self.dashed = False
        self.dash_buffer = 0

        self.freeze_buffer = 0
        self.shake_buffer = [0,0]
        pass

    def update(self,inputs,physicsbodies): # updates player movement and returns a screen with player on
        surf = pygame.Surface((720,720),pygame.SRCALPHA)

        dx , dy = self.MovementByInput(inputs) # Base movement according to player inputs
        dx , dy = self.Acceleration(dx,dy) # Changes movement according to player accelerations
        dx , dy = self.Collisions(physicsbodies,dx,dy) # Changes movement according to world collisions
        self.rect = self.rect.move(dx,dy) # Moves player by movement

        pygame.draw.rect(surf,self.colour,self.rect)
        return surf
    
    def MovementByInput(self,inputs): # Base movement according to player inputs
        dx = 0
        # Walking 
        if inputs.held_keys[pygame.K_LEFT]:
            dx += self.walk_speed * -1
        if inputs.held_keys[pygame.K_RIGHT]:
            dx += self.walk_speed  
        # Jumping 
        if inputs.pressed_keys[pygame.K_c] and (self.on_ground or self.on_wall):
            self.y_acc = self.y_jump_acc
            if self.on_wall and dx:
                self.x_acc = self.x_jump_acc * (dx // abs(dx)) * -1
        # Dashing
        self.dash_buffer -= 1
        if inputs.pressed_keys[pygame.K_x] and not self.dashed and self.dash_buffer <= 0:
            self.dash_buffer = 50
            self.dashed = True
            self.shake_buffer = (5,20)
            self.freeze_buffer = 5
            if inputs.held_keys[pygame.K_LEFT]:
                self.x_acc = self.x_dash_acc * -1
            if inputs.held_keys[pygame.K_RIGHT]:
                self.x_acc = self.x_dash_acc
            if inputs.held_keys[pygame.K_UP]:
                self.y_acc = self.y_dash_acc
        return dx , 0
    
    def Acceleration(self,dx,dy): # Changes movement according to player accelerations
        # Resistance to acceleration
        if self.x_acc:
            self.x_acc += (self.x_acc // abs(self.x_acc)) * -1        
        if self.y_acc < self.gravity:
            self.y_acc += 1
        # Check acceleration hasn't passed max
        if abs(self.x_acc) > self.max_x_acc:
            self.x_acc = self.max_x_acc * (self.x_acc // abs(self.x_acc))
        if abs(self.y_acc) > self.max_y_acc:
            self.y_acc = self.max_y_acc * (self.y_acc // abs(self.y_acc))
        # Increase movement by acceleration
        dx += self.x_acc
        dy += self.y_acc
        return dx , dy
    
    def Collisions(self,physicsbodies,dx,dy): # Changes movement according to world collisions
        self.on_wall = False
        self.on_ground = False
        for body in physicsbodies: # iterate through solidbodies
            if body.colliderect(self.rect.move(0,dy)): # Checks collision in the y axis
                if dy < 0: # If jumping
                    self.y_acc = 0
                    dy = body.bottom - self.rect.top
                if dy > 0: # If falling
                    self.on_ground = True
                    self.dashed = False
                    dy = body.top - self.rect.bottom
            if body.colliderect(self.rect.move(dx,0)): # Checks collisions in the x axis
                self.on_wall = True
                if dx < 0: # If moving right
                    dx = body.right - self.rect.left
                if dx > 0: # If moving left
                    dx = body.left - self.rect.right
        return dx , dy

@dataclass
class Level: # object for storing level infomation
    start:pygame.Rect
    physicsbodies:list[pygame.Rect]
    hostilebodies:list[pygame.Rect]
    end:list[pygame.Rect]

    def Draw(self): # returns a surface with the world rects displayed on it
        surface = pygame.Surface((720,720),pygame.SRCALPHA).convert_alpha()
        for body in self.physicsbodies:
            pygame.draw.rect(surface , (255,255,255) , body)
        for body in self.hostilebodies:
            pygame.draw.rect(surface , (231,84,75) , body)
        return surface

def MakeLevel(array): # function for making level objects 
    start = None
    physicsbodies = []
    hostilebodies = []
    end = []
    for i in range(len(array)):
        for j in range(len(array[i])):
            if array[i][j] == 1:
                physicsbodies.append(pygame.Rect(j*48,i*48,48,48))
            elif array[i][j] == 2:
                hostilebodies.append(pygame.Rect(j*48,i*48,48,48))
            elif array[i][j] == 3:
                start = pygame.Rect(j*48,i*48,48,48)
            elif array[i][j] == 4:
                end.append(pygame.Rect(j*48,i*48,48,48))
    return Level(start,physicsbodies,hostilebodies,end)

if __name__ == '__main__':
    g = GameManager()
    g.run()
