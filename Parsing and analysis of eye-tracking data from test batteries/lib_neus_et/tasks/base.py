"""
Base abstract task class definition.
"""
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import numpy as np
import warnings
# from lib_neus_2.et import et_data

from lib_neus_et.datasets import FeatureDataset, FeatureDatasetBestEye


class Task_base(ABC):

    def __init__(self, data, params):

        self._et = data
        self._params = params
        self._features = None
        self._last_compute_parameters = None

        self._features_be = None


    def compute(self, verbose=True, **kwargs):

        """
        Computes the features. First it checks if the computation parameters have changed since the last call. If they didn't it will return precomputed values.
        """

        if verbose: print(f'\nComputing features of {self._task_name} task.')

        if self._features is None or self._different_parameters(kwargs):

            self._features = self._compute(verbose=verbose, **kwargs)
            self._last_compute_parameters = kwargs

        return self._features
    
    def reduce(self, features, **kwargs):

        """
        Reduce a set of features according to a function. In base class is a wrapper of the FeatureData method. Can be overridden for specific tasks.
        """

        return features.reduce(**kwargs)


    def compute_best_eye(self, features = None, verbose=True, use_custom = False, funcs = None, force_eye = False, **kwargs):


        flag = True

        if features is None:

            flag = False

            features = self._features
        

        
        if features is None:

            return None
        
        if len(features) == 0:

            return FeatureDatasetBestEye()

        # We need to compute them

        if not use_custom:

            funcs = self._best_eye_func(**kwargs)


        res = FeatureDatasetBestEye()

        for rep in features._data:

            cur = {}

            # Create

            for name in rep:

                short_name = features._general_feat_name(name)

                if funcs[short_name]['join'] and (force_eye or rep[name]['join'] == rep[name]['join']): # check NaN, can't use isnan

                    # Use Joined value

                    cur.update({name : rep[name]['join']})

                elif funcs[short_name]['M'] and (force_eye or rep[name]['M'] == rep[name]['M']): # check NaN

                    # Use median eye value

                    cur.update({name : rep[name]['M']})

                else:

                    # Reduce the two eyes

                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=RuntimeWarning)

                        cur.update({name : funcs[short_name]['fun']([rep[name]['L'], rep[name]['R']])})

            res.add_rep(cur)


        if flag:
            self._features_be = res

            return self._features_be
        
        else:
            return res
        


    def plot(self, figsize = (12, 8), plot_features=False, compute_args={}, reduce=False, reduce_args={}, show=True, save=False, savename = './base'):

        fig = plt.figure(figsize=figsize)

        # Plot the table with the features if necessary

        if plot_features:

            val = self.compute(**compute_args)

            if reduce:
                val = self.reduce(val, **reduce_args)

            val = val.matrix(rep=0)

            # Use the correct visualization format

            val = [[f.format(x) for x in y] for y,f in zip(val, [u[2] for u in self._feat_names.values()])]


            ax = fig.add_subplot(122)
            the_table = ax.table(cellText=val, 
                                rowLabels=self.get_feat_names(), 
                                colLabels=['L', 'R', 'M', 'join'],
                                colColours=['cyan', 'orange', 'magenta', 'gray'],
                                loc='center')
            the_table.scale(0.75,2.5)
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(10)
            ax.axis('off')

        # Get the plot and title from overridden method

        title = self._plot_aux(fig, plot_features=plot_features)
        plt.suptitle(title)
        plt.subplots_adjust(left=0.2, bottom=0.2)
        plt.tight_layout()


        if show:
            plt.show()

        if save:

            plt.savefig(savename + '.png')

        plt.close()


    def get_feat_names(self, descriptions = False):


        if not descriptions:

            return list(self._feat_names.keys())
        else:
            return [s + ' : ' + u[0] for s,u in self._feat_names.items()]
        
    
    def explain_naming(self) -> None:

        """
        Prints an explaination of the naming convention of the current task.
        """

        print('Naming convention of {} task:\n'.format(self._task_name))

        print('<task>.<feature>\n')

        print(f'where <task> is "{self._task_prefix}" and <feature> is the name of the feature. For more information on the features use the method "get_feat_names".')


    def __str__(self):
        return self._task_name + '\n' + self._params.__repr__()
    
    def _different_parameters(self, kwargs):

        """
        Check if the compute parameters are different from the last call.
        """

        if self._last_compute_parameters is None:

            return True

        for k in kwargs:

            
            if k in self._last_compute_parameters and kwargs[k] != self._last_compute_parameters[k]:
                return True
                
        return False


    # Compute the features
    @abstractmethod
    def _compute(self, *kwargs, verbose = True):
        return False

     # Compute the features
    @abstractmethod
    def _best_eye_func(self, *kwargs):
        return False

    # Returns a matplotlib handle to the plot method so that features can be appended
    @abstractmethod
    def _plot_aux(self, fig, plot_features=False):
        return False

    # The names (and descriptions) of the features
    @abstractmethod
    def _feat_names(self):
        pass

    # The prefix of the task used in the pandas dictionary
    @abstractmethod
    def _task_prefix(self):
        pass

    # The task name
    @abstractmethod
    def _task_name(self):
        pass
