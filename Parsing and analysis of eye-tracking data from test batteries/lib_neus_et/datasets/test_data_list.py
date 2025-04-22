import json
import numpy as np
from pandas import DataFrame

from .feature_data import FeatureDataset
import warnings

# Maybe use prefix as an additional key for the list of FeatureDatasets?

class TestDataList():

    def __init__(self, task_list=[]):

        # Create a the base dictionary with the names of the tasks

        if isinstance(task_list, list):

            # Only the names

            self._check_names(task_list)
            
            self._data = {k : [] for k in task_list}

        elif isinstance(task_list, dict):

            # Dictionary of FeatureDatasets

            self._check_names(task_list.keys())

            for k in task_list.items():
                if not isinstance(k, FeatureDataset):
                    raise ValueError('When initializing a TestDataList you need to pass a dictionary of FeatureDatasets.')
        
        else:
            raise ValueError(f'Initialization not supported with {type(task_list)}')
        

    
    def get_data(self, task_name, idx):

        """
        Returns a specific FeatureDataset instance.
        """

        return self._data[task_name][idx]
    

    def add(self, feats, task):

        """
        Adds an additional FeatureDataset to a certain task.
        """

        for el in self._data[task]:

            try:
                el.join(feats, inplace=True)
                return
            except:
                continue

        
        # Could not add it to existing Feature Datasets

        self._data[task].append(feats)
    



    def reduce(self, fun, task):

        """
        Applies a reduction function on the certain tasks.
        """

        res = []

        for el in self._data[task]:

            res.append(el.single_reduce(fun))

        self._data[task] = res



    def _check_names(self, t_list):

        for el in t_list:

            if not isinstance(el, str):

                raise ValueError('Task names should be strings.')