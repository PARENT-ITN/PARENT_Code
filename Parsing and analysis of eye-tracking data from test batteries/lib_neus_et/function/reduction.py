import numpy as np
import warnings

def exp_rt(t):

    """
    Uses the reduction taken from Pel et al. and Kooiker et al. 
    The final reaction time is the minimum X_(0) plus one third of the time constant of an exponential CDF fitted to the remaining X_(i) - X(0). In this case we simplify and don't fit with
    means squares but instead use a sufficient statistic for the mean.
    """

    t = np.sort(t)

    if len(t) == 0 or np.isnan(t[0]):

        return np.nan
    
    if len(t) == 1 or np.isnan(t[1]):

        return t[0]
    
    return (2 * t[0]  + np.nanmean(t[1:])) / 3 