"""Examples module for users on how to create algorithms and testing"""
from dataclasses import dataclass

from gevopy import algorithms
from gevopy.tools import crossover, mutation, selection


# ------------------------------------------------------------------
# Basic Uniform Selection ------------------------------------------
# This algorithm selects both matching partners using an uniform
# distribution. Due to the fact that fitness does not play any role
# on the selection of phenotypes, adaptation to the environment is
# fully random.
@dataclass
class BasicUniform(algorithms.Standard):
    selection1 = selection.Uniform()
    selection2 = selection.Uniform()
    crossover = crossover.OnePoint()
    mutation = mutation.SinglePoint()


# ------------------------------------------------------------------
# Simple Ponderated Selection --------------------------------------
# This algorithm selects one matching partners using a ponderated
# distribution and the second with an uniform. Ponderated gives all
# phenotypes a chance to reproduce proportional to the fitness score.
# However, the posibility that best matches best is reduced agains
# two times ponderated.
@dataclass
class BasicPonderated(algorithms.Standard):
    selection1 = selection.Ponderated()
    selection2 = selection.Uniform()
    crossover = crossover.OnePoint()
    mutation = mutation.SinglePoint()
