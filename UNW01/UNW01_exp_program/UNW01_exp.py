import numpy
from psychopy import visual, core, event, clock, gui
from psychopy.event import Mouse
import numpy as np
import sys
import glob
import csv
import os
import datetime
import random
import tobii_research as tr

random.seed() # use clock for random seed

def escape():
    # Exits the task when escape is pressed
    while True:
        for key in event.getKeys():
           if key in['escape']:
                core.quit()
        break

# Experiment parameters
exp_code = "UNW01" # Unique experiment code
runET = 0
timeout_time = 10

# get current date and time as string
x = datetime.datetime.now()
start_time = x.strftime("%y_%m_%d_%H%M")

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

# GUI for experiment setup and subject details
setupGUI = gui.Dlg(title= exp_code + " Experiment")
setupGUI.addText('Experiment Setup')
setupGUI.addField('Condition:', choices=['1', '2'])
setupGUI.addField('Participant Number:') # remove random for experiment
setupGUI.addText(' ')  # blank line
setupGUI.addText('Participant details')
setupGUI.addField('Age:')
setupGUI.addField('Gender:', "NA", choices=["Male", "Female", "Non-binary", "NA", "Other"])
language = setupGUI.addField('English first language?', choices=["Yes", "No"])
setup_data = setupGUI.show()  # show dialog and wait for OK or Cancel
if setupGUI.OK:  # or if ok_data is not None
    unc_condition = int(setup_data[0])
    subNum = int(setup_data[1])
    subAge = int(setup_data[2])
    subGender = setup_data[3]
    dataFile = "DATA\ " + exp_code + "_" + start_time + "_s" + f"{subNum:03}" + ".csv" # create csv data file
    test_dataFile = "DATA\ " + exp_code + "_" + start_time + "_s" + f"{subNum:03}" + "_test.csv" # create csv data file
    eye_dataFile = "DATA\ " + exp_code + "_" + start_time + "_s" + f"{subNum:03}" + "_eye.csv"  # create csv data file
else:
    print('Setup cancelled')
    core.quit()

# main experiment data file
dataHeader = ['exp_code', 'pNum', 'phase', 'cue1', 'out',
              'cert_cond', 'prob_outcome', 'out_order', 'out_response', 'accuracy', 'RT',
              'age', 'gender', 'cue_img_rand', 'out_img_rand']
with open(dataFile, 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(dataHeader)

TS = 0 # variable for PP timestamps
t_phase = 0 # variable for trial phase information

if runET == 1:
    # connect to eye=tracker
    writeHeader = True

    found_eyetrackers = tr.find_all_eyetrackers()

    my_eyetracker = found_eyetrackers[0]
    print("Address: " + my_eyetracker.address)
    print("Model: " + my_eyetracker.model)
    print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
    print("Serial number: " + my_eyetracker.serial_number)
    print("NEW")

    def gaze_data_callback(gaze_data):
        # Print gaze points of left and right eye
#        print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
#            gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
#            gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
        with open(eye_dataFile, 'a', newline = '') as f:  # You will need 'wb' mode in Python 2.x

            global writeHeader, trial, t_phase, TS

            gaze_data["trial"] = trial
            gaze_data["trial_phase"] = t_phase
            gaze_data["pp_TS"] = TS

            w = csv.DictWriter(f, gaze_data.keys())
            if writeHeader == True:
                w.writeheader()
                writeHeader = False
            w.writerow(gaze_data)

winWidth = 1920; winHeight = 1080
win = visual.Window(
    size=[winWidth, winHeight],
    units="pix",
    fullscr=False,
    color=[0.5, 0.5, 0.5])

my_mouse = event.Mouse()

textFeedback = visual.TextStim(win=win, units="pix", pos=[0, -100], color=[-1,-1,-1],
                               font="Arial", height = 40, bold=True)

# read in input files and generate trial sequence

# function for generating trial sequence
def genTrialSeq(design_filename, blocks):
    # read in input files
    stg_design = np.genfromtxt(design_filename, delimiter=',', skip_header = True, dtype = int)
    stg_trials = []

    for b in range(0,blocks):
        newPerm = np.random.permutation(len(stg_design)) # shuffles rows
        stg_trials.append(stg_design[newPerm])

    stg_trials = np.reshape(stg_trials, (-1, 4)) # -1 here signals the missing dimensions, which is auto computed

    return stg_trials

# need control of certain/uncertain here - odd/even Ps?
if unc_condition == 1:
    stg1 = genTrialSeq(os.path.join(script_dir, "input_files/UNW01_stg1_certain.csv"), 3)
elif unc_condition == 2:
    stg1 = genTrialSeq(os.path.join(script_dir, "input_files/UNW01_stg1_uncertain.csv"), 3)
else:
    print("Incorrect condition set")
    win.close()
    sys.exit()

stg1 = np.c_[np.ones(len(stg1), dtype=int), stg1]

stg2 = genTrialSeq(os.path.join(script_dir, "input_files/UNW01_stg2.csv"), 2)
stg2 = np.c_[np.ones(len(stg2), dtype=int)*2, stg2]

stg3 = genTrialSeq(os.path.join(script_dir, "input_files/UNW01_stg3.csv"), 2)
stg3 = np.c_[np.ones(len(stg3), dtype=int)*3, stg3]

trialSeq = np.concatenate((stg1, stg2, stg3))


# read in image files and create image array for cues
cue_files_list = glob.glob('img_files\cue*.png')
imgArrayCue = [visual.ImageStim(win, img, size = 300) for img in cue_files_list] # create array of images
imgArrayCue = np.array(imgArrayCue) # convert to no array
cueShuffle = np.random.permutation(4)
imgArrayCue = imgArrayCue[cueShuffle]

# read in image files and create image array for cues
out_files_list = glob.glob('img_files\out*.png')
imgArrayOut = [visual.ImageStim(win, img, size = [220, 60]) for img in out_files_list] # create array of images
imgArrayOut = np.array(imgArrayOut) # convert to no array
outShuffle = np.random.permutation(4)
imgArrayOut = imgArrayOut[outShuffle]

# read in instruction slides
instr_files_list = glob.glob('instruction_files\Slide*.PNG')
instrArray = [visual.ImageStim(win, img, size=(winWidth, winHeight)) for img in instr_files_list] # create array of images

# correct outcome box
corOutFrame = visual.Rect(win, width = 220, height = 60, lineColor = [-1,1,-1], fillColor = None)


# present the instructions
for instr in range(0, 2):
    instrArray[instr].draw()
    win.flip()
    event.waitKeys(keyList=["space"]) # wait for spacebar response

textFeedback.text = "Please wait for the experimenter"
textFeedback.draw()
win.flip()
event.waitKeys(keyList=["f1"]) # wait for spacebar response

# turn eye-tracker on
if runET == 1:
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

outcome_x_positions = [-375, -125, 125, 375]
out_key_list = np.array(["c", "v", "b", "n"])

for trial in trialSeq[0:1,]:

    # "trial" is the row from trialSeq, containing info on cues/outcomes etc
    cue1 = imgArrayCue[trial[1]-1]
    cue1.pos = [0, 200]
    cue1.draw()

    # randomise position of outcomes
    trial_out_order = np.random.permutation(4) # shuffles outcomes
    correct_out_position = np.where(trial_out_order == trial[2] - 1)  # -1 because outs are 1-4, positions are 0-3

    for o in range(0, 4):
        imgArrayOut[trial_out_order[o]].pos = [outcome_x_positions[o], -200]
        imgArrayOut[trial_out_order[o]].draw()

    # stimulus on
    TS = win.flip()
    img_On_time = clock.getTime()
    t_phase = 1  # start of the "stimulus on" phase

    print(trial)
    print(trial_out_order)
    print(correct_out_position)
    
    win.getMovieFrame()   # Defaults to front buffer, I.e. what's on screen now.
    win.saveMovieFrames('screenshot_main.png')  # save with a descriptive and unique filename. 
    
    clicked = False
    while clicked == False:
        for out in imgArrayOut:
            if (clock.getTime() - img_On_time) > timeout_time:
                clicked = True
                response_index = -99
                acc = -99
                RT = -99
                feedback = "Timeout!"
                textFeedback.color = [1, -1, -1]
            else:
                if my_mouse.isPressedIn(out) :
                    escape() # if escape key held, will escape
                    response_index = np.where(imgArrayOut == out) # which image is this by index
                    print(response_index)
                    RT = clock.getTime() - img_On_time
                    clicked = True
                    clicked_outcome = out
                    if response_index == (trial[2]-1): # is this the correct outcome image?
                        acc = 1
                        feedback = "Correct!"
                        textFeedback.color = [-1, 1, -1]
                    else:
                        acc = 0
                        feedback = "Error!"
                        textFeedback.color = [1, -1, -1]

    if acc != -99: # if not a timeout
        # redraw cue and outcomes to the screen as flip/buffer is FUBAR
        cue1 = imgArrayCue[trial[1]-1]
        cue1.pos = [0, 200]
        cue1.draw()

        for o in range(0, 4):
            imgArrayOut[trial_out_order[o]].pos = [outcome_x_positions[o], -200]
            imgArrayOut[trial_out_order[o]].draw()

        # indicate correct outcome
        correct_out_position = int(correct_out_position[0])
        corOutFrame.pos = [outcome_x_positions[correct_out_position], -200]
        corOutFrame.draw()

        response_index = int(response_index[0]) + 1

    # write feedback text to screen
    textFeedback.text = feedback
    textFeedback.draw()

    TS = win.flip()
    t_phase = 2  # feedback on phase
    core.wait(2)

    # ITI
    TS = win.flip()
    t_phase = 3  # feedback off, start of ITI phase
    core.wait(1)

    # write details to csv
    trial_data = np.append(trial, [np.array2string(trial_out_order), response_index, acc, RT,
                                   subAge, subGender, # demographics
                                   np.array2string(cueShuffle), np.array2string(outShuffle)]) # image assignment
    trial_data = trial_data.astype(str)
    trial_data = np.insert(trial_data, 0, [exp_code, str(subNum)])

    with open(dataFile, 'a', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(trial_data)

# test phase

# test phase data file
dataHeader = ['exp_code', 'pNum', 'age', 'gender', 'out_order', 'cue',
              'outcome', 'rating', 'rating_rt']
with open(test_dataFile, 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(dataHeader)


# build test order of cues and outcomes
cueRand = np.random.permutation(4) # random order of cues
outRand = np.random.permutation(4) # random order of outcomes

outcome_y_positions = [300, 100, -100, -300]

ratingScale = [visual.RatingScale(win, low = 1, high = 10, labels = ['very unlikely', 'very likely'],
                                  scale = None, pos = (500,outcome_y_positions[i]), size = .6,
                                  textSize = 1.2, textColor = "Black", lineColor = "Black", showAccept = False, showValue = True) for i in range(0,4)]

textTestInstr = visual.TextStim(win, text = "How likely is it that this clown will result in each of the audience reactions?",
                                pos = (-400, 200), color="Black", height = 25, alignText="left")


next_btn = visual.ImageStim(win, image = 'img_files\click_next.PNG', size=(100, 50), pos = (850,-450)) # create next button

for instr in range(2, 4):
    instrArray[instr].draw()
    win.flip()
    event.waitKeys(keyList=["space"]) # wait for spacebar response

textFeedback.text = "Please wait for the experimenter"
textFeedback.draw()
win.flip()
event.waitKeys(keyList=["f1"]) # wait for f1 response

for c in range(0,1):
    imgArrayCue[cueRand[c]].pos = (-400,0)

    test_data = np.array([exp_code, subNum, subAge, subGender, outRand+1, cueRand[c]+1])

    clicked = False
    while clicked == False:
        next_btn.draw()
        imgArrayCue[cueRand[c]].draw()
        textTestInstr.draw()
        for r in range(0,4):
            ratingScale[r].draw()
            imgArrayOut[outRand[r]].pos = (50, outcome_y_positions[r])
            imgArrayOut[outRand[r]].draw()
        win.flip()
        if my_mouse.isPressedIn(next_btn):
            escape()
            clicked = True
            for r in range(0,4):
                if ratingScale[r].getRating() is None:
                    print("none detected")
                    clicked = False

    for r in range(0,4):
        rating = ratingScale[r].getRating()
        decisionTime = ratingScale[r].getRT()
        choiceHistory = ratingScale[r].getHistory()

        test_data_rating = np.append(test_data, [outRand[r]+1, rating, decisionTime])

        with open(test_dataFile, 'a', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(test_data_rating)
    
    win.getMovieFrame()   # Defaults to front buffer, I.e. what's on screen now.
    win.saveMovieFrames('screenshot_test.png')  # save with a descriptive and unique filename. 
    
    # ITI
    TS = win.flip()
    t_phase = 4  # feedback off, start of ITI phase
    core.wait(1)

    # reset the rating scales
    for r in range(0, 4):
        ratingScale[r].reset()



# turn eye-tracker off
if runET == 1:
    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

for instr in range(4, 6):
    instrArray[instr].draw()
    win.flip()
    event.waitKeys(keyList=["space"]) # wait for spacebar response

textFeedback.text = "Please contact the experimenter"
textFeedback.draw()
win.flip()
event.waitKeys(keyList=["f1"]) # wait for f1 response

win.close()
sys.exit()