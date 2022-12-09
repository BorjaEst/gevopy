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
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, PrivateAttr, root_validator

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
    :param fitness: Fitness instance to evaluate phenotypes
    :param algorithm: Algorithm instance to evolve phenotypes
    :param name: Experiment name, if none, generates an uuid4 string
    :param database: Database interface object, defaults to EmptyInterface
    """
    fitness: gevopy.fitness.FitnessModel
    algorithm: gevopy.algorithms.Algorithm = DEFAULT_ALGORITHM
    database: gevopy.database.Interface = EmptyInterface()
    name: str = Field(default_factory=lambda: str(uuid.uuid4()))
    _logger: logging.Logger = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._logger = logging.getLogger(f"{__name__}.Experiment")
        self._logger = self.Logger(self.logger, {"exp": self})

    class Logger(logging.LoggerAdapter):
        # pylint: disable=missing-class-docstring
        def process(self, msg, kwargs):
            return f"[{self.extra['exp'].name}]: {msg}", kwargs

    @property
    def logger(self):
        """Experiment logger, used to trace and print experiment info.
        :return: Experiment.Logger
        """
        return self._logger

    @contextlib.contextmanager
    def session(self, *args, **kwds):
        """Function to generate a context session to interface the experiment.
        :param args: Same as database.session possitional arguments
        :param kwds: Same as database.session key arguments
        """
        with self.database.session(*args, **kwds) as db_session:
            self.logger.debug("Enter session with: %s %s", args, kwds)
            yield Session(experiment=self, database=db_session)
            self.logger.debug("Exit session with: %s %s", args, kwds)


class Session(BaseModel):
    """Base class for evolution experiment sessions.
    Provides the essential attributes to prepare the execution conditions.
    :param experiment: Experiment name the session is linked with
    :param database: Database interface session,
    """

    experiment: Experiment
    database: gevopy.database.SessionContainer
    _population: List[GenotypeModel] = PrivateAttr(default=[])

    class Config:
        # pylint: disable=missing-class-docstring
        arbitrary_types_allowed = True

    def save_phenotypes(self, phenotypes):
        """Saves the phenotypes to the experiment database.
        :param phenotypes: List of phenotypes to add to the experiment
        """
        if any(not isinstance(x, GenotypeModel) for x in phenotypes):
            raise ValueError("Phenotypes must inherit from GenotypeModel")
        iserial_phenotypes = (p.dict(serialize=True) for p in phenotypes)
        self.database.add_phenotypes(iserial_phenotypes)  # Iter to speed up

    def run(self, **execution_kwds):
        """Executes the algorithm until a stop condition is met.
        :param max_generation: The maximum number of loops to run
        :param max_score: The score required to stop the evolution
        :return: Generated Execution instance
        """
        return Execution(**execution_kwds).run(session=self)

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
        :param phenotypes: List of phenotypes to add to the experiment
        :param save: Flag to save new population status in database
        """
        return self._population

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


class Execution(BaseModel):
    """Base class for evolution algorithm execution. This class uses an
    experiment session to run evolution cycles and generations on a population
    of phenotypes. It also includes statistics about the execution process.

    Note that if neither max_generation or max_score are defined, the
    constructor raises ValueError for required valid end conditions.
    """
    max_generation: Optional[PositiveInt] = None
    max_score: Optional[float]
    halloffame: gevopy.tools.HallOfFame = gevopy.tools.HallOfFame(3)
    generation: int = 0

    @root_validator()
    def check_max_gen_or_score(cls, values):
        """Checks for valid end conditions in the Execution"""
        # pylint: disable=no-self-argument
        max_generation = values.get('max_generation')
        max_score = values.get("max_score")
        if (max_generation is None) and (max_score is None):
            raise ValueError('Either max_generation or max_score is required')
        return values

    @property
    def best_score(self):
        """Best score reached by the evaluated phenotypes during the run.
        :return: Float (not only positive)
        """
        try:  # If not started, halloffame is empty and raises IndexError
            return self.halloffame[0].score
        except IndexError:  # Empty if not started
            return None

    class RunLogger(logging.LoggerAdapter):
        # pylint: disable=missing-class-docstring
        def process(self, msg, kwargs):
            return f"[gen:{self.extra['exe'].generation}]: {msg}", kwargs

    def run(self, session):
        """Executes the algorithm until a stop condition is met.
        :param session: Experiment session used for the evolution execution
        :return: Completed Execution instance (statistics)
        """
        logger = self.RunLogger(session.experiment.logger, dict(exe=self))
        algorithm = session.experiment.algorithm
        fitness = session.experiment.fitness
        try:
            logger.info("Start of evolutionary experiment execution")
            session.eval_phenotypes(fitness, save=True)  # Evaluate first pop
            while not self.completed:
                logger.info("New execution cycle; %s", self.best_score)
                self.generation += 1  # Increase generation index
                session.generate_offspring(algorithm, save=False)
                session.eval_phenotypes(fitness, save=True)
                population = session.get_phenotypes()
                self.halloffame.update(population, self.generation)
        except Exception as err:
            logger.error("Error %s raised during experiment execution", err)
            raise err
        else:
            logger.info("Experiment execution completed successfully")
            return self

    @property
    def completed(self):
        """Evaluates if the final generation or required score is reached.
        :return: True if evolution conditions are met, False otherwise
        """
        if self.max_generation:
            if self.generation and self.max_generation <= self.generation:
                return True
        if self.max_score:
            if self.best_score and self.max_score <= self.best_score:
                return True
        return False  # If any of the defined

    def __repr__(self) -> str:
        """Representation for Execution class. Prints execution statistics.
        :return: Statistical representation for the evolutionary execution
        """
        return (
            "Evolutionary algorithm execution report:\n"
            f"  Executed generations: {self.generation}\n"
            f"  Best phenotype: {self.halloffame[0].id}\n"
            f"  Best score: {self.best_score}\n"
        )
