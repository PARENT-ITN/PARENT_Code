import numpy as np
import warnings

# NOTE: no dependencies to other scripts of this library


def ME(x, y, ord=None):

    """
    Mean error between two arrays. By using the norm function from Numpy.

    :param x: First array.
    :type x: np.ndarray
    :param y: Second array.
    :type y: np.ndarray
    :param ord: Norm order.
    :type ord: {non-zero int, inf, -inf, ‘fro’, ‘nuc’}
    """

    if x.shape != y.shape:
        raise ValueError(f"The dimensions of the two arrays must be the same, gotten {x.shape} and {y.shape} instead")
    
    if len(x.shape) > 1:
        raise ValueError('This function can only be applied to monodimensional arrays.')
    
    diff = x - y

    diff = diff[~np.isnan(diff)]
    
    if type(ord)==int:

        return np.linalg.norm(diff, ord=ord) / (diff.size ** (1/ord))
    
    return np.linalg.norm(diff, ord=ord) / (diff.size ** (1/ord))
    





def align_closest(aligned, to_align):
    """
    Aligns one time series to the other, by taking the closest data point.
    """

    t1 = aligned[:,0]
    t2 = to_align[:,0]


    ind = np.argmin(np.abs(t1.reshape((1,-1)) - t2.reshape((-1,1))), 0)


    # Remove dumplicates
    #ind, u = np.unique(ind, return_index=True)

    res = np.concatenate((t1[:,None], to_align[ind,1:]), axis=1)

    return res


def LT(x, low, high, reverse=False, total_time=False):

    """
    Counts how many samples from x are in an interval. Returns also the ratio of NaNs.

    :param total_time: If True gives looking time over total time, otherwise returns looking time over time looking at the screen.
    :type total_time: bool
    """
    not_nan = np.count_nonzero(~np.isnan(x))
    if not_nan == 0:
        return 0.0, 1.0
    if reverse:
        x = 1-x

    if total_time:
        return np.count_nonzero((x > low) & (x <= high))/len(x), 1.0 - not_nan/len(x)
    else:
        return np.count_nonzero((x > low) & (x <= high))/not_nan, 1.0 - not_nan/len(x)
    

def MISS(x, max_nan = 0):

    """
    Counts missing values but only gaps that are bigger than max_nan.
    Takes as input an array of booleans 0 - missing, 1 - valid.
    """

    # Only sum gaps in missing values that are bigger than a certain threshold a
    idx = np.where(np.concatenate(([1], x, [1]), axis=0))  # Finds the ones
    d = np.diff(idx) - 1   # Gaps in valid values
    d[d<max_nan] = 0
    return np.sum(d)/len(x)

def divide_by_gaps(x, max_nan):

    """
    Returns a list of splices of the original array if they are separated by continuous gaps of NaNs of lenghth > max_nan.
    """

    miss = np.isnan(x)
    diff = np.diff(np.concatenate(([0], miss.astype('int'), [0])))
    ends = np.where(diff==1)[0]
    starts = np.where(diff==-1)[0]

    keep = starts - ends > max_nan

    starts = starts[keep]
    ends = ends[keep]


    # Return empty array if there are no gaps

    if len(ends) == 0:
        return np.array([]), np.array([]), [x]

    # Remove the first start if the array begins with a gap

    if ends[0] == 0:
        ends = ends[1:]
    else:
        starts = np.concatenate(([0], starts))

    # Remove the last if the array ends with a gaps

    if starts[-1] == len(x):
        starts = starts[:-1]

    if len(starts) > len(ends):
        ends = np.concatenate((ends, [len(x)]))

    if len(starts) != len(ends):
        print(starts)
        print(ends)
        assert False

    # Attach everything and return
    list_splits = []
    for i in range(len(starts)):

        list_splits.append(x[starts[i]:ends[i]])

    return starts, ends, list_splits



def compute_speed(time, pos, method = 'forward'):

    """
    Compute speed by finite differences.
    Methods:
    forward - Forward Euler.
    center - Nicholson differences.
    """

    if time.shape[0] != pos.shape[0]:

        raise ValueError(f"The arrays need to have the same shape instead {time.shape} and {pos.shape} were given.")


    if method == 'forward':

        return np.diff(pos, axis=0, append=np.nan) / np.diff(time, append=np.nan)

    elif method == 'center':

        if len(pos.shape) == 1:
            pos = pos[:,None]

        fwd = np.diff(pos[1:,:], axis=0, append=np.nan, prepend=np.nan) / np.diff(time[1:], append=np.nan, prepend=np.nan)[:,None]
        bck = np.diff(pos[:-1,:], axis=0, append=np.nan, prepend=np.nan) / np.diff(time[:-1], append=np.nan, prepend=np.nan)[:,None]


        return .5 * np.squeeze(fwd + bck)
    

