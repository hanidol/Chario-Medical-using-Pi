#!/usr/bin/python3
import pygame
from pygame.locals import *
pygame.init()


#define commands

STOP = 0x00
FORWARD_DIRECTION = 0x01
BACKWARD_DIRECTION = 0x02
LEFT_DIRECTION = 0x04
RIGHT_DIRECTION = 0x08
MOTORLEFT = 0x10
MOTORRIGHT = 0x20
SET_SPEED = 0x40

currentDirection = 0x00



carSpeed = 200
done = False
title = "Hello!"
width = 640
height = 400
screen = pygame.display.set_mode((width, height))
screen.fill((255, 255, 255))
clock = pygame.time.Clock()
pygame.display.set_caption(title)

#load images
down_off = pygame.image.load('images/down_off.gif')
down_on = pygame.image.load('images/down_on.gif')
left_on = pygame.image.load('images/left_on.gif')
left_off = pygame.image.load('images/left_off.gif')
right_on = pygame.image.load('images/right_on.gif')
right_off = pygame.image.load('images/right_off.gif')
up_on = pygame.image.load('images/up_on.gif')
up_off = pygame.image.load('images/up_off.gif')

import serial
ser = serial.Serial('/dev/ttyUSB0', 9600)


#show initally on the screen
def arrowsOff():
    screen.blit(down_off,(300,250))
    screen.blit(left_off,(230,180))
    screen.blit(right_off,(370,180))
    screen.blit(up_off,(300,110))


arrowsOff()
font=pygame.font.SysFont("monospace", 30)

def sendCommandToArduino():
    #send command drive with motor speed 0xA0
    checkSum = 0x01+currentDirection+0xA0
    ser.write((chr(0x01)+chr(currentDirection)+chr(0xA0)+chr(checkSum)).encode())

def showSpeed():
    screen.fill(pygame.Color("white"), (0, 0, 110, 40))
    scoretext=font.render("Speed:"+str(carSpeed), 1,(0,0,0))
    screen.blit(scoretext, (0, 0))

while not done:
    for event in pygame.event.get():
        if (event.type == QUIT):
            done = True
        elif(event.type == KEYDOWN):
            if (event.key == K_ESCAPE):
                done = True
            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                screen.blit(left_on,(230,180))
                print("Left");
                currentDirection|=LEFT_DIRECTION
                sendCommandToArduino()
            if keys[K_RIGHT]:
                screen.blit(right_on,(370,180))
                print("Right");
                currentDirection|=RIGHT_DIRECTION
                sendCommandToArduino()
            if keys[K_UP]:
                screen.blit(up_on,(300,110))
                print("Up");
                currentDirection|=FORWARD_DIRECTION
                sendCommandToArduino()
            if keys[K_DOWN]:
                screen.blit(down_on,(300,250))
                print("Down");
                currentDirection|=BACKWARD_DIRECTION
                sendCommandToArduino()
            if keys[K_LEFTBRACKET]:
                if(carSpeed>0):
                    carSpeed-=5
                print("Slowdown");
                showSpeed()
            if keys[K_RIGHTBRACKET]:
                carSpeed+=5
                showSpeed()
                print("faster")
        elif(event.type == KEYUP):
            if keys[K_LEFT]:
                screen.blit(left_off,(230,180))
                print("Left");
                currentDirection&=LEFT_DIRECTION
                sendCommandToArduino()
            if keys[K_RIGHT]:
                screen.blit(right_off,(370,180))
                print("Right");
                currentDirection&=RIGHT_DIRECTION
                sendCommandToArduino()
            if keys[K_UP]:
                screen.blit(up_off,(300,110))
                print("Up");
                currentDirection&=FORWARD_DIRECTION
                sendCommandToArduino()
            if keys[K_DOWN]:
                screen.blit(down_off,(300,250))
                print("Down");
                currentDirection&=BACKWARD_DIRECTION
                sendCommandToArduino()

    pygame.display.update()
    clock.tick(60)