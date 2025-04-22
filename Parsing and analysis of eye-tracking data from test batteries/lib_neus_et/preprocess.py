"""
Preprocess function. Defines which tasks are present in the file.
"""
import json

# Preprocess data ----------------------------------------------------

def preprocessData(filename, mode = 'meta', verbose = False):
    
    """
    Preprocess function. Defines which tasks are present in the file.

    :param filename: Name of the .json file.
    :type filename: str
    :param mode: Method used to identify the tasks. There are two possibilities: older tests use audio messages, test with children and recent tests use meta flags within the file.
    :type mode: "meta" or "audio"

    :return: The function returns:

            - Raw data from file as a list
            - Dictionary containing all tasks present in the test. Together with starting index and ending index.
            - Dictionary with other info saved in the file: test ID, screen info, eye-tracker info
    """

    # load data
    d = json.loads(open(filename, encoding = 'utf-8').read())

    info = {'test_id' : d['test'],
            'et_id' : d['info']['eyetracker'],
            'screen_res' : {'W' : d['info']['screen']['resolution']['width'], 'H' : d['info']['screen']['resolution']['height']},
            'screen_size' :  {'W' : d['info']['screen']['size']['width'], 'H' : d['info']['screen']['size']['height']}}

    if verbose:
        print('          Test ID:', info['test_id'])
        print('    Eyetracker ID:', info['et_id'])
        print('     Test version:', d['info']['version'])
        print('Screen resolution:',str(d['info']['screen']['resolution']['width'])+'x'+str(d['info']['screen']['resolution']['height']))
        print()


    if verbose: print('Sorting data.')
    ds = d['data'] #list
    ds.sort(key = lambda x: x['time'])

    # map events in the data to facilitate removal of back button effects (What are these?)
    # forward button should not be possible in non-research version
    if verbose: print('Checking for back button use.')
    cur_step = -1
    steps = {}
    for rx, rec in enumerate(ds):                    # rx is the counting number, rec is the rest
        if 'type' in rec and rec['type'] == 'step':
            if rec['step'] not in steps:             # store position for every 'step' event
                steps[rec['step']] = [rx]            # Key is the data point
                cur_step = rec['step']
            else:
                # Only if time step is lower than current step it is added to the STEPS dictionary

                if rec['step'] < cur_step:           # if current step reduces then back button was used
                    steps[rec['step']].append(rx)    # store position of step where recording resumed
                    cur_step = rec['step']           # and reset current step counter

    dt = []
    start = 0
    for k, v in steps.items():
        if len(v) > 1: # same step was encountered more than once due to back button use
            if verbose: print('  Step', k, '> removing datapoints between', v[0], 'and', str(v[-1] - 1)+'.')
            dt += ds[start:v[0]] # Add in the back of dt the current slice of ds, without extra time steps
            start = v[-1]
    dt += ds[start:]   # append the remainder of the list (after last back button press)
    del(ds)  # delete auxiliary data from memory

    if verbose: print('Parsing data into separate tasks.')

    if mode == 'meta':
        tasks, eot = split_meta(dt)
    elif mode == 'audio':
        tasks, eot = split_audio(dt)
    else:
        raise ValueError('ERROR: preprocessing mode not detected. Try "meta" for the new tests and "audio" for the older.')

    # final cleanup of the tasks dictionary
    if 'Start' in tasks:
        del tasks['Start']

    if 'Person data memorization' in tasks:
        tasks['Person data memorization'] = [tasks['Person data memorization'][-1]]


    # output detected tasks (if verbose)
    if verbose:
        for k,v in tasks.items():
            print('  %s task found %dx.' % (k, len(v)))

    # output whether end of test was detected
    if not eot:
        print('Warning, end of test was not detected! Test ID: %s.' % d['test'])
        if verbose: print()
    else:
        if verbose:
            print('End of test detected; data read in full.')
            print()

    return dt, tasks, info



def split_meta(dt):

    eot = False  # end of test detected flag
    cx, cur_task = 0, 'Start'
    tasks = {} # dictionary
    task_open = False


    for rx, rec in enumerate(dt):
        if 'meta' in rec:  # Only check 'task' data points
            # when a new task is found: close previous task and open a new one
            # this version assumes all tasks contain unique audio identifiers -- change for a better solution later on
            # Basically a switch between the audio identifiers
            # CUR_TASK contains the last switch case
            # Since it uses rx-1 it always add the previous task id
            if  rec['meta']['type'] == 'begin':
                cx = rx
                task_open = True

                if  'smile-pursuit' in rec['meta']['task']:
                    cur_task = 'Smile pursuit'

                elif 'dummy' in rec['meta']['task']:
                    cur_task = 'Dummy'

                elif 'attention' in rec['meta']['task']:
                    cur_task = 'Attention'

                elif  'memory' in rec['meta']['task']:
                    if 'color' in rec['meta']['task']:
                        cur_task = 'Memory-Color'
                    elif 'shape' in rec['meta']['task']:
                        cur_task = 'Memory-Shape'
                    else:
                        cur_task = 'Memory-Face'

                elif  'social-orienting-pair' in rec['meta']['task']:
                    cur_task = 'Image pair'

                elif 'social-orienting-face' in rec['meta']['task']:
                    cur_task = 'Face'
                else:
                    cur_task = rec['meta']['task']


            elif rec['meta']['type'] == 'end' and task_open:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                task_open = False
            else:
                # print('Potential unhandled task event >', rec)  # for debugging purposes
                pass

    # The test was properly finished
    if not task_open:
        eot = True

    return tasks, eot


def split_audio(dt):

    eot = False  # end of test detected flag
    cx, cur_task = 0, 'Start'
    tasks = {} # dictionary

    for rx, rec in enumerate(dt):
        if 'task' in rec.keys():  # Only check 'task' data points
            # when a new task is found: close previous task and open a new one
            # this version assumes all tasks contain unique audio identifiers -- change for a better solution later on
            # Basically a switch between the audio identifiers
            # CUR_TASK contains the last switch case
            # Since it uses rx-1 it always add the previous task id
            if 'audio' in rec['task'] and 'pst-x' in rec['task']['audio']:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'PST.x'
            elif 'audio' in rec['task'] and 'memorize' in rec['task']['audio']:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'Person data memorization'
            elif 'audio' in rec['task'] and 'recall' in rec['task']['audio']:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'Person data memorization'
            elif 'name' in rec['task'] and rec['task']['name'] == 'dots':
                # these will be separate for each counting task, careful with new version!
                # ANDREA: The syntax for this task is different
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'Dot count'

            # Old version using the audio, not compatible with new library
            #elif 'audio' in rec['task'] and 'pursuit' in rec['task']['audio']:
            #    if cur_task in tasks:
            #        tasks[cur_task].append((cx,rx-1))
            #    else:
            #        tasks[cur_task] = [(cx,rx-1)]
            #    cx = rx
            #    cur_task = 'Pursuit'


            elif 'offset' in rec['task'] and 'period' in rec['task']:
                # Split different instances of smooth pursuit
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'Pursuit'
            elif 'audio' in rec['task'] and 'ast-x' in rec['task']['audio']:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'AST.x'
            elif 'audio' in rec['task'] and 'story-1' in rec['task']['audio']:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'Story'
            elif 'audio' in rec['task'] and 'corsi' in rec['task']['audio']:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'Corsi'
            elif 'audio' in rec['task'] and 'pst-y' in rec['task']['audio']:
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                cx = rx
                cur_task = 'PST.y'
            elif 'audio' in rec['task'] and ('end.wav' in rec['task']['audio'] or 'end.oga' in rec['task']['audio']):
                # end of test detected
                if cur_task in tasks:
                    tasks[cur_task].append((cx,rx-1))
                else:
                    tasks[cur_task] = [(cx,rx-1)]
                eot = True
            else:
                # print('Potential unhandled task event >', rec)  # for debugging purposes
                pass

    return tasks, eot



# -----------------------------------------------------------------
# Preprocess parameters

def preprocessParameters(directory, verbose=True):

    """
    Read parameters from json files in the directory.
    """

    if verbose:
        print('Reading parameters')

    params = json.load(open(directory + 'general_params.json'))

    # Add eye-tracker

    params.update(json.load(open(directory + 'eyetrackers.json')))

    # Add tasks

    params.update(json.load(open(directory + 'tasks.json')))

    # Add parsing parameters

    params.update(json.load(open(directory + 'parsing.json')))

    return params
