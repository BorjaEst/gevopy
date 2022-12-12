"""Evolution algorithms with python.
The :mod:`__init__` module is intended to initialise the package and contain
the master classes to carry on the evolution. From this module, the user
can call for the `Experiment` in order to generate an instance with the
required methods and data to evolve some initial population to a desired
state.
"""

from gevopy.experiments import Experiment
from gevopy.fitness import FitnessModel
from gevopy.genetics import GenotypeModel

__all__ = [
    "Experiment",
    "FitnessModel",
    "GenotypeModel",
]
