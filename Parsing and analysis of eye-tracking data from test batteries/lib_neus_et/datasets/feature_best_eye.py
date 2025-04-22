"""
Defines FeatureDataset class
"""

import json
import numpy as np
from pandas import DataFrame
import warnings

from .feature_base import FeatureDatasetBase

# Maybe inherit from dictionary?

class FeatureDatasetBestEye(FeatureDatasetBase):

    """
    Class to store features for the best eye, one value per feature. Meant for multiple repetitions of the same task.
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
        """

        return np.nan




    def check_shape(self, dictionary):


        for k in dictionary:

            if not isinstance(dictionary[k], (float, int, str, np.int32)):

                return False
        

        return True
        


    def set_val(self, val, rep, name):

        """
        Update a single field.
        """

        if len(self._data) == 0:
            raise RuntimeError('Cannot set value for empty dataset.')

        if name not in self._data[0].keys():
            raise ValueError(f'Name {name} must be in {self._data[0].keys()}')


        try:

            self._data[rep][name] = val

        except:

            raise ValueError(f'Repetition {rep} does not exist try an integer 0<rep<{len(self._data)}.')

    def get_val(self, rep, name):

        try:

            return self._data[rep][name]

        except Exception as error:

            raise ValueError(f'Trying to get value gave the following error: {error}')

    

    def matrix(self, rep = 0):

        """
        Matrix form of a single repetition.
        """

        d = self._data[rep]

        return [[d[k]] for k in d.keys()]

# -----------------------------------------------------------------------------

    


    def _aux_unroll(self, d, name, rep):

        """
        Aux function. Update dictionary with unrolled version of the features.
        """

        if name not in d:

            d.update({name : []})

        
        d[name].append(rep[name])


    def _aux_fill(self, res, name, small_name, fun, single):

        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)

            if single:
                res[name] = fun(res[name])
            else:
                res[name] = fun[small_name](res[name])


    def _aux_groupfill(self, res, name, fun):

        
        res[name] = fun(res)[name]

