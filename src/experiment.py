# -*- coding: utf-8 -*-

'''experiment.py
experiemnt stimulus here
'''
from psychopy import core, data, gui, visual, event, logging
from pyglet.window import key

import os
from src.fileIO import create_dir, load_instruction
from random import uniform, shuffle

import numpy as np

sans = ['Arial','Gill Sans MT', 'Helvetica','Verdana'] #use the first font found on this list

class Paradigm(object):
    '''
    Study paradigm
    '''
    def __init__(self, escape_key='esc', window_size=(1280, 720), color=0, *args, **kwargs):
        self.escape_key = escape_key
        self.trials = []
        self.stims = {}

        if window_size =='full_screen':
            self.window = visual.Window(fullscr=True, color=color, units='pix', *args, **kwargs)
        else:
            self.window = visual.Window(size=window_size, color=color, allowGUI=True, units='pix', *args, **kwargs)

class Text(object):
    '''
    show text in the middle of the screen
    such as 'switch'
    '''
    def __init__(self, window, text, color):
        '''Initialize a text stimulus.
        Args:
        window - The window object
        text - text to display
        duration - the duration the text will appear
        keys - list of keys to press to continue to next stimulus. If None,
                will automatically go to the next stimulus.
        Additional args and kwargs are passed to the visual.TextStim
        constructor.
        '''
        self.window = window
        self.text = visual.TextStim(self.window, text=text, height=34, wrapWidth=1100, color=color, font=sans)

    def show(self, clock, duration):
        self.text.draw()
        self.window.flip()
        start_trial = clock.getTime()
        core.wait(duration)
        if event.getKeys(keyList=['escape']):
            print('user quit')
            core.quit()
        return start_trial

class Question(object):
    '''
    collect mind wandering report
    '''
    def __init__(self, window, questions, color):
        '''Initialize a question stimulus.
        Args:
        window - The window object
        questions - a list of dictionaries
        keys - list of keys to press to continue to next stimulus. If None,
                will automatically go to the next stimulus.
        Additional args and kwargs are passed to the visual.TextStim
        constructor.
        '''
        self.window = window
        self.description = visual.TextStim(self.window, text=None, height=34, wrapWidth=1100, color=color, font=sans)
        self.questions = questions
        self.rating = visual.RatingScale(self.window, low=1, high=10, markerStart=5,
                precision=10, tickMarks=[1, 10],
                leftKeys='1', rightKeys='2', acceptKeys='4')

    def set(self, trial):
        self.description.setText(trial['Item'])
        self.rating.setDescription(trial['Scale'])

    def show(self, clock):
        keyState=key.KeyStateHandler()
        self.window.winHandle.push_handlers(keyState)
        self.description.draw()
        self.rating.draw()
        self.window.flip()
        start_trial = clock.getTime()

        pos = self.rating.markerStart
        inc = 0.1

        while self.rating.noResponse:
            if event.getKeys(keyList=['escape']):
                print('user quit')
                core.quit()

            if keyState[key._1] is True:
                pos -= inc
            elif keyState[key._2] is True:
                pos += inc

            if pos > 9:
                pos = 9
            elif pos < 0:
                pos = 0

            self.rating.setMarkerPos(pos)
            self.description.draw()
            self.rating.draw()
            self.window.flip()

        score = self.rating.getRating()
        rt = self.rating.getRT()
        self.rating.reset()
        return start_trial, score, rt

class instructions(object):
    '''
    show instruction
    '''
    def __init__(self, window, instruction_txt):
        self.window = window
        self.instruction_txt = load_instruction(instruction_txt)

        self.display = visual.TextStim(
                window, text='default text', font=sans,
                name='instruction',
                pos=[-50,0], height=30, wrapWidth=1100,
                color='black',
                ) #object to display instructions

    def show(self, duration=None):
        # get instruction
        for i, cur in enumerate(self.instruction_txt):
            self.display.setText(cur)
            self.display.draw()
            self.window.flip()
            if duration:
                core.wait(duration)
            else:
                event.waitKeys(keyList=['4'])
            
            if event.getKeys(keyList=['escape']):
                print('user quit')
                core.quit()

def get_keyboard(timer, respkeylist, keyans):
    '''
    Get key board response
    Args:
    
        timer : obj
            the timer for the experiment
        
        respkeylist : list str 
            a list of key names you whish to capture
        
        keyans : list str
            what each key in respkeylist means. 
            The length of this list should be the same to respkeylist.
            
        
    Return:
        KeyResp : str
            the name of the key being pressed
        
        Resp : str
            what KeyResp actually means
        
        KeyPressTime : float
            The clock time when the key press occurred
    '''
    
    def quitEXP(endExpNow):
        if endExpNow:
            print 'user cancel'
            core.quit()
    
    Resp = None
    KeyResp = None
    KeyPressTime = np.nan
    keylist = ['escape'] + respkeylist

    for key, time in event.getKeys(keyList=keylist, timeStamped=timer):
        if key in ['escape']:
            quitEXP(True)
        else:
            KeyResp, KeyPressTime = key, time
    # get what the key press means
    if KeyResp:
        Resp = keyans[respkeylist.index(KeyResp)]
    return KeyResp, Resp, KeyPressTime


def subject_info(experiment_info):
    '''
    get subject information
    return a dictionary
    '''
    dlg_title = '{} subject details:'.format(experiment_info['Experiment'])
    infoDlg = gui.DlgFromDict(experiment_info, title=dlg_title)

    experiment_info['Date'] = data.getDateStr()

    file_root = ('_').join([experiment_info['Subject'],
                            experiment_info['Experiment'], experiment_info['Date']])

    experiment_info['DataFile'] = 'data' + os.path.sep + file_root + '.csv'
    experiment_info['LogFile'] = 'data' + os.path.sep + file_root + '.log'

    if infoDlg.OK:
        return experiment_info
    else:
        core.quit()
        print 'User cancelled'

def event_logger(logging_level, LogFile):
    '''
    log events
    '''
    directory = os.path.dirname(LogFile)
    create_dir(directory)

    logging.console.setLevel(logging.WARNING)
    logging.LogFile(LogFile, level=logging_level)
