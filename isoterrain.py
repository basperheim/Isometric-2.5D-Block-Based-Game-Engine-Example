#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division
import ctypes; ctypes.windll.kernel32.SetConsoleTitleA("Isometric Terrain")
from ctypes import windll

# change directory to current directory
import sys, os, glob
from os.path import isfile, dirname, realpath, abspath
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append('\\images'); sys.path.append('iso_terra\\images')
sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))

# Import Win32 modules
user32 = ctypes.windll.user32; screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
import win32api, win32con, win32gui, win32ui
from win32api import GetSystemMetrics

from collections import OrderedDict
import random, re
import pygame
from pygame.locals import *

# import time module for time stamp objects
import time
from time import gmtime, strftime, sleep

import types
def imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            yield val.__name__
modules = imports()
print '\n', "MODULES USED:"
for i in modules:
    print i
print '\n\n'

# PYGAME -- Initiate Window and Pygame window parameters
def initiate_window(title="Isometric Terrain", screenX=int(screensize[0]*.8), screenY=int(screensize[1]*.8)):
    pygame.init()
    pygame.font.init()
    window_size = [screenX, screenY]
    window = pygame.display.set_mode(window_size,HWSURFACE|DOUBLEBUF|RESIZABLE)

    # Pygame game window's location within Windows OS
    SetWindowPos = windll.user32.SetWindowPos
    SetWindowPos(pygame.display.get_wm_info()['window'], 0, int(screensize[0]*.15), int(screensize[1]*.05), 0, 0, 0x0001)
    pygame.display.set_caption(title, title)
    return window_size, window

window_size, window = initiate_window()
SetWindowPos = windll.user32.SetWindowPos

# PYGAME -- Font Generator
font_tahoma = {}
for sizes in range(10, 41):
    try:
        font_tahoma[sizes] = pygame.font.Font("tahoma.ttf", sizes)
    except:
        print "FONT ERROR: Unable to find user font."
        font_tahoma[sizes] = pygame.font.SysFont('tahoma', sizes)

# --- Objects
class Object(object):
    pass
IMG = Object()
IMG.count = 0
Window = Object()
Mouse = Object()
Grid = Object()
Screen = Object()

class Draw:
    def __init__(self, total, x, y, size, zoom):
        self.total = total
        self.x = x
        self.y = y
        self.size = size
        self.zoom = zoom
Draw.x = 0
Draw.y = 0
Draw.size = 128
Draw.zoom = 0
Draw.angle1 = 2
Draw.angle2 = 4
Draw.errors = []

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.x = y
Camera.x = -7
Camera.y = -1

class Block:
    def __init__(self, terrain, height):
        self.terrain = terrain
        self.height = height
Block.terrain = {}; Block.height = {} # dictionary objects used for blocks' information
Grid.size = 64

for x in range(-Grid.size, Grid.size+1):
    for y in range(-Grid.size, Grid.size+1):
        randomTerrain = random.randint(0, 1000)
        if randomTerrain <= 100:
            Block.terrain[x, y] = "Water"
            Block.height[x, y] = 0
        elif randomTerrain <= 200:
            Block.terrain[x, y] = "Rocky"
            Block.height[x, y] = random.randint(80, 120)
        elif randomTerrain <= 900:
            Block.terrain[x, y] = "Grass"
            Block.height[x, y] = random.randint(5, 50)            
        else:
            Block.terrain[x, y] = "Dirt"
            Block.height[x, y] = random.randint(5, 50)            
        
for x in range(-5, 5):
    for y in range(-5, 5):
        Block.terrain[x, y] = "Urban"
        Block.height[x, y] = 75

# Windows screen modes
Screen.mode = 15
Screen.current = 7
Screen.max = 0
def screen_modes(self):
    Screen = self
    Screen.available = {}
    Screen.size = {}
    if (Screen.max - Screen.current < 1):
        Screen.current = 6
    else:
        Screen.current += 1
    try:
        Screen.available = pygame.display.list_modes() 
        for modes in range(1, 100):
            Screen.available[modes]
    except IndexError:
        Screen.max = modes-1
        Screen.mode = Screen.max-Screen.current
        window_size = (Screen.available[Screen.mode][0], Screen.available[Screen.mode][1])
        print "Screen mode #", Screen.mode, "--", window_size, "--", Screen.current
        window = pygame.display.set_mode(window_size,HWSURFACE|DOUBLEBUF|RESIZABLE)
        return window_size, window

# Look for image files
def FindImages():
    current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    print "CURR DIRECTORY:", current_directory, '\n'
    image_files = []
    try:
        types = ('*.png', '*.bmp', '*.pic', '*.jpeg', '*.jpg', '*.ico')
        for extension in types:
            file_found = glob.glob(current_directory + '\images\\' + extension)
            for files in file_found:
                if len(files) > 0:
                    image_files += [files]
    except Exception as error:
        exc_type, exc_obj, tb = sys.exc_info(); lineno = tb.tb_lineno
        print '\n', "FindImage Error on line #", lineno, "--", '\n', exc_type, '\n'
    print "IMAGES FOUND:", image_files, '\n'
    return image_files

# PYGAME -- Load images
def LoadImages(resize):
    IMG.list = []
    IMG.count = 0
    for pics in IMG.files:
        fileName, fileExtension = os.path.splitext(str(pics))
        start = fileName.index("images"); fileName = fileName[start+7:]
        __file__ = "iso_terra"    # <--- This code is necessary for a CX_freeze standalone app--otherwise you'll get an error.

        # Look for images in the "images" folder
        name = os.path.join(dirname(__file__), "images", fileName+fileExtension)
        name = os.path.join("images", fileName+fileExtension)
        print "IMAGE NAME:", name
        
        new_name = "IMG." + fileName
        setattr(IMG, str(fileName), pygame.image.load(name).convert_alpha())
        #exec(new_name + " = pygame.image.load(name).convert_alpha()")
        IMG.list += [str(fileName)]

# PYGAME -- Scale images
def image_resize():
    if Draw.size >= 256:
        Draw.size = 256
    if Draw.size <= 48:
        Draw.size = 48
    resize = Draw.size
    for images in IMG.list:
        new_name = "Draw." + images
        img_name = "IMG." + images
        setattr(Draw, str(images), pygame.transform.scale(eval(str(img_name)), (resize, resize)))
        #exec(new_name + " = pygame.transform.scale(" + str(img_name) + ", (resize, resize))")

# PYGAME -- Grid/Blocks draw information 
def grid_paramaters(self):
    win_sizeX = self[0]; win_sizeY = self[1]

IMG.files = FindImages()
LoadImages(Draw.size)
image_resize()

# PYGAME -- FPS and Game Speed
clock = pygame.time.Clock()
Grid.tempo = 0
tempo_switch = False
earthquake_mode = False

pygame.key.set_repeat(100, 50)
previous_key = 0
Draw.areaX = 5
Draw.areaY = 5
Draw.rangeY = 8

# Use a timer to control FPS.
timer_event = pygame.USEREVENT
fps = 30
pygame.time.set_timer(timer_event, int(2000 / fps))

# PYGAME -- Game loop begins
while True:
    window.fill((0, 0, 0))    
    clock.tick(fps) # FPS
    current_time = str(int(time.time()))
    
    # pygame.time clock
    Grid.clock = pygame.time.get_ticks()/1000
    Grid.clock += int(Grid.clock/Grid.clock)
    
    # pygame clock used for animations
    if tempo_switch == False:
        Grid.tempo += pygame.time.get_ticks()/pygame.time.get_ticks()*50
    else:
        Grid.tempo -= pygame.time.get_ticks()/pygame.time.get_ticks()*50

    if Grid.tempo > 1500: # change this number to adjust animation speed
        Grid.tempo = 1500 # change this number to adjust animation speed
        tempo_switch = True
    elif Grid.tempo <= 0:
        Grid.tempo = 0
        tempo_switch = False
    
    # get mouse position
    (Mouse.x, Mouse.y) = pygame.mouse.get_pos()

    # pygame window objects
    Window.sizeX = window_size[0]; Window.sizeY = window_size[1]
    Draw.centerX = int((Window.sizeX/2) - Draw.size/2)
    Draw.centerX = int((Window.sizeX/2) - Draw.size/2)

    # mouse edge scrolling
    if Grid.tempo %200 == 0:
        if Mouse.y <= 100: # scroll up
            Camera.y -= 1    
        if Mouse.y >= Window.sizeY - 100: # scroll down
            Camera.y += 1
        if Mouse.x < 100: # scroll left
            Camera.x -= 2
            Camera.y += 1
        if Mouse.x >= Window.sizeX - 100: # scroll right
            Camera.x += 2
            Camera.y -= 1
    
    # stop camera from going past the edge of the grid
    if Camera.x < -Grid.size-5:
        Camera.x = -Grid.size-5
    if Camera.x > Grid.size-10:
        Camera.x = Grid.size-10
    if Camera.y < -Grid.size:
        Camera.y = -Grid.size
    if Camera.y > Grid.size-5:
        Camera.y = Grid.size-5
    
    # isometric grid objects
    Draw.startX = 0
    Draw.startY = 0
    Draw.endX = Window.sizeX
    Draw.endY = Window.sizeY
    RangeExtend = True
    
    # Start the drawing loop for isometric grid
    Grid.mouse = False
    for Grid.y in range(-Draw.rangeY, Draw.areaY):    
        for Grid.x in range(-1, Draw.areaX):
            loopX = Grid.x + int(Camera.x)
            loopY = Grid.y + int(Camera.y)
            
            if loopY != 0:
                loopX += loopY  # Cycle to the next column
            loopY = loopY*-1
            
            # determine how the blocks line up next to each other using angle objects
            drawX = int((Draw.size*Grid.x)/2.0)
            drawY = int(Draw.size/Draw.angle1)*Grid.y + int((Draw.size*Grid.x)/Draw.angle2)

            # Check if mouse cursor is hovering over the block
            if Grid.mouse == False:
                if Mouse.x in range(drawX+int(Draw.size/5), drawX+int(Draw.size*.6)):
                    if Mouse.y in range(drawY, drawY+int(Draw.size*0.5)):
                        Grid.mouse = (loopX, loopY)
            
            # adjust the draw area for the grid so that it doesn't draw too many, or too few blocks to cover window
            if Grid.y == Draw.areaY-1:
                if drawY > Window.sizeY+Draw.size:
                    Draw.areaY -= 1
                else:
                    Draw.areaY += 1
            if Grid.x == Draw.areaX-1:
                if drawX > Window.sizeX+Draw.size:
                    Draw.areaX -= 1
                else:
                    Draw.areaX += 1

            # check if blocks are being drawn in upper right hand corner
            if drawX in range(Window.sizeX, Window.sizeX+Draw.size):
                if drawY in range(-Draw.size, 0):
                    RangeExtend = False
                    pygame.draw.rect(window, (40,40,40), (drawX, drawY, drawX+5, drawY+5))
            
            # draw the blocks to the pygame window using draw information
            if drawX in range(-Draw.size, Window.sizeX+Draw.size) and drawY in range(-Draw.size, Window.sizeY+Draw.size):
                try:
                    height = Block.height[loopX, loopY]
                    terrain = Block.terrain[loopX, loopY]
                    drawY -= int(height/5)
                    
                    if earthquake_mode is True:
                        drawY += random.randint(-3, 3)
                    
                    # mouse hover select box
                    if Grid.mouse == (loopX, loopY):
                        # make hovered block bob up and down
                        bobX = int((Grid.tempo/1000) * Draw.size/4) - int(height/4)
                        hoverX = drawX; hoverY = drawY
                        drawY = drawY - bobX
                                        
                    # Terrain types
                    if terrain == "Water":
                        Block.height[loopX, loopY] = 0
                        if Grid.tempo <= 300:
                            block_type = Draw.cube_water1
                        elif Grid.tempo <= 700:
                            block_type = Draw.cube_water2
                        else:
                            block_type = Draw.cube_water3
                            
                    elif terrain == "Urban":
                        Block.height[loopX, loopY] = 0
                        ranUrban = random.randint(1, 100)
                        if ranUrban == 1:
                            block_type = Draw.cube_urban1
                        else:
                            block_type = Draw.cube_urban2      
                        
                    if terrain == "Dirt":
                        block_type = Draw.cube_dirt
                    elif terrain == "Grass":
                        block_type = Draw.cube_grass
                    if terrain == "Rocky":
                        block_type = Draw.cube_rocky                            
                    window.blit(block_type, (drawX, drawY)) # blit block to pygame window
                    
                    # mouse hover select box
                    if Grid.mouse == (loopX, loopY):
                        window.blit(Draw.outline_cube0, (drawX, drawY-1))
                        
                    # mouse hover text
                    if Grid.mouse != False:
                        text_image = font_tahoma[20].render(str(Grid.mouse),  5, (240, 240, 240))
                        window.blit(text_image, (hoverX+10, hoverY+20))
                    
                    # Draw location numbers on blocks
                    if loopX %5 == 0 and loopY %5 == 0:
                        block_num = font_tahoma[20].render(str(loopX) + ", " + str(loopY), 5, (200, 200, 200))
                        window.blit(block_num, (drawX+int(Draw.size/6), drawY+int(Draw.size/10)))
                        
                except Exception as error:
                    exc_type, exc_obj, tb = sys.exc_info(); lineno = tb.tb_lineno
                    Draw.errors += ["Game Loop Error on line " + str(lineno) + " -- " + str(error) + " -- " + str(exc_type)]
                    if len(Draw.errors) > 5:
                        del(Draw.errors[0])
    
    # Blit text information to pygame window
    pygame.draw.rect(window, (0,0,0), (5, 5, 190, 165)) # blit black rect
    
    image_count = font_tahoma[20].render("Draw.size: " + str(Draw.size), 5, (240, 240, 240))
    window.blit(image_count, (10, 10))

    text_string = "Camera: " + str(Camera.x) + ", " + str(Camera.y)
    text_image = font_tahoma[20].render(text_string,  5, (240, 240, 240))
    window.blit(text_image, (10, 35))
    
    text_image = font_tahoma[20].render("Clock: " + str(int(Grid.clock)) + " sec ",  5, (240, 240, 240))
    window.blit(text_image, (10, 60))

    text_image = font_tahoma[20].render("Grid.tempo: " + str(int(Grid.tempo)),  5, (240, 240, 240))
    window.blit(text_image, (10, 85))
    
    text_image = font_tahoma[20].render("FPS: " + str(int(clock.get_fps())),  5, (240, 240, 240))
    window.blit(text_image, (10, 110))
    
    text_image = font_tahoma[18].render("Earthquake: " + str(earthquake_mode),  5, (240, 0, 0))
    window.blit(text_image, (10, 135))
    
    # blit text of errors to pygame window if error list is not empty
    if Draw.errors != []:
        errorY = Window.sizeY-10
        for errors in range(len(Draw.errors)):
            errorY -= 20
            error_display = font_tahoma[20].render(str(Draw.errors[errors]),  5, (240, 240, 240))
            window.blit(error_display, (10, errorY))
        Draw.errors = []
    
    # PYGAME -- Get keyboard and mouse events
    pygame.event.pump()    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(); pygame.quit(), quit()
            
        elif event.type == KEYDOWN:
            KeyPress = pygame.key.get_pressed()
            if KeyPress[pygame.K_ESCAPE]:
                sys.exit(); pygame.quit(), quit()
            elif KeyPress[pygame.K_MINUS]: # zoom out
                Draw.size -= 8
                image_resize()
            elif KeyPress[pygame.K_EQUALS]: # zoom in
                Draw.size += 8
                image_resize()
                
            elif KeyPress[K_UP] or KeyPress[K_w]: # scroll up
                Camera.x += 1
                Camera.y -= 1
            elif KeyPress[K_DOWN] or KeyPress[K_s]: # scroll down
                Camera.x -= 1
                Camera.y += 1
            elif KeyPress[K_LEFT] or KeyPress[K_a]: # scroll left
                Camera.x -= 1
            elif KeyPress[K_RIGHT] or KeyPress[K_d]: # scroll right
                Camera.x += 1
                
            elif KeyPress[K_F7]: # screenshot
                pygame.image.save(window, "screenshot.png")
            elif KeyPress[K_F11]: # Change screen mode
                window_size, window = screen_modes(Screen)
                SetWindowPos = windll.user32.SetWindowPos        
                
        elif pygame.mouse.get_pressed()[1]: # scroll wheel click
            print "Mouse Wheel Click"
        
        elif  pygame.mouse.get_pressed()[0]: # left mouse click
            if Mouse.x in range(10, 150) and Mouse.y in range(135, 160):
                earthquake_mode = not earthquake_mode
        
        # Scroll wheel movement
        elif (event.type == pygame.MOUSEBUTTONDOWN):
            if event.button == 4:
                Draw.size += 8              
                image_resize()
            if event.button == 5:
                Draw.size -= 8               
                image_resize()

    # PYGAME -- Blit pygame images
    if Grid.tempo %10 == 0:
        pygame.display.flip()

        if RangeExtend == True:
            Draw.rangeY += 1
        else:
            Draw.rangeY -= 1
