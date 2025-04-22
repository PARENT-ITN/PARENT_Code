"""
Defines FeatureDataset class
"""

import json
import numpy as np
from pandas import DataFrame
import warnings

from .feature_base import FeatureDatasetBase

# Maybe inherit from dictionary?

class FeatureDataset(FeatureDatasetBase):

    """
    Class to store features for left, right, median and join eyes. Meant for multiple repetitions of the same task.
    Has methods to reduce the values.

    :param rep: The features. Can be either empty, one repetition or multiple repetitions of the same task.
    :type data: None, list[str], list[dict], FeatureDataset.
    """

    def __init__(self, rep=None):

        super().__init__(rep)


    def _data_type(self, rep):

        return isinstance(rep, dict)

    def _init_feat(self):

        """
        Initializes empty fatures, with all the eyes.

        :param rep: The features. Can be either empty, one repetition or multiple repetitions of the same task.
        :type data: None, list[str], list[dict], FeatureDataset.
        """

        return {'L' : np.nan, 'R' : np.nan, 'M' : np.nan, 'join' : np.nan}




    def check_shape(self, dictionary):

        for k in dictionary:

            if not isinstance(dictionary[k], dict) or list(dictionary[k].keys()) != ['L', 'R', 'M', 'join']:
                return False

        return True
        


    def set_val(self, val, rep, name, eye):

        """
        Update a single field.
        """

        if len(self._data) == 0:
            raise RuntimeError('Cannot set value for empty dataset.')

        if eye not in ['L', 'R', 'M', 'join']:
            raise ValueError('Please select an existing eye, try "M", "L", "R" or "join".')

        if name not in self._data[0].keys():
            raise ValueError(f'Name {name} must be in {self._data[0].keys()}')


        try:

            self._data[rep][name][eye] = val

        except:

            raise ValueError(f'Repetition {rep} does not exist try an integer 0<rep<{len(self._data)}.')

    def get_val(self, rep, name, eye):

        try:

            return self._data[rep][name][eye]

        except Exception as error:

            raise ValueError(f'Trying to get value gave the following error: {error}')


    def unravel(self, eye = None):

        """
        Returns unraveled version of the dataset.
        """
        if isinstance(eye, str):
            eye = [eye]

        res = []

        for rep in self._data:

            cur = {}

            for name in rep:
                for e in rep[name]:
                    if eye is None or e in eye:
                        cur.update({name + '.' + e : rep[name][e]})

            res.append(cur)

        return res

    

    def matrix(self, rep = 0):

        """
        Matrix form of a single repetition.
        """

        d = self._data[rep]

        return [[d[k]['L'], d[k]['R'], d[k]['M'], d[k]['join']] for k in d.keys()]

# -----------------------------------------------------------------------------

    


    def _aux_unroll(self, d, name, rep):

        """
        Aux function. Update dictionary with unrolled version of the features.
        """

        if name not in d:

            d.update({name : {'L' : [], 'R' : [], 'M' : [], 'join' : []}})

        for eye in rep[name]:

            d[name][eye].append(rep[name][eye])


    def _aux_fill(self, res, name, small_name, fun, single):

        for eye in res[name]:

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
    
                if single:
                    res[name][eye] = fun(res[name][eye])
                else:
                    res[name][eye] = fun[small_name](res[name][eye])


    def _aux_groupfill(self, res, name, fun):

        for eye in res[name]:
                res[name][eye] = fun(res)[name][eye]

