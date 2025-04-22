"""
Define class for one eye-tracking test.
"""

from .tasks import TaskFactory
from .datasets import FeatureDataset, FeatureDatasetBestEye, ET_Data
from .screen import Screen
from .preprocess import preprocessData

import pandas as pd
import warnings 




class ET_Test():


    def __init__(self, filename, test_params):


        self.features = {}
        self.features_be = {}
        self.task_list = {}
        self.screen = None

        self.filename = filename

        self.params = test_params



    def keys(self):

        return self.task_list.keys()
    

    def get_patient_id(self, pandas=False):

        """
        Returns the patient ID (or name) and test date from the file name.
        """

        patno_id = self.filename.split('/')[-2]
        date = self.filename.split('/')[-3]
        if pandas:
            return {'ID' : patno_id, 'ET date' : pd.to_datetime(date, format="%y-%m-%d")}
        return {'ID' : patno_id, 'ET date' : date}
    
    def get_test_name(self):

        """
        Returns name of the test in a readable format.
        """

        if 'test-neus-v2' in self.filename:
            return 'Neus v2'
        elif 'test-neus-1' in self.filename:
            return '1 min'
        elif 'test-neus-2' in self.filename:
            return '2 min'
        elif 'test-xyzzy' in self.filename:
            return 'Neus new'
        elif '4month' in self.filename:
            return 'Cadiz (4 month)'
        elif 'standard' in self.filename:
            return 'Standard test (<2y) - P4'
        elif 'cartoon' in self.filename:
            return 'Cartoon test'
        else:
            return 'Unknown'
        
    def get_test_number(self):

        """
        Returns test number conting in the same folder.
        """

        f = self.filename.split('/')[-1]

        f = f.split('.')[0]

        return f.split('-')[-1]


    def parse(self, process_mode='meta', verbose=False):


        """
        Read the file and creates a dictionary of tasks. All initializations are done here.

        :param process_mode: The mode to preprocess files. See :py:func:preprocessData for more information.
        :type process_mode: "meta" or "audio"
        """

        dt, task_splits, screen_info = preprocessData(self.filename, process_mode, verbose=verbose) 

        self.screen = self._screen_from_info(screen_info)

        # Get the sampling rate of the device from file
        if screen_info['et_id'] in self.params['Eyetracking device']:
            sampling_rate = self.params['Eyetracking device'][screen_info['et_id']]['Sampling Rate']
        else:
            raise ValueError('The eye-tracking ID {} is not present in the parameter files.'.format(screen_info['et_id']))

        for task in task_splits:

            self.task_list[task] = []

            for times in task_splits[task]:

                data = dt[times[0]:times[1]]
                et = ET_Data(data, sampling = sampling_rate, screen=self.screen)
                #TODO: add the parameters of each task, taken from a dictionary saved somewhere. Not necessary at this stage.
                self.task_list[task].append(TaskFactory(task)(et, {}))




    
    def compute(self, task_list=None, rep=None, verbose=True):

        """
        Computes the features.

        Parameters:

        :parameter task_list: If not None it will compute features only for these tasks.
        :type task_list: None or list[str]
        :parameter rep: If not None it will compute features only for these indeces of the selected tasks.
        :type rep: None, int, slice, list[int]
        """
        

        return self._compute_base(dataset=FeatureDataset, 
                                  fun='compute', 
                                  attr='features',
                                  params=self.params['Compute parameters'],
                                  task_list=task_list, 
                                  rep=rep, 
                                  verbose=verbose)
    

    def compute_best_eye(self, params=None, task_list=None, rep=None, verbose=True):

        """
        Computes the features (best eye version). Uses features already computed in best eye.

        Parameters:

        :parameter params: Parameters used by the compute_best_eye method. A dictionary with keys the names of the tasks.
        :type params: dict
        :parameter task_list: If not None it will compute features only for these tasks.
        :type task_list: None or list[str]
        :parameter rep: If not None it will compute features only for these indeces of the selected tasks.
        :type rep: None, int, slice, list[int]
        """

        if params is None:

            params={k : {} for k in self.task_list}

    
    
        if task_list is None:

            iter = self.features.keys()

        else:

            iter = [t for t in task_list if t in self.features]


        for k in iter:

            if k not in self.task_list or len(self.task_list[k])==0:

                print(f'Task {k} not present in the test. Skipping.')
                continue


            obj = self.task_list[k][0]  

            if verbose:
                print(f'Computing features for task {k}.')

            if k in self.features_be.keys():

                # Compute again
                self.features_be[k] = FeatureDatasetBestEye()

            else:

                # Add it

                self.features_be.update({k : FeatureDatasetBestEye()})

            # Check the rep possibilities and define an iter_task interator.

            if rep is None:

                iter_task = self.features[k]

            elif isinstance(rep, slice) or isinstance(rep, int):

                iter_task = self.features[k][rep]

            elif isinstance(rep, list):

                d = len(self.features[k])

                iter_task = [self.features[k][i] for i in rep if i < d]
            
            else:

                raise ValueError(f'Parameter rep must be either an index, a list of indeces, a slice or None. Got {type(rep)} instead.')

            for t in iter_task:

                # Compute features and add them to the feature dataset

                self.features_be[k].join(obj.compute_best_eye(features = t, verbose = verbose, **params[k]), inplace=True)

            
        return self.features_be


    def reduce(self, fun, task, single=True, best_eye=False):

        """
        Reduce a task features with a certain function. The function must be compatible with missing values. Uses the reduce method of the task class.


        :param fun: This is the function used to reduce multiple values of the feature across different repetitions (e.g. the mean() to have an average of the values). 
        Must be compatible with missing values.
        :type fun: a dictionary of callable functions, or a callable function.
        :param task: Name of the task to reduce.
        :type task: str
        :param single: If True fun must be a dictionary that maps feature names to single reduction functions (each feature is reduced according to a different criterion).
          Otherwise all features are reduced together (might be necessary in some cases).
        :type single: bool
        :param best_eye: If True reduce the features of the best eye.
        :type best_eye: bool
        """

        if best_eye:

            feat = self.features_be

        else:

            feat = self.features

        if task not in feat or task not in self.task_list:

            raise ValueError(f'The name {task} is not present. Try {list(feat.keys())}')
        
        if len(self.task_list[task]) == 0:
            print(f'No repetition present for task {task}, cannot reduce.')
            return

        # Add number of usable repetitions
        
        feat[task] = self.task_list[task][0].reduce(feat[task], fun=fun, single=single)
    

    def to_pandas(self, task_list=None, best_eye = False):

        """
        Returns a pandas dataframe containing the features. Features must have been already computed.

        :parameter task_list: If not None it will compute features only for these tasks.
        :type task_list: None or list[str]
        :param best_eye: If True it will generate a dataframe only for values of the best eye.
        :type best_eye: bool
        """

        if best_eye:

            feats = self.features_be

        else:

            feats = self.features
        
        df = pd.DataFrame()

        if isinstance(task_list, str):
            task_list = [task_list]

        if task_list is None:
            to_iterate = feats.keys()
        else:
            to_iterate = task_list

        for k in to_iterate:

            if k not in feats:
                warnings.warn(f'Task {k} not present in features. Skipping.')
                continue


            if len(feats[k]) > 1:
                warnings.warn(f'More than one repetition for task {k}. This may cause some unexpected behavior when concatenating.')

            curr = feats[k].to_pandas()

            df = pd.concat((df, curr), axis=1)

        df.insert(0, 'num_rep', df.index)

        return df
    
    def threshold_nan(self, task, eye='M', threshold=1.0):

        """
        Removes the repetitions with too many missing values (more than threshold) from a certain task. Eye can be "L", "R", "M".

        :param task: Name of the task to reduce.
        :type task: str
        :param eye: The eye according to which to calculate the missing values. Remember that "M" allows for the less conservative measure (more tasks kept).
        :type eye: "L", "R" or "M"
        :param threshold: A repetition is kept if the ratio of missing values is less or equal than this value. Meaningful between 0.0 (keep only tasks withot missing values) and 1.0 (keep all tasks).
        :type threshold: float
        """

        if task not in self.features:

            warnings.warn(f'Task {task} is not present in the test.')
            return 

        if eye != 'all':

            self.features[task] = self.features[task].threshold_nan(eye=eye, threshold=threshold)
        
        else:

            tmp = self.features[task]

            for e in ['L', 'R', 'M', 'join']:

                tmp = tmp.threshold_nan(eye=e, threshold=threshold)

            self.features[task] = tmp


    



# ---------------------------------------------------------------------------------------------------



    def _screen_from_info(self, data):

        """
        Creates a screen instance given the content of the file and the parameters of the test.
        """

    
        d = {'diagonal' : self.params['Setup Info']['diagonal'], 'distance' : self.params['Setup Info']['distance']}

        d.update({'resolution' : {'width': data['screen_res']['W'], 'height': data['screen_res']['H']}})
        d.update({'size' : {'width': data['screen_size']['W'], 'height': data['screen_size']['H']}})

        return Screen(d)


    
    def _compute_base(self, dataset, fun, attr, params, task_list=None, rep=None, verbose=True):

        """
        Computes the features.

        Parameters:

        :parameter task_list: If not None it will compute features only for these tasks.
        :type task_list: None or list[str]
        :parameter rep: If not None it will compute features only for these indeces of the selected tasks.
        :type rep: None, int, slice, list[int]
        """
        

        if task_list is None:

            iter = self.task_list.keys()

        else:

            iter = [t for t in task_list if t in self.task_list]

        
        feats = getattr(self, attr)


        for k in iter:

            if verbose:
                print(f'Computing features for task {k}.')

            if k in feats.keys():

                # Compute again
                feats[k] = dataset()

            else:

                # Add it

                feats.update({k : dataset()})

            # Check the rep possibilities and define an iter_task interator.

            if rep is None:

                iter_task = self.task_list[k]

            elif isinstance(rep, slice) or isinstance(rep, int):

                iter_task = self.task_list[k][rep]

            elif isinstance(rep, list):

                d = len(self.task_list[k])

                iter_task = [self.task_list[k][i] for i in rep if i < d]
            
            else:

                raise ValueError(f'Parameter rep must be either an index, a list of indeces, a slice or None. Got {type(rep)} instead.')

            for t in iter_task:

                # Compute features and add them to the feature dataset

                feats[k].join(getattr(t, fun)(verbose = verbose, **params[k]), inplace=True)

            
        return feats