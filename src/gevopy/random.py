"""Evolution algorithm module to generate random units, for example random
chromosomes.
"""

import numpy as np

from gevopy import genetics


def haploid(size):
    """Returns a random standard Haploid chromosome.
    :param size: Integer with chromosome size
    """
    data = np.random.randint(2 ** 1, size=size, dtype="uint8")
    return genetics.Haploid(data)


def diploid(size):
    """Returns a random standard Diploid chromosome.
    :param size: Integer with chromosome size
    """
    data = np.random.randint(2 ** 2, size=size, dtype="uint8")
    return genetics.Diploid(data)


def triploid(size):
    """Returns a random standard Triploid chromosome.
    :param size: Integer with chromosome size
    """
    data = np.random.randint(2 ** 3, size=size, dtype="uint8")
    return genetics.Triploid(data)
