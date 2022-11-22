"""Module for test fitness"""
import time

from gevopy import fitness


class TimeFitness(fitness.FitnessModel):
    """Fitness model to use on test requirements"""
    # pylint: disable=attribute-defined-outside-init

    def setup(self, phenotypes):
        """Set up method to run once per generation"""
        self.executed = True

    def score(self, phenotype):
        """Method to use for evaluation phenotypes"""
        time.sleep(0.001)
        return time.time()
