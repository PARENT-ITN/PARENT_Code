import numpy as np
import scipy.signal as signal


def medfilter(x, window_size=3):

    return signal.medfilt(x, kernel_size=window_size)