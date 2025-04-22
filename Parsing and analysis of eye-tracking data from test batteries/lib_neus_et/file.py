"""
Defines functions used to manipulate files.
"""

import os
import json



def getUsers(path='', include = [], exclude = []) -> list[str]:

    """
    Get the test files with a certain substing in the name.

    :param path: The path to the directory to be explored for finding the files.
    :type path: str
    :param include: If one of the elements of this list is in the file name the file is included. If empty all files are included.
    :type include: list[str] or str
    :param exclude: If any of the elements of this list are in the file directory then the file is discarded. Used to exclude patients.
    :type exclude: list[str] or str
    :return: List of files.   
    """

    # Directories with string in exclude are excluded and files with string in includes are included
    if not isinstance(include, list):
        include = [include] # List of strings
    if not isinstance(exclude, list):
        exclude = [exclude] # List of strings

    # get a list of all test subjects (their important files)
    paths = []
    for root, _, files in os.walk(path):
        if not any([x in root for x in exclude]):
            if len(include) == 0: # include all files, if include is empty (counterintuitively)
                paths += [os.path.join(root, f).replace('\\', '/') for f in files]
            else:   # check each file for inclusion
                for f in files:
                    if any([x in f for x in include]):
                        paths.append(os.path.join(root, f).replace('\\', '/'))

    return paths






def log_to_json(directory, file_name, test_num=0, time=0, save=True, save_dir=None, verbose=False) -> dict:


    """
    Convert .log test files to .json test files.

    :param directory: Directory containing the .log file.
    :type directory: str
    :param file_name: The .log file name.
    :type file_name: str
    :param test_num: Number to add as test number in new file.
    :type test_num: int
    :param time: Number to add as test time in new file.
    :type test_num: int
    :param save: If True it will save the return dictionary as a .json file.
    :type save: bool
    :param save_dir: Where to save the .json file. If None the file will be saved in the same directory as the .log file.
    :type save_dir: str

    :return: Dictionary form of .json test file.
    """

    # Open the file
    with open(directory + file_name, encoding='utf-8') as f:
        f = f.readlines()

    # Get the info
    info = {'eyetracker' : None,
            'eyetracker-time' : None,
            'screen' : {'resolution' : {'height' : 0, 'width' : 0}, 'size' : {'height' : 0, 'width' : 0}},
           'version' : None}

    info['version'] = f[0][:-1].split()[-1]
    info['eyetracker'] = f[1][:-1].split()[-1]
    info['screen']['size']['width'] = f[2][:-1].split()[-2]
    info['screen']['size']['height'] = f[2][:-1].split()[-1]
    info['screen']['resolution']['width'] = f[3][:-1].split()[-2]
    info['screen']['resolution']['height'] = f[3][:-1].split()[-1]
    info['eyetracker-time'] = f[4][:-1].split()[-1]

    # Fill the data
    dictionary = {'info' : None, 'data' : [], 'time' : time, 'trial' : None, 'test' : test_num}
    dictionary['info'] = info

    if verbose:
        print('Converting data to .json format')


    for line in f[5:]:
        aux = json.loads(line.split(sep='\t')[1].split(sep='\n')[0])
        if 'gaze' in aux.keys():
            d = aux['gaze']
            d.update({'type' : 'gaze'})
        elif 'test' in aux.keys():
            if 'step' in aux['test'].keys():
                # Here is the name of the tasks
                t = aux['time']
                d = aux['test']
                d.update({'time' : t})
            else:
                if aux['test']['type'] == 'data':
                    t = aux['time']
                    d = aux['test']['data']
                    if 'action' in d:
                        d.update({'time' : t, 'type' : 'action'})
                        if d['action'] == 'show':
                            pass
                    else:
                        d.update({'time' : t, 'type' : 'data'})
                else:
                    t = aux['time']
                    d = aux['test']
                    d.update({'time' : t})
        else:
            raise Exception()

        dictionary['data'].append(d)

    # Free list
    del(f)

    #Obtain trial name from file name

    dictionary['trial'] = '-'.join(file_name.split('-')[2:]).split('.')[0]

    if verbose:
        print('Test name: {}'.format(dictionary['trial']))

    if save:
        if verbose:
            print('Saving file in directory: {}'.format(directory))
        if save_dir == None:
            save_dir = directory
        with open(os.path.join(save_dir, file_name.split('.')[0] + '.json'), 'w', encoding='utf-8') as f:
            json.dump(dictionary, f)

    return dictionary