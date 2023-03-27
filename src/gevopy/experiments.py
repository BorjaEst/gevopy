"""The :mod:`experiments` module is intended to contain the classes
needed to execute the defined evolutionary algorithms.

The main class Experiment allows the user to create an object where
to group all the definitions in order to prepare them for execution.
It allows to create context session where phenotypes can be added and
parameters can be modified.

Session method `run` triggers the execution of the evolution process
and returns an Execution object with all the relevant statistics and
parameters at the end of the evolution process.
"""

import contextlib
import logging
import uuid
from typing import List

from pydantic import BaseModel, Extra, Field, PrivateAttr

import gevopy.algorithms
import gevopy.database
import gevopy.fitness
import gevopy.tools
from gevopy.database import EmptyInterface
from gevopy.fitness import FitnessModel
from gevopy.genetics import GenotypeModel
from gevopy.tools import crossover, mutation, selection

# https://docs.python.org/3/howto/logging-cookbook.html
module_logger = logging.getLogger(__name__)

# Default algorithm for base experiment
DEFAULT_ALGORITHM = gevopy.algorithms.Standard(
    selection1=selection.Ponderated(),
    selection2=selection.Uniform(),
    crossover=crossover.OnePoint(),
    mutation=mutation.SinglePoint(mutpb=0.1),
    survival_rate=0.2,
)


class Experiment(BaseModel):
    """Base class for evolution experiments.
    Provides the essential attributes to create and run an experiment.
    :param name: Experiment name, if none, generates an uuid4 string
    :param database: Database interface object, defaults to EmptyInterface
    """
    database: gevopy.database.Interface = EmptyInterface()
    name: str = Field(default_factory=lambda: str(uuid.uuid4()))
    _logger: logging.Logger = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._logger = logging.getLogger(f"{__package__}.Experiment")
        self._logger = self.Logger(self._logger, {"exp": self})

    class Logger(logging.LoggerAdapter):
        # pylint: disable=missing-class-docstring
        def process(self, msg, kwargs):
            return f"[{self.extra['exp'].name}]: {msg}", kwargs

    @contextlib.contextmanager
    def session(self, *args, **kwds):
        """Function to generate a context session to interface the experiment.
        :param args: Same as database.session possitional arguments
        :param kwds: Same as database.session key arguments
        """
        with self.database.session(*args, **kwds) as db_session:
            self._logger.debug("Enter session with: %s %s", args, kwds)
            yield Session(experiment=self, database=db_session)
            self._logger.debug("Exit session with: %s %s", args, kwds)

    def close(self,  *args, **kwds):
        """Function to close the database interface driver.
        :param args: Same as database Driver close possitional arguments
        :param kwds: Same as database Driver close key arguments
        """
        self._logger.debug("Closing experiment with: %s %s", args, kwds)
        self.database.close(*args, **kwds)


class Session(BaseModel):
    """Base class for evolution experiment sessions.
    Provides the essential attributes to prepare the execution conditions.
    :param experiment: Experiment name the session is linked with
    :param fitness: Fitness instance to evaluate phenotypes
    :param algorithm: Algorithm instance to evolve phenotypes
    :param database: Database interface session,
    """
    experiment: Experiment
    fitness: gevopy.fitness.FitnessModel = None
    algorithm: gevopy.algorithms.Algorithm = DEFAULT_ALGORITHM
    database: gevopy.database.SessionContainer
    _logger: logging.Logger = PrivateAttr()
    _population: List[GenotypeModel] = PrivateAttr(default=[])

    class Config:
        # pylint: disable=missing-class-docstring
        arbitrary_types_allowed = True

    def __init__(self, experiment, **data):
        super().__init__(experiment=experiment, **data)
        self._logger = logging.getLogger(f"{__package__}.Experiment")
        self._logger = self.Logger(self._logger, {"exp": experiment})

    class Logger(logging.LoggerAdapter):
        # pylint: disable=missing-class-docstring
        def process(self, msg, kwargs):
            return f"[{self.extra['exp'].name}]: {msg}", kwargs

    @property
    def logger(self):
        """Session logger, used to trace and print experiment info.
        :return: Session.Logger
        """
        return self._logger

    def save_phenotypes(self, phenotypes):
        """Saves the phenotypes to the experiment database.
        :param phenotypes: List of phenotypes to add to the experiment
        """
        if any(not isinstance(x, GenotypeModel) for x in phenotypes):
            raise ValueError("Phenotypes must inherit from GenotypeModel")
        iserial_phenotypes = (p.dict(serialize=True) for p in phenotypes)
        self.database.add_phenotypes(iserial_phenotypes)  # Iter to speed up

    def add_phenotypes(self, phenotypes, save=True):
        """Adds phenotypes to the experiment session population.
        :param phenotypes: List of phenotypes to add to the experiment
        :param save: Flag to save new population status in database
        """
        for phenotype in phenotypes:  # Add experiment to phenotypes
            phenotype.experiment = self.experiment.name
        if save:
            self.save_phenotypes(phenotypes)
        self._population += phenotypes

    def get_phenotypes(self):
        """Gets population phenotypes from the experiment session.
        :return: Pool with experiment session phenotypes
        """
        return gevopy.tools.Pool(self._population)

    def del_experiment(self):
        """Deletes the experiment phenotypes and data. Also in database.
        """
        self.database.del_experiment(name=self.experiment.name)
        self._population = []

    def eval_phenotypes(self, fitness, save=True):
        """Executes the fitness evaluation on the session population.
        :param algorithm: Algorithm to run each execution generation cycle
        :param save: Flag to save new population status in database
        """
        if not isinstance(fitness, FitnessModel):
            raise ValueError("Expected 'FitnessModel' type for 'fitness'")
        fitness(self._population)
        if save:
            self.save_phenotypes(self._population)

    def generate_offspring(self, algorithm, save=True):
        """Replaces population with offspring generated from algorithm.
        :param algorithm: Algorithm to run for producing the offspring
        :param save: Flag to save new population status in database
        """
        if not isinstance(algorithm, gevopy.algorithms.Algorithm):
            raise ValueError("Expected 'Algorithm' type for 'algorithm'")
        self._population = algorithm(self._population)
        if save:
            self.save_phenotypes(self._population)

    def reset_score(self, save=True):
        """Resets the score of the current population of phenotypes.
        :param save: Flag to save new population status in database
        """
        for phenotype in self._population:
            phenotype.score = None
        if save:
            self.save_phenotypes(self._population)

    def run(self, max_generation=None, max_score=None):
        """Executes the algorithm until a stop condition is met.
        :param max_generation: The maximum number of loops to run
        :param max_score: The score required to stop the evolution
        :return: Generated Execution instance
        """
        if (max_generation is None) and (max_score is None):
            raise ValueError('Either max_generation or max_score is required')
        if max_generation and not isinstance(max_generation, int):
            raise TypeError('Expected positive int for max_generation')
        if max_generation and max_generation < 0:
            raise ValueError('Expected positive int for max_generation')
        if max_score and not isinstance(max_score, (float, int)):
            raise TypeError('Expected int or float for max_score')

        execution = Execution(experiment=self.experiment)
        logger = execution._logger

        try:
            logger.info("Start of evolutionary experiment execution")
            self.eval_phenotypes(self.fitness, save=True)  # Evaluate 1st pop
            execution.halloffame.update(self.get_phenotypes())
            while not execution.completed(max_generation, max_score):
                execution.generation += 1  # Increase generation index
                self.generate_offspring(self.algorithm, save=False)
                self.eval_phenotypes(self.fitness, save=True)
                execution.halloffame.update(self.get_phenotypes())
                logger.info("Completed cycle; %s", execution.best_score)
        except Exception as err:
            logger.error("Error %s raised during experiment execution", err)
            raise err
        else:
            logger.info("Experiment execution completed successfully")
            return execution


class Execution(BaseModel):
    """Base class for evolution algorithm execution. This class uses an
    experiment session to run evolution cycles and generations on a population
    of phenotypes. It also includes statistics about the execution process.

    Note that if neither max_generation or max_score are defined, the
    constructor raises ValueError for required valid end conditions.
    """
    halloffame: gevopy.tools.HallOfFame = gevopy.tools.HallOfFame(3)
    generation: int = 0
    _logger: logging.Logger = PrivateAttr()

    def __init__(self, experiment):
        super().__init__()
        logger_data = {"exp": experiment.name, "exe": self}
        self._logger = logging.getLogger(f"{__package__}.Experiment")
        self._logger = self.Logger(self._logger, logger_data)

    class Config:
        # pylint: disable=missing-class-docstring
        # pylint: disable=too-few-public-methods
        extra = Extra.forbid

    def __repr__(self) -> str:
        return (
            "Evolutionary algorithm execution report:\n"
            f"  Executed generations: {self.generation}\n"
            f"  Best phenotype: {self.halloffame[0].id}\n"
            f"  Best score: {self.best_score}\n"
        )

    @property
    def best_score(self):
        """Best score reached by the evaluated phenotypes during the run.
        :return: Float (not only positive)
        """
        try:  # If not started, halloffame is empty and raises IndexError
            return self.halloffame[0].score
        except IndexError:  # Empty if not started
            return None

    class Logger(logging.LoggerAdapter):
        # pylint: disable=missing-class-docstring
        def process(self, msg, kwargs):
            return f"[gen:{self.extra['exe'].generation}]: {msg}", kwargs

    def completed(self, max_generation, max_score):
        """Evaluates if the final generation or required score is reached.
        :param max_generation: The maximum number of loops to run
        :param max_score: The score required to stop the evolution
        :return: True if evolution conditions are met, False otherwise
        """
        if max_generation:
            if self.generation and max_generation <= self.generation:
                return True
        if max_score:
            if self.best_score and max_score <= self.best_score:
                return True
        return False  # If any of the defined
