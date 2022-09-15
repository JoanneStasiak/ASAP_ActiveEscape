    # ASAP Active Escape Task - Practice Trials
# Jo Stasiak
#2021
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Practice runs for the Active Escape Task

Participants will be completing two practice trials - one controllable, perceptible trial and one uncontrollable, unpleasant trial.
'''
from __future__ import absolute_import, division
from psychopy import locale_setup
from psychopy import prefs
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np
from numpy import (sin, cos, tan, log, log10, pi, average,sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os
import sys
import random
import re
import csv
import pandas as pd
from numpy.random import choice
from psychopy.hardware import keyboard
import ctypes

#Use a joystick and be able to use the buttons on it
from psychopy.hardware import joystick
from psychopy.experiment.components.joyButtons import virtualJoyButtons as virtualjoybuttonslib

from math import *

#Following packages are for the MCCULW Digital Port, which is used to send the shocks from the stimulus computer to Biopac
from mcculw import ul
from mcculw.enums import InterfaceType
from mcculw.enums import CounterChannelType, DigitalPortType, DigitalIODirection
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo
import tkinter as tk
from mcculw.device_info import DaqDeviceInfo
from pyglet.window import key
from mcculw.enums import ULRange


keyState=key.KeyStateHandler()
prefs.general['audioLib']=['pyo']
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
psychopyVersion = '2021.1.2'
expName = 'ASAP Active Escape'
expInfo = {'Participant*': ''}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()
expInfo['date'] = data.getDateStr()
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['Participant*'], expName, expInfo['date'])
pid=expInfo["Participant*"]

thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,savePickle=True, saveWideText=True,dataFileName=filename)
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)

endExpNow = False
frameTolerance = 0.001

win = visual.Window(size=(1295, 980),pos=(270,80), fullscr=False, screen=1, winType='pyglet', allowGUI=True, allowStencil=True,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',blendMode='avg', useFBO=True, units='height')
win.setMouseVisible(False)

expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0

#Set up the digital port:
board_num = 0 #Get the first port recognized (there should only be one)
daq_dev_info = DaqDeviceInfo(board_num)#get information about the board
ao_info = daq_dev_info.get_ao_info()
num_chans = min(ao_info.num_chans, 4)#get the number of channels the board has - you might have to look at the MCCULW documentation for the parameters
num_points = num_chans
ao_range = ULRange.BIP10VOLTS#Get the range of voltage that can be sent, ours is +/- 10V
ul.a_out(board_num,0, ao_range, data_value =2000)#Set the voltage of the board - data_value=2000 is the equivalent of 0 volts

# Initialize variables
InstructionsClock = core.Clock()
isiClock = core.Clock()
instructionsText = visual.TextStim(win=win, text='', height=0.045, pos=[0,0], wrapWidth=1.125)
countdownText = visual.TextStim(win=win, text='', height=0.1, pos=[0,0])
isi = visual.TextStim(win=win, text = '+', height = 0.07, pos=[0,0])
text =visual.TextStim(win=win, text = '+', height = 0.07, pos=[0,0])
interRun = visual.TextStim(win=win, text = '', height = 0.045, pos=[0,0], wrapWidth=1.125)
#background colors
background = visual.Rect(win=win, width=(1.95, 1.95)[0], height=(1.35, 1.35)[1], ori=0.0, pos=(0, 0),lineWidth=1.0,  colorSpace='rgb',  lineColor='black', fillColor='', opacity=0.99, interpolate=True)
cue = visual.TextStim(win=win, text='', height=0.45, pos=[0,0.05], color="black")
countText=visual.TextStim(win=win, text='', height = 0.42, pos=[0,0.05], color="black")
targetPlace = visual.Circle(win=win, radius=0.0715, edges=99, lineWidth=1.8, lineColor="black", fillColor="white", pos=[0,0], size=0.655)
bgEx = visual.Rect(win=win, width=0.22, height=0.22, fillColor='white', pos=[0,-0.03])
code = 0

#Set up the joystick
nJoys = joystick.getNumJoysticks()#number of joysticks connected
print("nJOys = ", nJoys)
id = 0
joy = joystick.Joystick(id)#call the joystick 'joy' and identify it as the first one found
nAxes = joy.getNumAxes() #get the number of axes supported
joyClock = core.Clock()

#Set up the joystick buttons
button_resp = type('', (), {})()
button_resp.device_number = 0
button_resp.device = joystick.Joystick(0)
button_resp.status = None
button_resp.clock = core.Clock()
button_resp.numButtons = button_resp.device.getNumButtons()

defaultKeyboard = keyboard.Keyboard()
defaultKeyboard = keyboard.Keyboard()


#Create a function to send shocks, intialize at 0V
curIntensity = 2000
def deliverShock(intensity=curIntensity):#have the voltage be the function parameter
    #Deliver shock
    ul.a_out(board_num,0, ao_range, data_value =intensity)#send the shock with the given intensity
    core.wait(0.02)
    #Reset ShockPort
    ul.a_out(board_num,0, ao_range, data_value =2000)#set back to 0V

# Intro Loop conditions
textArray = ["You will now be completing a series of trials involving the possible administration of shocks.",\
    "In CONTROLLABLE trials, you will be able to make a motor response to try to avoid the shock. \n\nIn UNCONTROLLABLE trials, you will *not* be able to avoid the shock.",\
    "In all trials, you will see a countdown of 18 seconds. Then, you will have just under 1 second to use the joystick to move a center cursor, a small triangle, to a target circle which will be randomly placed in one of the four corners of the screen.",\
    "When getting ready to make the motor response, try to hover your thumb over or next to the thumbstick rather than resting it directly on top of the thumbstick." ,\
    "After each trial, you will be responding to two questions about your emotional experience. \n\nFor both questions, you will use the buttons on the joystick to make your response.\n\nYou will have 5 seconds to respond to each question.",\
    "You will be completing 7 blocks of these trials. \n\nWe will be checking in with you after each block.", \
    "It is very important that you stay as still as possible throughout the task. \n\nDo you have any questions before we begin?",\
    "Let's go through a couple of practice trials!"]

fix = visual.Polygon(win=win, edges=3, size=(0.0285,0.0285), fillColor="white",lineColor='black',lineWidth=2.26, pos=[0,0])#the triangular cursor used by the joystick in the motor response
space = keyboard.Keyboard()
moveKeys = keyboard.Keyboard()
ratKeys = keyboard.Keyboard()
qText = visual.TextStim(win=win, text='',pos=(0, 0.2), height=0.058, wrapWidth=.95, color='white');
qInst = visual.TextStim(win=win, text="Please use the buttons 1, 2, 3, or 4 to respond.", pos=(0,0.39), height=0.037, wrapWidth=1.7, color="white");
interRun=visual.TextStim(win=win, text='', pos=(0,0), height=0.06, wrapWidth=1.1, color='white')
trialTypeCorner = visual.TextStim(win=win, text='', height=0.0445, pos=[0.35, -0.355], color="black")
#Create a 'scale' for the two emotion questions
horLine = visual.Line(win=win, start=(-[0.75, 0.75][0]/2.0, 0), end=(+[0.75, 0.75][0]/2.0, 0),
    ori=0, pos=(0, -0.06), lineWidth=9,  colorSpace='rgb',  lineColor='white', fillColor='white',
    opacity=1, depth=0.0, interpolate=True)
tick1 = visual.Line(win=win, start=(-[0.1, 0][0]/2.0, 0), end=(+[0.1, 0][0]/2.0, 0),
    ori=90, pos=(-0.35, -0.06), lineWidth=5, size=0.8, colorSpace='rgb',  lineColor='white', fillColor='white',
    opacity=1, depth=0.0, interpolate=True)
tick2 = visual.Line(win=win, start=(-[0.1, 0][0]/2.0, 0), end=(+[0.1, 0][0]/2.0, 0),
    ori=90, pos=(-0.115, -0.06), lineWidth=5, size=0.8, colorSpace='rgb',  lineColor='white', fillColor='white',
    opacity=1, depth=0.0, interpolate=True)
tick3 = visual.Line(win=win, start=(-[0.1, 0][0]/2.0, 0), end=(+[0.1, 0][0]/2.0, 0),
    ori=90, pos=(0.115, -0.06), lineWidth=5,size=0.8,  colorSpace='rgb',  lineColor='white', opacity=1, depth=0.0, interpolate=True)
tick4 = visual.Line(win=win, start=(-[0.1, 0][0]/2.0, 0), end=(+[0.1, 0][0]/2.0, 0),
    ori=90, pos=(0.35, -0.06), lineWidth=5, size=0.8, colorSpace='rgb',  lineColor='white', opacity=1, depth=0.0, interpolate=True)
QuestionScale = visual.RatingScale(win=win, scale=None, showValue=False, showAccept=False, textColor="darkGrey", skipKeys=None, stretch=2.0, tickHeight=-1.0)
num1 = visual.TextStim(win=win, text='1',pos=(-0.35, -0.13), height=0.06, wrapWidth=1.8, color='white');
num2 = visual.TextStim(win=win, text='2',pos=(-0.115, -0.13), height=0.06, wrapWidth=1.8, color='white');
num3 = visual.TextStim(win=win, text='3',pos=(0.115, -0.13), height=0.06, wrapWidth=1.8, color='white');
num4 = visual.TextStim(win=win, text='4',pos=(0.35, -0.13), height=0.06, wrapWidth=1.8, color='white');

#Text for the left and right anchors of the scales
LeftAnchor = visual.TextStim(win=win, text='',pos=(-0.38, -0.235), height=0.045, wrapWidth=0.3, color='white');
RightAnchor = visual.TextStim(win=win, text='',pos=(0.385, -0.235), height=0.045, wrapWidth=0.3, color='white');

button_resp.oldButtonState = button_resp.device.getAllButtons()[:]
button_resp.keys = []
button_resp.rt = []


questions = ["How intense was your emotional experience in this trial?","How certain are you of your answer?"]
qAnchorsLeft = ["Not at all","Not certain"]
qAnchorsRight=["Extremely", "Completely certain"]
print("y joy: ", joy.getY())
print("x joy: ", joy.getX())

globalClock = core.Clock()
globalClock.reset()
space=keyboard.Keyboard()
def introFunc(text):
    global globalClock
    win.setMouseVisible(False)
    continueRoutine = True
    if defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    instructionsText.setText(text)
    instructionsText.draw()
    win.flip()
    event.waitKeys(keyList='space')
    win.flip()
    core.wait(0.1)
    thisExp.addData("Instructions", instructionsText.text)
    thisExp.nextEntry()

isiOffsetTime=[0]
isiClock=core.Clock()
routineTimer = core.CountdownTimer()
def isiFunc(timeVar, textVar):
    continueRoutine = True
    isiClock.reset()
    isiTimeStart=isiClock.getTime()
    win.setMouseVisible(False)
    text.setText(textVar)
    text.draw()
    isiTimeStartGlobal=globalClock.getTime()
    win.flip()
    if defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    core.wait(timeVar)
    isiTimeEnd=isiClock.getTime()
    win.flip()
    isiTimeEndGlobal=globalClock.getTime()
    thisExp.addData('isiTimeStartGlobal', isiTimeStartGlobal)
    thisExp.addData('isiTimeEndGlobal', isiTimeEndGlobal)
    thisExp.addData('isi Onset', isiTimeStart)
    thisExp.addData("isi Duration", isiTimeEnd)
    thisExp.addData("isi Text", text.text)
    thisExp.addData("isi Offset", isiOffsetTime[-1])

triggerKey = keyboard.Keyboard()
triggerClock=core.Clock()
joyClock = core.Clock()


pid=expInfo["Participant*"]
def pracRun(trialsNumArray, trialsTypeArray):
    global code
    prac=[1]
    for i in prac:
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        isiArray=[4.0000,5.0000,6.0000]
        isiFunc(2.00, '+')
        trialsArray = trialsTypeArray# we will only have them do two practice trials
        trialsNum=trialsNumArray
        for z in trialsNum:
            win.setMouseVisible(False)
            continueRoutine=True
            trialClock = core.Clock()
            trialClock.reset()
            randomTrialType = random.choice(trialsArray)
            randomTrialSelect = randomTrialType
            trialsArray.remove(randomTrialSelect)
            if randomTrialSelect == 'a': #Controllable perceptible
                cue.setText("O")
                background.setFillColor("blue")
                trialType="Controllable Perceptible"
                cue.setColor("#FF9C0F")
                countText.setColor("white")
                trialTypeCorner.setColor("white")
                eventCode = 10 # channels 29 & 31
            if randomTrialSelect == 'd': #Uncontrollable Aversive
                background.setFillColor("#ff8080")
                trialType="Uncontrollable Unpleasant"
                cue.setText("X")
                cue.setColor("#002375")
                countText.setColor("black")
                trialTypeCorner.setColor("black")
                eventCode = 5 # channels 28, 30
                win.setMouseVisible(False)
            t = trialClock.getTime()
            y = t
            background.draw()
            cue.draw()# show the cue, X or O
            thisExp.addData("Full Trial Onset", globalClock.getTime())
            win.flip()
            cueOnset=trialClock.getTime()
            cueOnsetGlobal = globalClock.getTime()
            cueOffset=0
            core.wait(1.0)
            win.flip()
            cueOffset=trialClock.getTime()
            cueOffsetGlobal = globalClock.getTime()
            thisExp.addData('Cue Onset', cueOnset)
            thisExp.addData('Cue Offset', cueOffset)
            thisExp.addData('Cue Onset Global', cueOnsetGlobal)
            thisExp.addData('Cue Offset Global', cueOffsetGlobal)
            for y in range(18,0,-1):#Start the countdown from 18 to 1
                if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                    core.quit()
                countTimer=core.Clock()
                countTimer.reset()
                win.setMouseVisible(False)
                continueRoutine=True
                if randomTrialSelect == 'a':#a = Controllable, Perceptible trial
                    background.setFillColor("blue") #bright blue background
                    trialType="Controllable Perceptible"
                    countText.setColor("white")
                    trialTypeCorner.setColor("white")
                if randomTrialSelect=='d':# d = Uncontrollable, Unpleasant trial
                    background.setFillColor("#ff8080") # light red background
                    background.setOpacity(0.9)
                    trialType="Uncontrollable Unpleasant"
                    countText.setColor("black")
                    trialTypeCorner.setColor("black")

                while continueRoutine:
                    background.setAutoDraw(True)
                    countText.setText(str(y))
                    countText.setAutoDraw(True)
                    countTextOnsetGlobal=globalClock.getTime()
                    countTextOnset=countTimer.getTime()
                    countTextOffset=''
                    trialTypeCorner.setText(trialType)
                    trialTypeCorner.setAutoDraw(True)
                    if countTimer.getTime() > 0.9-frameTolerance:
                        trialTypeCorner.setAutoDraw(False)
                        background.setAutoDraw(False)
                        continueRoutine=False
                    if countTimer.getTime() > 0.65-frameTolerance:#Show the text for less time than the background so there is a flashing effect
                        countText.setAutoDraw(False)
                        countTextOffsetGlobal=globalClock.getTime()
                    if continueRoutine:
                        win.flip()
                thisExp.addData("Count Text Onset", countTextOnset)
                thisExp.addData('Count Text Offset', countTextOffset)
                thisExp.addData("Count Text Onset Global", countTextOnsetGlobal)
                thisExp.addData('Count Text Offset Global', countTextOffsetGlobal)
            trialTimeOffset=trialClock.getTime()
            trialTimeOffsetGlobal=globalClock.getTime()
            thisExp.addData("Full Trial Timer Offset Global", trialTimeOffsetGlobal)
            thisExp.addData("Full Trial Timer Offset", trialTimeOffset)
            trialClock.reset()

            #Begin the motor response
            continueRoutine = True
            trialType=[]
            targetArrays = [1,2,3,4]#for the random placement of the target circle
            shockStat=0
            xposArray=[]#Create arrays for the x,y coordinates in native vs translated space
            yposArray=[]
            succArray=[]
            targetClock=core.Clock()
            joyClock=core.Clock()
            choiceKeys = keyboard.Keyboard()
            motorStatus = ""
            motorResponseClock=core.Clock()
            motorResponseClock.reset()
            routineTimer.add(1.40500)
            background.setFillColor("blue")
            trialType="Controllable Perceptible"
            if randomTrialSelect=='d':
                background.setFillColor("#ff8080")
                trialType="Uncontrollable Unpleasant"
            targetClock.reset()
            randomTarget = random.choice(targetArrays)
            if randomTarget== 1:
                targetPlace.setPos((-0.582, 0.43))#Set the circle to be in the top left of the screen
            if randomTarget == 2 :
                targetPlace.setPos((0.582, 0.43))#Circle is set for the top right
            if randomTarget == 3:
                targetPlace.setPos((0.582, -0.44))#Circle is set for the bottom left
            if randomTarget == 4:
                targetPlace.setPos((-0.582, -0.44))#Circle is set for the bottom right

            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            continueRoutine=True
            joyClock.reset()
            trialStart=joyClock.reset()
            joyTimeStart=''#will set this to a clock time later
            code+=1
            starty = joy.getY()#get the initial y position of the joystick
            startx = joy.getX()#get the initial x position of the joystick
            xCoor=0
            yCoor=0

            while continueRoutine:
                background.draw()
                win.setMouseVisible(False)
                targetPlace.draw()
                fix.draw()
                motorResponseGlobal = globalClock.getTime()
                if joy.getY() != starty or joy.getX() != startx:
                    joyTimeStart = joyClock.getTime()
                if joy.getX()>startx + 0.0002:#if the joystick axis moved past the intial position - used to protect against drift
                    xCoor += 0.0290#this controls the speed of the joystick when moving left - make this number smaller if you want the cursor to move slower
                if joy.getX()<-startx - 0.0002:
                    xCoor -= 0.0290#moving the joystick right on the x axis
                if joy.getY() >starty + 0.0002:
                    yCoor -= 0.0290#for some reason our y axis is mirrored, so this moves the cursor DOWN
                if joy.getY() <-starty - 0.0002:
                    yCoor += 0.0290#move the cursor UP
                if yCoor <= (-0.47):#limit the cursor so it doesn't run off the screen
                    yCoor=-0.47#if it reaches this coordinate, stop it from moving any more down
                if yCoor >= 0.47:
                    yCoor=0.47#stop it from moving upwards
                if xCoor <= -0.65:
                    xCoor=-0.65#stop the cursor from moving left
                if xCoor >=0.65:
                    xCoor=0.65#stop the cursor from moving right
                if continueRoutine:
                    win.flip()
                xposition = round(xCoor, 3)#round off the x coordinates so we don't get massive floats in our data file
                yposition = round(yCoor, 3)
                xposArray.append(xposition)#update these arrays at every frame to get exact positions
                yposArray.append(yposition)
                xCoorArray.append(xCoor)
                yCoorArray.append(yCoor)
                fix.setPos((xCoor,yCoor))#update the cursor at every frame

                joyTimeEnd=''
                if fix.overlaps(targetPlace): #if the cursor overlaps with the target circle...
                    succArray.append("Success") #successful motor response!

                if fix.overlaps(targetPlace) == False:
                    succArray.append("Fail")#failed motor response
                if joyClock.getTime() >= 0.940:#This is the amount of time participants have to make the motor response - 940 ms
                    continueRoutine=False
                    background.setAutoDraw(False)
                    win.flip()
                    motorResponseEndGlobal=globalClock.getTime()
            if "Success" in succArray:
                motorStatus="Success"
            if "Success" not in succArray:
                motorStatus="Fail"


            #Do they receive a shock?
            # 0  = no shocks
            # 1 = perceptible shock
            # 2 = unpleasant shock
            trialEnd=joyClock.getTime()
            if (trialType=="Controllable Perceptible") and motorStatus == "Success":#If successful response in a controllable trial...
                shockStat = 0#do not give a shock
            if (trialType=="Uncontrollable Unpleasant"):#If it is an UNCONTROLLABLE, unpleasant trial
                shockStat = 2 #give them a shock regardless of their performance
            if (trialType=="Controllable Perceptible") and motorStatus == "Fail":"Fail":#Failure in controllable perceptible trial...
                shockStat = 1#give a perceptible shock
            if shockStat == 0:
                print("do not give shock")
            if shockStat == 1:
                print("give benign shock")
                deliverShock(perShock)# send a perceptible shock
                print('sendTrig')
                core.wait(0.5)
            if shockStat == 2:
                print("Give averse shock")
                deliverShock(unpShock)# send an unpleasant shock
                print('sendTrig')
                core.wait(0.5)
            motorResponseEndGlobal = globalClock.getTime()
            thisExp.addData('Shock Status', shockStat)
            thisExp.addData('Joy Movement Started', joyTimeStart)
            thisExp.addData('Success Joy RT', joyTimeEnd)
            thisExp.addData('Motor Status', motorStatus)
            thisExp.addData('Motor Response Start Global', motorResponseGlobal)
            thisExp.addData('Motor Response End Global', motorResponseEndGlobal)
            thisExp.addData('Trial Start', trialStart)
            thisExp.addData('Trial End', trialEnd)
            continueRoutine=True
            isiFunc(2.000, '+')#short fixation before questions
            for x,y,z in zip(questions,qAnchorsLeft,qAnchorsRight):
                continueRoutine = True
                routineTimer.add(4.50)
                #set the colors of the numbers on the scale to white bc they will be changing color later
                num3.setColor("white")
                num1.setColor("white")
                num2.setColor("white")
                num4.setColor("white")
                buttonArray=[]
                ratingSelection = 0
                QuestionScale.reset()
                Q1Clock = core.Clock()
                Q1Clock.reset()
                QuestionScale.reset()
                Q1Components = [tick1, tick2, tick3, tick4,  horLine, num1, num2, num3, num4, button_resp,LeftAnchor, RightAnchor, qText]
                for i in Q1Components:
                    i.tStart = None
                    i.tStop = None
                    i.tStartRefresh = None
                    i.tStopRefresh = None
                    if hasattr(i, 'status'):
                        i.status = NOT_STARTED
                    if hasattr(i, 'setAutoDraw'):
                        i.setAutoDraw(True)
                frameN = -1
                while continueRoutine:
                    win.setMouseVisible(False)
                    LeftAnchor.setText(y)#the two questions have different anchors
                    RightAnchor.setText(z)
                    qText.setText(x)
                    qOnsetTime=Q1Clock.getTime()
                    qOnsetGlobal = globalClock.getTime()
                    waitOnFlip = False
                    if button_resp.status == NOT_STARTED:#intialize the joystick buttons to make a response
                        button_resp.frameNStart = frameN
                        button_resp.status = STARTED
                        win.callOnFlip(button_resp.clock.reset)
                    if button_resp.status == STARTED:
                        button_resp.newButtonState = button_resp.device.getAllButtons()[:]
                        button_resp.pressedButtons = []
                        button_resp.releasedButtons = []
                        button_resp.newPressedButtons = []
                        if button_resp.newButtonState != button_resp.oldButtonState:
                            button_resp.pressedButtons = [i for i in range(button_resp.numButtons) if button_resp.newButtonState[i] and not button_resp.oldButtonState[i]]
                            button_resp.releasedButtons = [i for i in range(button_resp.numButtons) if not button_resp.newButtonState[i] and button_resp.oldButtonState[i]]
                            button_resp.oldButtonState = button_resp.newButtonState
                            button_resp.newPressedButtons = [i for i in [0,1, 2, 3, 6, 7, 8, 9] if i in button_resp.pressedButtons]
                            #the joystick is set up a little weird such that it has 4 physical buttons that either correspond to the numbers 0,1,2,3 or 6,7,8,9
                            #Prior to the study we use the console to set the joystick to 0,1,2,3, but if we need to reset the console during the task, these buttons may also unintentially change value to 6,7,8,9, so we want to make sure the responses are recorded in case that happens
                            [logging.data("joystick_{}_button: {}".format(button_resp.device_number,i)) for i in button_resp.pressedButtons]
                        theseKeys = button_resp.newPressedButtons
                        if len(theseKeys) > 0:
                            button_resp.keys = theseKeys[-1]
                            button_resp.rt = button_resp.clock.getTime()
                            if button_resp.keys  == 0 or button_resp.keys  == 6:#if they answered '1'
                                num2.setColor("white")
                                num1.setColor("green")
                                num3.setColor("white")
                                num4.setColor("white")
                                ratingSelection = 1
                            if button_resp.keys  == 1 or button_resp.keys  == 7:#if they answered '2'
                                num3.setColor("white")
                                num1.setColor("white")
                                num2.setColor("green")
                                num4.setColor("white")
                                ratingSelection = 2
                            if button_resp.keys == 2 or button_resp.keys  == 8:#if they answered '3'
                                num3.setColor("green")
                                num2.setColor("white")
                                num4.setColor("white")
                                num1.setColor("white")
                                ratingSelection = 3
                            if button_resp.keys  == 3 or button_resp.keys  == 9:#if they answered '4'
                                num2.setColor("white")
                                num1.setColor("white")
                                num4.setColor("green")
                                num3.setColor("white")
                                ratingSelection = 4
                            print("button response: " ,button_resp.keys)
                    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                        core.quit()
                    if Q1Clock.getTime() >4.500:
                        continueRoutine=False
                        qOffsetGlobal = globalClock.getTime()
                    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                        core.quit()
                    if not continueRoutine:
                        break
                    continueRoutine = False
                    for thisComponent in Q1Components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break
                    if continueRoutine:
                        win.flip()
                for thisComponent in Q1Components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)

                qOffsetTime=Q1Clock.getTime()
            #reset the colors to white so they don't remain green for the second question
                num3.setColor("white")
                num1.setColor("white")
                num2.setColor("white")
                num4.setColor("white")
                routineTimer.reset()
                isiFunc(0.500, '+')
                thisExp.addData("Question Text", qText.text)
                thisExp.addData("Question Response", ratingSelection)
                thisExp.addData("Question RT", button_resp.rt)
                thisExp.addData("Question Onset Global", qOnsetGlobal)
                thisExp.addData("Question Offset Global", qOffsetGlobal)
    isiFunc(2.50, '+')
pracTrialsNumArray=[1,2]
trialsTypeprac=['a', 'd']

#Start the practice trials!
#We need to get the values of the perceptible and unpleasant shocks that were decided on during calibration
pid=expInfo["Participant*"]
with open("data\\" + str(pid) + "_UnpleasantCalibration_2.txt", 'r') as unp:#we want to use the shocks decided on in the second round of calibration
    lines = unp.readlines()
    unpShock = lines[-1].split('\t')[-1]
    print(unpShock)
unpShock=re.sub("[^0-9]", "", unpShock)#find the column called 'unpShock' and get the last value in it
unpShock=int(unpShock)
with open("data\\" + str(pid) + "_PerceptibleCalibration_2.txt", 'r') as per:
    lines = per.readlines()
    perShock = lines[-1].split('\t')[-1]
    print(perShock)
perShock=re.sub("[^0-9]", "", perShock)#find the column called 'perShock' and get the last value in it
perShock=int(perShock)

startExpTime=globalClock.getTime()

for i in textArray:
    introFunc(i)

endInst=globalClock.getTime()
isiFunc(2.00, '+')
startPrac=globalClock.getTime()
pracRun(pracTrialsNumArray, trialsTypeprac)
introFunc("Great job! \n\nPlease wait for the experimenter.")
