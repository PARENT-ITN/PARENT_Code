"""
Generic non abstract task class definition.
"""

from .base import Task_base
from lib_neus_et.datasets.feature_data import FeatureDataset

import numpy as np




class Generic(Task_base):

    # These are the features
    _feat_names = {'nan' : ('Percentage missing values.', float, '{:.3f}')}

    _task_prefix = 'generic'
    _task_name = 'Generic'


    def __init__(self, data, params):

        super().__init__(data, params)





    def _compute(self, verbose = True) -> FeatureDataset:

        """
        Computed the features for task Generic and returns them.

        :param verbose: Toggles verbose execution.
        :type verbose: bool
        :return: The features dataset for the task.
        :rtype: FeatureDataset

        """

        # Create dataset without values

        names = [self._task_prefix + '.' + s for s in self._feat_names.keys()]
        features = FeatureDataset(names)

        # Code goes here

        # Example

        for eye in ['L', 'R', 'M']:

            miss = 0.0 # compute feature

            features.set_val(miss, 0, 'generic.nan', eye) # add feature to dataset

        
        # Features that need both eyes together

            

        return features
    





    def _plot_aux(self, fig, plot_features=False):

        """
        Auxilliary function to plot gaze trajectories in task Generic. Plots scanpaths.

        :param fig: The figure where to plot.
        :type fig: matplotlib.pyplot.figure
        :param plot_features: If True the features computed for the gaze path will be shown as a table next to the plot.
        :type plot_features: bool
        :return: Title for the plot.
        :rtype: str

        """

        N = 2 if plot_features else 1

        X_L = self._et.get_gaze('L')
        X_R = self._et.get_gaze('R')

        # Plot the x coordinate
        ax = fig.add_subplot(1, N, 1)
        ax.plot(X_L[:,1], X_L[:,2], 'b')
        ax.plot(X_R[:,1], X_R[:,2], 'r')
        ax.set_ylim([0.0, 1.0])
        ax.set_xlim([0.0, 1.0])
        ax.legend(['Left eye', 'Right eye'])
        ax.set_xlabel('x coordinate')
        ax.set_ylabel('y coordinate')

        return 'Generic task'
    

    def _best_eye_func(self, *kwargs):


        ret = {'generic.nan' : {'join' : False, 'M' : True, 'fun' : lambda x : np.nan}}

        return ret
    