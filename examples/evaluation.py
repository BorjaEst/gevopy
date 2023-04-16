"""Examples module for users on how to create fitness functions and testing"""
import numpy as np

from gevopy.fitness import FitnessModel


# ------------------------------------------------------------------
# Most Ones --------------------------------------------------------
# This fitness object scores each genotypes with the amount of ones
# the genotype has in it's chromosome attribute.
class MostOnes(FitnessModel):
    """Fitness model count amount of '1' in the chromosome"""

    def score(self, genotype):
        return genotype.chromosome.count(1)


# ------------------------------------------------------------------
# Random -----------------------------------------------------------
# This fitness object scores each genotypes completelly random.
class Random(FitnessModel):
    """Fitness model assigns a random score between 0-1"""
    # pylint: disable=attribute-defined-outside-init

    def setup(self, genotypes):
        """Set up method to run once per generation"""
        self.executed = True

    def score(self, genotype):
        """Method to use for evaluation genotypes"""
        return np.random.random()
