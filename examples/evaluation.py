"""Examples module for users on how to create fitness functions and testing"""
import numpy as np

from gevopy.fitness import FitnessModel


# ------------------------------------------------------------------
# Most Ones --------------------------------------------------------
# This fitness object scores each phenotypes with the amount of ones
# the phenotype has in it's chromosome attribute.
class MostOnes(FitnessModel):
    """Fitness model count amount of '1' in the chromosome"""

    def score(self, phenotype):
        return phenotype.chromosome.count(1)


# ------------------------------------------------------------------
# Fitness ----------------------------------------------------------
# This fitness object scores each phenotypes completelly random.
class Random(FitnessModel):
    """Fitness model assigns a random score between 0-1"""
    # pylint: disable=attribute-defined-outside-init

    def setup(self, phenotypes):
        """Set up method to run once per generation"""
        self.executed = True

    def score(self, phenotype):
        """Method to use for evaluation phenotypes"""
        return np.random.random()
