# -*- coding: utf-8 -*-

'''run.py
build the main program here
'''

import os
import sys

from psychopy import core, event, logging, visual
from random import shuffle
from src.experiment import subject_info, event_logger, Paradigm, Text, Question, instructions
from src.fileIO import load_conditions_dict, write_csv, read_only

INFO = {
    'Experiment': 'resting_state',  # compulsory
    'Subject': 'R0001_001',  # compulsory
    }
settings = {
    'window_size': 'full_screen',
    #'window_size': [800, 600],
    'mouse_visible': False,
    'logging_level': logging.INFO
}

# MRI related settings
dummy_vol = 3
tr = 3
slice_per_vol = 60
RS_length = 9

# RSQ path
PATH = '/groups/Projects/P1336/resting_state/resting_Q.csv'
questions, headers = load_conditions_dict(PATH)
headers += ['StartTime', 'Rating', 'RT', 'IDNO']
shuffle(questions)

RSQ_txt = '/groups/Projects/P1336/resting_state/instructions/RSQ_instr.txt'
end_txt = '/groups/Projects/P1336/resting_state/instructions/end_instr.txt'
# collect participant info
experiment_info = subject_info(INFO)
# now run this thing
if __name__ == "__main__":
    # set working directory as the location of this file
    _thisDir = os.path.dirname(os.path.abspath(__file__)
                               ).decode(sys.getfilesystemencoding())
    os.chdir(_thisDir)

    # set log file
    event_logger(settings['logging_level'], experiment_info['LogFile'])

    # create experiment
    Experiment = Paradigm(escape_key='esc', color=0,
                          window_size=settings['window_size'])
    fixation = Text(window=Experiment.window, text='+', color='black')
    trigger = visual.TextStim(
                Experiment.window, text='Ready...',
                name='trigger',
                pos=[-50,0], height=34, wrapWidth=1100,
                color='black',
                )
    question = Question(window=Experiment.window, questions=questions, color='black')
    RSQ = instructions(window=Experiment.window, instruction_txt=RSQ_txt)
    endexp = instructions(window=Experiment.window, instruction_txt=end_txt)
    # hide mouse
    event.Mouse(visible=settings['mouse_visible'])

    # wait trigger
    trigger.draw()
    Experiment.window.flip()
    event.waitKeys(keyList=['5'])

    # dummy volumes
    timer = core.Clock()
    fixation.show(timer, tr * dummy_vol)

    # start the clock
    timer = core.Clock()
    # show fixation cross
    fixation.show(timer, RS_length * 60)
    if event.getKeys(keyList=['escape']):
        print('user quit')
        core.quit()

    # instruction end
    RSQ.show()
    for q in questions:
        question.set(q)
        start_trial, score, rt = question.show(timer)
        q['StartTime'] = start_trial
        q['Rating'] = score
        q['RT'] = rt
        q['IDNO'] = experiment_info['Subject']
        write_csv(experiment_info['DataFile'], headers, q)

    # save files
    logging.flush()
    # change output files to read only
    read_only(experiment_info['DataFile'])
    read_only(experiment_info['LogFile'])

    # quit
    endexp.show(5)
    Experiment.window.close()
    core.quit()
