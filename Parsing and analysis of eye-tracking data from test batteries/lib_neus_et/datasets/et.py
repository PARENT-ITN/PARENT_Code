"""
Defines ET_data class
"""

import numpy as np
import warnings
from copy import deepcopy as dc

import lib_neus_et.detectors as detectors

from lib_neus_et.function.function import align_closest


class ET_Data:

    """
    Basic class to store eye-tracking data.
    It parses the data points into Numpy arrays and computes the average of the two eyes
    when created.

    :param data: The raw eye-tracking data points. As saved by the Nesu test.
    :type data: list of dictionaries.
    :param dt: The time unit of measurement of the device. 1 is seconds.
    :type dt: float
    :param sampling: Sampling rate of the device in [Hz].
    :type sampling: float
    """

    def __init__(self, data, screen, dt = 1e-6, sampling = 60.0):

        self.sampling_rate = sampling
        self.dt = dt
        self.screen = screen


        # Parse data

        self._t0, self._time, self._gaze, self._valid, self._pupil, self._steps, self._other = self._parse(data)

        self._empty = len(self._time) == 0

        # Compute the averge of the two eyes
        self._average_eyes()

        # If needed update steps and other

        self._parse_steps()
        self._parse_other()


    def deepcopy(self):
        return dc(self)
    
    def __len__(self):

        # Length of gaze data

        return len(self._time)


    def splice(self, t0, tf):

        """
        Returns a copy of the class with only the values between two time instants.

        :param t0: Start time.
        :type t0: float or int.
        :param tf: End time.
        :type tf: float or int
        """
        if tf == -1:

            tf = self._time[-1]
        idx = self._splice_idx(t0, tf)
        cp = self.deepcopy()


        # Take only the correct values

        # Time

        cp._time = self._time[idx]

        # Arrays

        for k in self._gaze:

            cp._gaze[k] = cp._gaze[k][idx,:]
            cp._valid[k] = cp._valid[k][idx]
            cp._pupil[k] = cp._pupil[k][idx]

        # List (steps)
        cp._steps = []

        for s in self._steps:
            if s['time'] >= t0 and s['time'] < tf:
                cp._steps.append(s)
            elif s['time'] >= tf:
                break

        # Other can be anything so we delegate to another function

        cp._other = self._splice_other(t0, tf, idx)

        return cp

    def empty(self):
        """
        Check if the class is empty.

        """
        return self._empty

# Auxilliary ------------------------------

    def _parse(self, data):

        gaze = {'L' : [], 'R' : []}
        time = []
        valid = {'L' : [], 'R' : []}
        pupil = {'L' : [], 'R' : []}
        steps = []
        other = []

        for i,rec in enumerate(data):

            # Gaze point

            if i == 0:
                t0 = rec['time']

            if 'type' in rec and rec['type'] == 'gaze':

                # Time
                time.append(rec['time'] - t0)

                # Gaze
                gaze['L'].append(list(rec['left']['gaze_screen'].values()))
                gaze['R'].append(list(rec['right']['gaze_screen'].values()))

                # Valid

                # Only consider valid gaze points inside the screen
                valid['L'].append(bool(rec['left']['gaze_valid']) and np.bitwise_and(np.array(gaze['L'][-1]) <= 1.0, np.array(gaze['L'][-1])>= 0.0).all())
                valid['R'].append(bool(rec['right']['gaze_valid']) and np.bitwise_and(np.array(gaze['R'][-1]) <= 1.0, np.array(gaze['R'][-1])>= 0.0).all())

                # Pupil
                pupil['L'].append(rec['left']['pupil_diameter'])
                pupil['R'].append(rec['right']['pupil_diameter'])

            elif 'type' in rec and rec['type'] == 'step':

                rec['time'] = (rec['time'] - t0) * self.dt
                steps.append(rec)

            else:
                rec['time'] = (rec['time'] - t0) * self.dt
                other.append(rec)

        # Convert to numpy arrays

        time = np.array(time, dtype='int64') * self.dt

        for k in gaze:

            gaze[k] = np.array(gaze[k], dtype='float32')
            pupil[k] = np.array(pupil[k], dtype='float32')
            valid[k] = np.array(valid[k], dtype='bool')


        return t0 * self.dt, time, gaze, valid, pupil, steps, other


    def _average_eyes(self):

        if self._empty:
            self._valid.update({'M' : np.array([])})
            self._gaze.update({'M' : np.array([])})
            self._pupil.update({'M' : np.array([])})
            return

        self._valid.update({'M' : np.logical_or(self._valid['L'], self._valid['R'])})

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)

            aux_gaze = np.nanmean(np.stack((self._gaze['L'], self._gaze['R']), axis=2), axis=2)
            aux_pupil = np.nanmean(np.stack((self._pupil['L'], self._pupil['R']), axis=1), axis=1)


        self._gaze.update({'M' : aux_gaze})
        self._pupil.update({'M' : aux_pupil})


    def _splice_idx(self, t0, tf, from_zero = True):
        if not from_zero:
            t0 -= self._t0
            tf -= self._t0
        return np.logical_and((self._time >=t0), (self._time < tf))






# Smoothig --------------------------------

    def align_time(self):
        """
        Align the sampling times to a uniform grid with intervals compatible with the sampling rate.
        This might cause a loss of data.
        """
    
        new_time = np.arange(int(self.sampling_rate * (self._time[-1] - self._time[0]))) / self.sampling_rate + self._time[0] # in seconds

        new_time = new_time.reshape((-1,1))

        # Align everything

        for eye in ['L', 'R', 'M']:

            self._gaze[eye] = align_closest(new_time, self.get_gaze(eye))[:,1:]
            self._valid[eye] = align_closest(new_time, self.get_valid(eye))[:,1]
            self._pupil[eye] = align_closest(new_time, self.get_pupil(eye))[:,1]

        
        # And time
        self._time = new_time.squeeze()



# Saccades and fixations ------------------


    def get_fixations(self, eye, mode = 'position', method = 'new',**kwargs):

        """
        Return fixations of the selected eye.
        Mode decides in waht coordinates the fixations are computed.

        """

        method_name = {'new' : 'dist_fix',
                       'old' : 'dist_fix_old',
                       'original' : 'fix_original',
                       'idt' : 'idt'}

        X = self.get_gaze(eye)

        t = X[:,0]
        pos = X[:,1:]

        pos = self.screen.convert(pos, input='position', output=mode)

        fun = detectors.__getattribute__(method_name[method])
        
        start, end, dur, mfix = fun(pos, t, **kwargs)

        # Convert centers back to screen position

        if len(mfix)>0:

            mfix = self.screen.convert(mfix, input=mode, output='position')


        return {'Starts' : start, 'Ends' : end, 'Durations' : dur, 'Centers' : mfix}


    def get_saccades(self, eye, **kwargs):

        X = self.get_gaze(eye)

        start, end, dur = detectors.sac_id(X[:,1:], X[:,0], **kwargs)

        return {'Starts' : start, 'Ends' : end, 'Durations' : dur}

# Getters ---------------------------------

    def get_gaze(self, eye):
        if eye not in self._gaze.keys():

            raise ValueError('Error: eyes specified does not exist. Try "L", "R" or "M".')
  

        return np.concatenate((self._time[:,None], self._gaze[eye]), axis=1)

    def get_valid(self, eye):

        if eye not in self._valid.keys():

            raise ValueError('Error: eyes specified does not exist. Try "L", "R" or "M".')
   

        return np.stack((self._time, self._valid[eye]), axis=1)

    def get_pupil(self, eye):

        if eye not in self._pupil.keys():

            raise ValueError('Error: eyes specified does not exist. Try "L", "R" or "M".')
     

        return np.stack((self._time, self._pupil[eye]), axis=1)


    def get_steps(self):

        return self._steps


    def get_other(self):
        return self._other



# To override for specific use -----------------------

    def _parse_steps(self):
        pass

    def _parse_other(self):
        pass

    def _splice_other(self, t0, tf, idx):

        res = []
        for s in self._other:

            if s['time'] >= t0 and s['time'] < tf:
                res.append(s)
            elif s['time'] >= tf:
                break
        return res
