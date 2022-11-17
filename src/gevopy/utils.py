"""Module with utilities for the evolution modules"""

import numpy as np


def cross_chromosomes(chromosome_1, chromosome_2, points):
    """Crosses chromosome arrays on the specified points.
    :param chromosome_1: First array to cross
    :param chromosome_2: Second array to cross
    :param points: List of points to cross
    """
    ch1, ch2 = chromosome_1, chromosome_2  # Short code
    ax1, ax2 = np.split(ch1, points), np.split(ch2, points)
    ax1[1::2], ax2[1::2] = ax2[1::2], ax1[1::2]
    ch1[:], ch2[:] = np.concatenate(ax1), np.concatenate(ax2)
