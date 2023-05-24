"""Evolution algorithms with python.
The :mod:`__init__` module is intended to initialise the package and contain
the master classes to carry on the evolution. 
"""
from gevopy.genetics import GenotypeModel
from gevopy.app import App

__all__ = ["App", "GenotypeModel"]
