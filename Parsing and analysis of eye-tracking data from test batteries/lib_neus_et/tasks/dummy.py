"""
Generic non abstract task class definition.
"""

from .base import Task_base
from lib_neus_et.datasets.feature_data import FeatureDataset
from lib_neus_et.function.function import MISS

import numpy as np




class Dummy(Task_base):

    # These are the features
    _feat_names = {'nan' : ('Percentage missing values.', float, '{:.3f}'),
                   'fix_num' : ('Number of fixations.', int, '{}'),
                   'cat' : ('Category of dummy. (Always A in example).', str, '{}')}

    _task_prefix = 'dummy'
    _task_name = 'Dummy'


    def __init__(self, data, params):

        super().__init__(data, params)





    def _compute(self, fix_params, max_nan=10, verbose = True) -> FeatureDataset:

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

            V = self._et.get_valid(eye)[:,1] # Valid values

            fix = self._et.get_fixations(eye, **fix_params)

            # Nans

            features.set_val(MISS(V, max_nan=max_nan), 0, 'dummy.nan', eye)

            # Number of fixations

            features.set_val(len(fix['Starts']), 0,  'dummy.fix_num', eye)


        
        # Features that need both eyes together

        features.set_val('A', 0, 'dummy.cat', 'join')

            

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

        pos_plot = 3 if plot_features else 2

        X_L = self._et.get_gaze('L')
        X_R = self._et.get_gaze('R')

        # Plot the x coordinate
        ax = fig.add_subplot(2, N, 1)
        ax.plot(X_L[:,0], X_L[:,1], 'b')
        ax.plot(X_R[:,0], X_R[:,1], 'r')
        ax.set_ylim([0, 1])
        ax.legend(['Left eye', 'Right eye'], loc='upper left')
        ax.set_xticks([])
        #plt.xlabel('Eye-tracker time', fontsize=20)
        ax.set_ylabel('x coordinate')

        # Plot y coordinate
        ax = fig.add_subplot(2, N, pos_plot)
        ax.plot(X_L[:,0], X_L[:,2], 'b')
        ax.plot(X_R[:,0], X_R[:,2], 'r')
        ax.set_ylim([0, 1])
        ax.legend(['Left eye', 'Right eye'], loc='upper left')
        ax.set_xticks([])
        ax.set_xlabel('Eye-tracker time')
        ax.set_ylabel('y coordinate')

        return 'Dummy task'
    

    def _best_eye_func(self, *kwargs):


        ret = {'dummy.nan' : {'join' : False, 'M' : True, 'fun' : lambda x : np.nan},
               'dummy.fix_num' : {'join' : False, 'M' : False, 'fun' : np.nanmin},
               'dummy.cat' : {'join' : True, 'M' : False, 'fun' : lambda x : np.nan}}

        return ret
    