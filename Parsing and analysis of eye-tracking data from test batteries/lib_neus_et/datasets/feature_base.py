"""
Defines FeatureDataset base abstract class
"""

import json
import numpy as np
from pandas import DataFrame
import warnings
from abc import ABC, abstractmethod

class FeatureDatasetBase(ABC):

    """
    Class to store features. Meant for multiple repetitions of the same task.
    Has methods to reduce the values.

    :param rep: The features. Can be either empty, one repetition or multiple repetitions of the same task.
    :type data: None, list[str], list[dict], FeatureDataset.
    """

    def __init__(self, rep=None):

        # Case 0: none

        if rep is None or len(rep) == 0:

            self._data = []
            self._prefix = ''

        # Case 1: only the names [list of strings]

        elif isinstance(rep, list) and isinstance(rep[0], str):

            if self.check_names(rep):

                self._data = [{k : self._init_feat() for k in rep}]
                self._prefix = self._set_prefix(rep[0])

            else:
                raise ValueError('All the features must begin with the same prefix.')

        # Case 2: repetition with values

        elif isinstance(rep, list) and isinstance(rep[0], dict):

            if self.check_names(list(rep[0].keys())):

                self._data = [rep[0]]
                self._prefix = self._set_prefix(list(rep[0].keys())[0])

            else:
                raise ValueError('All the features must begin with the same prefix.')

            for el in rep[1:]:
                self.add_rep(el)


        # Case 3: another FeatureDataset

        elif isinstance(rep, FeatureDatasetBase):

            self._data = rep._data
            self._prefix = rep._prefix

        else:
            raise ValueError(f'Initialization not supperted for type {type(rep)}.')


    def __len__(self):

        return len(self._data)
    
    def __repr__(self) -> str:

        return self._data.__repr__()
    
    def __str__(self) -> str:

        return self._data.__str__()
    
    def __getitem__(self, key):

        return self.get_rep(key=key)
    

    def _data_type(self, rep):

        return True


    @abstractmethod
    def _init_feat(self):

        return False


    def check_names(self, names):

        if len(names) == 1:
            return True

        prefix = names[0].split('.')[0]
        for el in names[1:]:
            if el.split('.')[0] != prefix:
                return False
        return True


    @abstractmethod
    def check_shape(self, dictionary):

        return True

    def check_prefix(self, names):

        for el in names:
            if el.split('.')[0] != self._prefix:
                return False
        return True


    def _set_prefix(self, string):

        return string.split('.')[0]

    def _get_nan_name(self, idx = 0):
        check = []
        for k in self._data[idx].keys():

            if k.split('.')[-1] == 'nan':
                check.append(k)

        if len(check) > 0:
            if len(check) > 1:
                # warnings.warn('More than one missing value feature found. Returning only the first one.')
                pass

            return check[0]
    

        warnings.warn('No missing values feature found. Returning None.')
        return None
    
    def _general_feat_name(self, st):

        return '.'.join([self._prefix, st.split('.')[-1]])


    def add_rep(self, rep):

        """
        Add repetition of the task to the dataset.

        :parameter rep: A valid repetition to add. Must respect the naming convention.
        :type rep: dict
        """

        # In case of empty one

        if self._prefix == '':
            self._prefix = self._set_prefix(list(rep.keys())[0])



        if self._data_type(rep) and self.check_shape(rep) and self.check_prefix(rep.keys()):
            self._data.append(rep)

        else:
            if not self._data_type(rep):
                raise ValueError(f'Unable to add repetition {rep}, due to wrong data type.')
            
            if not self.check_shape(rep):
                raise ValueError(f'Unable to add repetition {rep}, due to wrong shape.')
            
            if not self.check_prefix(rep.keys()):
                raise ValueError(f'Unable to add repetition {rep}, due to wrong task prefix.')
        

    def join(self, feat2, inplace=False):

        """
        Join two FeatureDatasets into one. If possible.
        """

        if not isinstance(feat2, FeatureDatasetBase):

            raise ValueError(f'Can only join to another FeatureDataset. Gotten {type(feat2)} instead.')
        
        if inplace:
            new = self
        else:
        
            new = type(self)(self._data)

        for el in feat2._data:

            try:

                new.add_rep(el)

            except:
                raise ValueError(f'Unable to add one repetition {el}.')
        
        return new



    def add_empty(self, names):
        """
        Add an empty repetition without values.

        :parameter names: Names of the features.
        :type names: list[str] 
        """
        self._data.append({k : self._init_feat() for k in names})


    @abstractmethod
    def set_val(self, val, rep, name, **kwargs):

        return None
    

    @abstractmethod
    def get_val(self, rep, name, **kwargs):

        return 0

    def get_nan(self):

        """
        Returns a FeatureDataset with only the NaN values.
        """

        name = self._get_nan_name()
        if name is not None:
            list_nans = []
            for el in self._data:
                if name in el:
                    list_nans.append({name : el[name]})
            return type(self)(list_nans)

        return None
    

    def unravel(self, **kwargs):

        """
        Returns unraveled version of the dataset.
        """
        

        return self._data


    def to_pandas(self, **kwargs):

        """
        Converts to pandas dataframe.
        """

        return DataFrame(self.unravel(**kwargs))
    
    @abstractmethod
    def matrix(self, rep = 0):

        """
        Matrix form of a single repetition.
        """

        return []

# -------------------- Reductions --------------------------------------------------

    def reduce(self, fun, single=True):

        """
        Uses a reduction function to aggregate all repetitions in a single one. The reduction function can be shared by
        all features or be different for each one WITH A DIFFERENT NAME. 

        TODO: maybe add the possibility to use different reduction functions for different "variants" of the same task?
        """

        if single and not callable(fun):
            raise ValueError('Parameter fun must be a callable object.')
        
        if not single and not isinstance(fun, dict):
            raise ValueError('Parameter fun must be a dictionary of functions, if single is True.')
        
        if self.__len__() == 0:

            # Reduce does nothing with an empty dataset
            return type(self)([])
        
        if self.__len__() == 1:

            #Nothing to reduce
            return type(self)(self._data)

        res = {}

        # Unroll

        for rep in self._data:

            for name in rep:

                self._aux_unroll(res, name, rep)

        # Fill

        for name in res:

            small_name = self._general_feat_name(name)

            self._aux_fill(res, name, small_name, fun, single)


        return type(self)([res])
    

    
    def group_reduce(self, fun):

        res = {}

        # Fill

        for rep in self._data:

            for name in rep:

               self._aux_unroll(res, name, rep)

        # Compute

        for name in res:

            self._aux_groupfill(res, name, fun)


        return type(self)([res])
    

    @abstractmethod
    def _aux_unroll(self, d, name, rep):

       pass

    
    @abstractmethod
    def _aux_fill(self, res, name, small_name, fun, single):

        pass


    @abstractmethod
    def _aux_groupfill(self, res, name, fun):

        pass




    def least_nan(self, **kwargs):

        """
        Return a dataset with only the repetition with the least NaNs. Uses only a certain eye to select.
        """

        nan_name = self._get_nan_name()

        min_val = 1.1
        min_idx = 0 

        for i in range(len(self)):

            val = self.get_val(i, nan_name, **kwargs)

            if not np.isnan(val) and val < min_val:
                min_idx = i
                min_val = val

        # Create the dataset

        return type(self)([self._data[min_idx]])
    

    def get_rep(self, key):

        """
        Returns a specific repetition or a slice, as a new FeatureDataset.
        """

        aux = self._data[key]

        if isinstance(key, int):

            aux = [aux]
        
        return type(self)(aux) 
            
            


    def threshold_nan(self, threshold=1.0, **kwargs):


        """
        Return a dataset with only the repetitions below a certain number of missing values. 
        """

        res = type(self)()

        for i in range(len(self)):

            nan_name = self._get_nan_name(i)

            val = self.get_val(i, nan_name, **kwargs)

            if not np.isnan(val) and val <= threshold:
                res.add_rep(self._data[i])

        # Create the dataset

        return res
    

    
