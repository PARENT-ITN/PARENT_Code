"""
Function to detect fixations and saccades
"""
import numpy as np
from .function.function import divide_by_gaps, compute_speed

def dispersion(X):

    """
    Compute the dispersion of consecutive data points, as:

    D = [max(x) - min(x)] + [max(y) - min(y)]

    :param X: Gaze positions and times.
    :type X: numpy.ndarray, size[1] must be 3.

    """

    if X.shape[1] == 3:
        X = X[:,1:]

    return np.sum(np.nanmax(X, axis=0) - np.nanmin(X, axis=0))




def idt(pos, time, minimum_duration, dispersion_threshold, max_nan = 0, return_idx = False):

    """
    Function to identify fixations based on the I-DT algorithm.

    Based on the pseudocode in Salvucci and Goldberg 2000, and adapted from the
    implementation of PyMovements library. (WIP)

    :param pos: Gaze position array.
    :type pos: numpy.ndarray
    :param time: Time array.
    :type time: numpy.ndarray
    :param minimum_duration: Minimum duration (in seconds) of a fixation.
    :type minimum_duration: float
    :param dispersion_threshold: Maximum dispersion of a fixation.
    :type dispersion_threshold: float
    :param max_nan: Maximum number of consecutive missing values that can be ignored.
    :type max_nan: int
    :param return_idx: If True function will return the idexes of the fixations, if False the times.
    :type return_idx: bool

    :return: A dictionary of: start times, end times, durations, and centers of the fixations.
    :rtype: dict[numpy.ndarray]

    """
    # Include nans decides if we must split the same fixation if there are nans in the middle.
    # Maybe put a max number of nan to have

    return {'Starts' : np.array([]), 'Ends' : np.array([]), 'Durations' : np.array([]), 'Centers' : np.array([])}




# ------------------------------------------------------------------------------

def dist_fix(pos, time, minimum_duration=50, max_dist=25, max_nan = 0, return_idx=False):

    """Detects fixations, defined as consecutive samples with an inter-sample
    distance of less than a set amount. Takes into account only non missing values.

    
    :param pos: Gaze position array.
    :type pos: numpy.ndarray
    :param time: Time array.
    :type time: numpy.ndarray
    :param minimum_duration: Minimum duration (in seconds) of a fixation.
    :type minimum_duration: float
    :param dispersion_threshold: Maximum dispersion of a fixation.
    :type dispersion_threshold: float
    :param max_nan: Maximum number of consecutive missing values that can be ignored.
    :type max_nan: int
    :param return_idx: If True function will return the idexes of the fixations, if False the times.
    :type return_idx: bool

    :return: A dictionary of: start times, end times, durations, and centers of the fixations.
    :rtype: dict[numpy.ndarray]

    """

    x = pos[:,0]
    y = pos[:,1]

    Sfix = []
    Efix = []
    mfix = []

    # loop through all coordinates
    # Finds the first non missing value

    ind = np.where(np.logical_and(~np.isnan(x), ~np.isnan(y)))[0]


    # Start from the first non-missing value

    if ind.size < 2:
        # No data
        return np.array([]), np.array([]), np.array([]), np.array([])

    si = ind[1]

    fixstart = False
    #print('New:{}'.format(si))
    for i in ind[2:]:
        # calculate Euclidean distance from the current fixation coordinate
        # to the next coordinate (this uses the screen size)
        dist = (((x[si]-x[i]))**2 + ((y[si]-y[i]))**2)**0.5

        # check if the next coordinate is below maximal distance
        if dist <= max_dist and not fixstart and i<ind[-1]:
            # start a new fixation
            si = i
            fixstart = True
            Sfix.append(time[i])
        elif (dist > max_dist or i == ind[-1]) and fixstart:
            # end the current fixation
            fixstart = False
            # only store the fixation if the duration is ok
            # Check how many NaNs there are
            num_nan = np.count_nonzero(np.isnan(x[si:i])) 

            if time[i-1]-Sfix[-1] >= minimum_duration and num_nan <= max_nan:
                Efix.append(time[i-1])
                mfix.append([np.nanmedian(x[si:i]), np.nanmedian(y[si:i])])
                #print('New end ', i)
                #print('Dist new ', dist)
            # delete the last fixation start if it was too short
            else:
                Sfix.pop(-1)
            si = i
        elif not fixstart:
            si = i

    # Converts to numpy and return

    Sfix = np.array(Sfix, dtype='float')
    Efix = np.array(Efix, dtype='float')
    mfix = np.array(mfix, dtype='float').reshape(-1, 2)

    assert len(Sfix) == len(Efix) # Remove this part at some point

    return Sfix, Efix, Efix - Sfix, mfix

# ------------------------------------------------------------------------------
def dist_fix_old(pos, time, minimum_duration=50, max_dist=25, max_nan = 0, return_idx=False):

    """Detects fixations, defined as consecutive samples with an inter-sample
    distance of less than a set amount. Ignores missing values at the beginning of the array.

    
    :param pos: Gaze position array.
    :type pos: numpy.ndarray
    :param time: Time array.
    :type time: numpy.ndarray
    :param minimum_duration: Minimum duration (in seconds) of a fixation.
    :type minimum_duration: float
    :param dispersion_threshold: Maximum dispersion of a fixation.
    :type dispersion_threshold: float
    :param max_nan: Maximum number of consecutive missing values that can be ignored.
    :type max_nan: int
    :param return_idx: If True function will return the idexes of the fixations, if False the times. (NOT IMPLEMENTED)
    :type return_idx: bool

    :return: A dictionary of: start times, end times, durations, and centers of the fixations. 
    :rtype: dict[numpy.ndarray]

    """
    
    assert pos.shape[0] == time.shape[0], "All the arrays must have the same shape"

    x = pos[:,0]
    y = pos[:,1]
    
    Sfix = []
    Efix = []
    mfix = []

	# loop through all coordinates
	# Finds the first non missing value

    ind = np.where(np.logical_and(~np.isnan(x), ~np.isnan(y)))[0]
	

	# Start from the first non-missing value

    if ind.size < 2:
		# No data
	    return np.array([]), np.array([]), np.array([]), np.array([])
    
    si = ind[1]

    fixstart = False
	#print('New:{}'.format(si))
    for i in ind[2:]:
        # calculate Euclidean distance from the current fixation coordinate
        # to the next coordinate (this uses the screen size)
        dist = (((x[si]-x[i]))**2 + ((y[si]-y[i]))**2)**0.5

        # check if the next coordinate is below maximal distance
        if dist <= max_dist and not fixstart and i<ind[-1]:
            # start a new fixation
            si = i
            fixstart = True
            Sfix.append(time[i])
        elif (dist > max_dist or i == ind[-1]) and fixstart:
            # end the current fixation
            fixstart = False
            # only store the fixation if the duration is ok
            if time[i-1]-Sfix[-1] >= minimum_duration:
                Efix.append(time[i-1])
                mfix.append([np.nanmedian(x[si:i]), np.nanmedian(y[si:i])])
                #print('New end ', i)
                #print('Dist new ', dist)
            # delete the last fixation start if it was too short
            else:
                Sfix.pop(-1)
            si = i
        elif not fixstart:
            si = i

    Sfix = np.array(Sfix, dtype='float')
    Efix = np.array(Efix, dtype='float')
    mfix = np.array(mfix, dtype='float').reshape(-1, 2)

    assert len(Sfix) == len(Efix)

    return Sfix, Efix, Efix - Sfix, mfix


def fix_original(pos, time, minimum_duration=50, max_dist=25, max_nan = 0, return_idx=False):

    """Detects fixations, defined as consecutive samples with an inter-sample
    distance of less than a set amount. The original function, adapted to new return types.

    
    :param pos: Gaze position array.
    :type pos: numpy.ndarray
    :param time: Time array.
    :type time: numpy.ndarray
    :param minimum_duration: Minimum duration (in seconds) of a fixation.
    :type minimum_duration: float
    :param dispersion_threshold: Maximum dispersion of a fixation.
    :type dispersion_threshold: float
    :param max_nan: Maximum number of consecutive missing values that can be ignored.
    :type max_nan: int
    :param return_idx: If True function will return the idexes of the fixations, if False the times. (NOT IMPLEMENTED)
    :type return_idx: bool

    :return: A dictionary of: start times, end times, durations, and centers of the fixations.
    :rtype: dict[numpy.ndarray]

    """


    # empty list to contain data

    assert pos.shape[0] == time.shape[0], "All the arrays must have the same shape"

    x = pos[:,0]
    y = pos[:,1]

    Sfix = []

    Efix = []

    mfix = []



    # loop through all coordinates

    si = 0
    fixstart = False

    #print('Old:{}'.format(si))
    # aux = 0
    for i in range(si+1,len(x)):

        if np.isnan(x[i]) or np.isnan(y[i]): continue

        # calculate Euclidean distance from the current fixation coordinate

        # to the next coordinate

        #aux+=1
        dist = (((x[si]-x[i]))**2 + ((y[si]-y[i]))**2)**0.5

        # check if the next coordinate is below maximal distance

        if dist <= max_dist and not fixstart:

            # start a new fixation

            si = 0 + i

            fixstart = True

            Sfix.append([time[i]])
        elif dist > max_dist and fixstart:

            # end the current fixation

            fixstart = False

            # only store the fixation if the duration is ok

            if time[i-1]-Sfix[-1][0] >= minimum_duration:

                Efix.append(Sfix[-1][0])
                mfix.append([x[si], y[si]])


            # delete the last fixation start if it was too short

            else:

                Sfix.pop(-1)

            si = 0 + i

        elif not fixstart:

            si += 1


    Sfix = np.array(Sfix, dtype='float')
    Efix = np.array(Efix, dtype='float')
    mfix = np.array(mfix, dtype='float').reshape(-1, 2)

    assert len(Sfix) == len(Efix)

    return Sfix, Efix, Efix - Sfix, mfix




def vel_acc_sacc(pos, time, minlen=5, maxvel=40, maxacc=340):

    """Detects saccades, defined as consecutive samples with an inter-sample
    velocity of over a velocity threshold or an acceleration threshold.

    :param pos: Gaze position array.
    :type pos: numpy.ndarray
    :param time: Time array.
    :type time: numpy.ndarray
    :param minlen: minimal length of saccades in milliseconds; all detected saccades with len(sac) < minlen will be ignored (default = 5)
    :type minlen: int
    :param maxvel: velocity threshold in position/second (default = 40)
    :type maxvel: float
    :param maxacc: acceleration threshold in position / second**2 (default = 340)
    :type maxacc: float
    """

    x = pos[:,0]
    y = pos[:,1]

    if x.shape != time.shape:
        raise ValueError("All the arrays must have the same shape")

    # CONTAINERS
    Ssac = []
    Esac = []

    # INTER-SAMPLE MEASURES
    # the distance between samples is the square root of the sum
    # of the squared horizontal and vertical interdistances

    # VELOCITY AND ACCELERATION
    # the velocity between samples is the inter-sample distance
    # divided by the inter-sample time
    vel = compute_speed(time, pos)
    # the acceleration is the sample-to-sample difference in
    # eye movement velocity
    acc = np.diff(vel)

    # SACCADE START AND END
    t0i = 0
    stop = False
    while not stop:
        # saccade start (t1) is when the velocity or acceleration
        # surpass threshold, saccade end (t2) is when both return
        # under threshold

        # detect saccade starts
        sacstarts = np.where(np.logical_or(vel[1+t0i:] > maxvel, np.abs(acc[t0i:]) > maxacc))[0]
        if len(sacstarts) > 0:
            # timestamp for starting position
            t1i = t0i + sacstarts[0] + 1
            if t1i >= len(time)-1:
                t1i = len(time)-2
            t1 = time[t1i]

            # add to saccade starts
            Ssac.append([x[t1i], y[t1i], t1])

            # detect saccade endings
            sacends = np.where(np.logical_and(vel[1+t1i:] < maxvel, np.abs(acc[t1i:]) < maxacc))[0]
            if len(sacends) > 0:
                # timestamp for ending position
                t2i = sacends[0] + 1 + t1i + 2
                if t2i >= len(time):
                    t2i = len(time)-1
                t2 = time[t2i]
                dur = t2 - t1

                # ignore saccades that did not last long enough
                if dur >= minlen:
                    # add to saccade ends
                    Esac.append([x[t2i], y[t2i], t2])
                else:
                    # remove last saccade start on too low duration
                    Ssac.pop(-1)

                # update t0i
                t0i = t2i
            else:
                # If the saccade goes over the end of the test we are not interested in it
                Ssac.pop(-1)
                stop = True
        else:
            stop = True

    Ssac = np.array(Ssac, dtype='float')
    Esac = np.array(Esac, dtype='float')
    if Ssac.size != 0:
        Dsac = Esac[:,2] - Ssac[:,2]
    else:
        Dsac = np.array([], dtype='float')

    return Ssac, Esac, Dsac


def ivt(pos, time, minlen=5, maxvel=40, max_nan = 0, return_idx=False):


    """
    Identification by velocity threshold.
    """

    return 0
