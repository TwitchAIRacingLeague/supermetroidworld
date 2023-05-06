
#import pygame
from inputs import get_gamepad
import threading
from multiprocessing import Process
import socket
import struct
import time
import datetime
#import simpleaudio as sa
import json
import os
print ("input finished")
import sys

import retro
from datetime import datetime
import random
import itertools
import gzip

def normalize_data(data):
    for i in range(len(data)):
        data[i] = round(data[i])
    return data

main_game = 'SuperMarioWorld-Snes'
list_of_hacks = ['SuperMetroid-Snes']

def save_state_to_file(env, name="start.state"):
    
    content = env.em.get_state()
    with gzip.open(name, 'wb') as f:
        f.write(content)

def load_state_from_file(env, name):
    with gzip.open(name, 'rb') as f:
        content = f.read()
    env.em.set_state(content)

    return env.step([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])


class joystickEventSender(threading.Thread):
    controllers = []
    running = 1
    JoystickData = []
    def __init__(self):
        #pygame.init()
        #pygame.joystick.init()
        #for x in range(pygame.joystick.get_count()):
        #    pygame.joystick.Joystick(x).init()
        #    if(pygame.joystick.Joystick(x).get_numbuttons() == 15):
        #        self.controllers.append(1)
        #    else:
        #        self.controllers.append(0)
        self.JoystickData = [0,0,0,0,0,0,0,0,0,0,0,0]
       	threading.Thread.__init__(self)

    def run(self):
        while True:
            lookup = {"BTN_SOUTH" : "B", 
                      "BTN_TL" : "L", 
                      "BTN_START" : "SELECT", 
                      "BTN_SELECT" : "START",  
                      "BTN_TR" : "R", 
                      "ABS_X" : "LR", 
                      "ABS_Y" : "UD", 
                      "BTN_NORTH": "X", 
                      "BTN_WEST" : "Y", 
                      "BTN_EAST" : "A"}
            index = {"B" : 0, "Y" : 1, "START" : 3, 
                     "SELECT" : 2, "DOWN" : 5, "UP" : 4, 
                     "RIGHT" : 7, "LEFT" : 6, "A" : 8, "X" : 9, 
                     "L" : 10, "R" : 11}
                    
            events = get_gamepad()
            for event in events:
                #print (event.code)
                if event.code in lookup:
                    #print (event.code, lookup[event.code])
                    if lookup[event.code] == "LR":
                        #print (event.state, int(event.state))
                        if int(event.state) == -32768:
                            self.JoystickData[index["LEFT"]] = 1
                            self.JoystickData[index["RIGHT"]] = 0
                        elif int(event.state) == 32512:
                            self.JoystickData[index["LEFT"]] = 0
                            self.JoystickData[index["RIGHT"]] = 1
                        else:
                            self.JoystickData[index["LEFT"]] = 0
                            self.JoystickData[index["RIGHT"]] = 0
                    elif lookup[event.code] == "UD":
                        #print (event.state, int(event.state))
                        if int(event.state) == 32512:
                            self.JoystickData[index["UP"]] = 1
                            self.JoystickData[index["DOWN"]] = 0
                        elif int(event.state) == -32768:
                            self.JoystickData[index["UP"]] = 0
                            self.JoystickData[index["DOWN"]] = 1
                        else:
                            self.JoystickData[index["UP"]] = 0
                            self.JoystickData[index["DOWN"]] = 0  
                    else:
                        if lookup[event.code] in index:
                            self.JoystickData[index[lookup[event.code]]] = event.state
                            
                #else:
                #    print(event.ev_type, lookup.get(event.code, event.code), event.state)
        
                
#def switch_env(x):

thread = joystickEventSender()
thread.start()


def action_to_list(buttons):
    binary_value = str(bin(buttons))
    binary_value = ''.join(list(binary_value)[2:])
    action = list(map(int,list(str(binary_value).zfill(12))))
    return action

#pygame.init()

states = {}
idx = 0
env = retro.make(game=main_game) #list_of_hacks[idx])
env.reset()
obs, rew, done, info = env.step([0,0,0,0,0,0,0,0,0,0,0,0])
print (info)
level = info['level']

class sound():
    def play(self, array, fs):
        sa.play_buffer(array, 2, 2, 44100)

mysound = sound()
i = 0
state_count = 0

SuperMarioWorld = "Super Mario World"
SuperMetroid = "Super Metroid"

main_state = "Main.state"
active_game = SuperMarioWorld

while True:
    obs, rew, done, info = env.step(thread.JoystickData)
    time.sleep(.01)
    # Sounds might be an option but really slows things down right now.
    # A possible solution is to figure out how to pass to "process" the values we want played
    # and some way to play them?
    #a = env.em.get_audio()
    #b = env.em.get_audio_rate()
    #p = Process(target = mysound.play, args=(a,b,))
    #p.start()
    #athread = threading.Thread(target = mysound.play, args=(a,b,))
    #athread.start()
    #print (thread.JoystickData)
#    print (active_game, info)
    if active_game == SuperMarioWorld:
#        print (thread.JoystickData)
        if thread.JoystickData == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]:
            print ("Saving")
            save_state_to_file(env, main_state)
        #print (info)
        # Basically if we change from the main level to a "new" level we are entering a "world" 
        # Thus we will change over to Super Metroid, the main failure here is that 
        # Super Metroid won't load if you enter the same level twice in a row
        # Then again hypothetically we wouldn't need to ever do that.
        if level != info['level']:
            print (info)
            if not os.path.exists(info['level']):
                save_state_to_file(env, str(info['level']) + ".state")
            state_count += 1
            #I don' think we need to handle prior to swap states. We need a "last item selected thing...", prior to swap will just start the SM level
            #save_state_to_file(env, "prior_to_swap.state")

            if info['level'] == 40:
                nextState = "morphBall.state"
            elif info['level'] == 41:
                nextState = "alphaMissileRoom.state"
            elif info['level'] == 42:
                nextState = "a.state"
            elif info["level"] == 37:
                nextState = "bt.state"
            else:

                continue

            #info_path = retro.data.get_file_path(game, info + '.json', inttype)
            level = info['level']
            tmp = env.em.get_state()
            # The rom is correctly loaded (at least the "name"), Next I need to make sure the metadata is correctly loaded.
            env.loadRom("SuperMetroid-Snes", nextState)
            # Load State seems to be broken.... I'll have to chase that down next
            # TODO fix load state, maybe I just have to load the data from file, then call load_state..not sure
            # I can also check hackrandomizer as that seems to work. 
            load_state_from_file(env, nextState)
            print (env.gamename)
            obs, rew, done, info = env.step([0,0,0,0,0,0,0,0,0,0,0,0])
            print ("METROID", info)
            room = info["room"]
            active_game = SuperMetroid

            #env.data.load(nextState)
    elif active_game == SuperMetroid:
        if thread.JoystickData == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]:
            print ("Saving")
            save_state_to_file(env, "a.state")
        if room != info['room']:
#            if not os.path.exists(info['level']):
#                save_state_to_file(env, str(info['level']) + ".state")
            state_count += 1
            env.loadRom("SuperMarioWorld-Snes")
            #nextState = "1.state"
            #info_path = retro.data.get_file_path(game, info + '.json', inttype)
            #load_state_from_file(env, nextState)
            #env.em.set_state(tmp)
            #obs, rew, done, info = load_state_from_file(env, nextState)
            obs, rew, done, info = env.step([0,0,0,0,0,0,0,0,0,0,0,0])
            level = info["level"]
            active_game = SuperMarioWorld

    if False: # Instead of changing when going HP, we are going to swap out save states when we change rooms in SMW
        
        print ("Changing Games", info["hp"], hp)
        save_state_to_file(env, "prior_to_swap.state")
        #if list_of_hacks[idx] not in states:
        print ("Saving the last hack's state")
        states[list_of_hacks[idx]] = env.em.get_state()

        idx = (idx + 1) % len(list_of_hacks)
        loadRom(list_of_hacks[idx])

        if list_of_hacks[idx] not in states:
            # If the state of our "new" hack isn't already listed in our state list we then will grab the state
            print ("grabbing our current state since we don't have a prior state.")
            states[list_of_hacks[idx]] = env.em.get_state()

        # Now assign the state to set_state
        env.em.set_state(states[list_of_hacks[idx]])
        obs, rew, done, info = env.step([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        hp = info['hp']
    #obs, rew, done, info = env.step([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    env.render()
    #print (i, info)
    i += 1
