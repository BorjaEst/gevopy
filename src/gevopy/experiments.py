"""The :mod:`experiments` module is intended to contain the classes
needed to execute the defined evolutionary algorithms.

The main class Experiment allows the user to create an object where
to group all the definitions in order to prepare them for execution.
It allows to create context session where genotypes can be added and
parameters can be modified.

Session method `run` triggers the execution of the evolution process
and returns an Execution object with all the relevant statistics and
parameters at the end of the evolution process.
"""

import contextlib
import logging
import uuid
from typing import List

from pydantic import BaseModel, Extra, Field, PrivateAttr, root_validator
from pydantic.types import PositiveInt

import gevopy.algorithms
import gevopy.database
import gevopy.fitness
import gevopy.tools
from gevopy.algorithms import Algorithm
from gevopy.database import EmptyInterface, SessionContainer
from gevopy.fitness import FitnessModel as Fitness
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


class Session():
    """Base class for evolution experiment sessions.
    Provides the essential attributes to prepare the execution conditions.
    :param experiment: Experiment name the session is linked with
    :param fitness: Fitness instance to evaluate genotypes
    :param algorithm: Algorithm instance to evolve genotypes
    :param database: Database interface session
    """

    def __init__(
        self,
        experiment: Experiment,
        database: SessionContainer,
        algorithm: Algorithm = DEFAULT_ALGORITHM,
        fitness: Fitness = None,
    ):
        self._logger = logging.getLogger(f"{__package__}.Experiment")
        self._logger = self.Logger(self._logger, {"exp": experiment})
        self.experiment = experiment
        self.database = database
        self.algorithm = algorithm
        self.fitness = fitness
        self.population = []

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

    def add_genotypes(self, genotypes, save=True):
        """Adds genotypes to the experiment session population.
        :param genotypes: List of genotypes to add to the experiment
        :param save: Flag to save new population status in database
        """
        for genotype in genotypes:  # Add experiment to genotypes
            genotype.experiment = self.experiment.name
        if save:
            save_genotypes(session=self)
        self.population += genotypes

    def get_genotypes(self):
        """Gets population genotypes from the experiment session.
        :return: List of genotypes stored in session
        """
        return self.population

    def del_experiment(self):
        """Deletes the experiment genotypes and data. Also in database.
        """
        self.database.del_experiment(name=self.experiment.name)
        self.population = []

    def run(self, end_conditions: dict,  hall_size: PositiveInt = 3):
        """Executes evolution algorithm inside the object session.
        Note that if neither of the conditions is defined, the constructor
        raises ValidationError for required valid end conditions.
        :param end_conditions: See 'EndConditions' arguments
        :param hall_size: Number of genotypes to store in the hall of fame
        """
        return execute_evolution(
            session=self,
            end_conditions=EndConditions(**end_conditions),
            halloffame=gevopy.tools.HallOfFame(maxsize=hall_size),
            pool=gevopy.tools.Pool(iterable=[]),
        )


class Execution(BaseModel, extra=Extra.forbid):
    """Base class for evolution algorithm execution. This class uses an
    experiment session to run evolution cycles and generations on a population
    of genotypes. It also includes statistics about the execution process.
    """
    halloffame: gevopy.tools.HallOfFame = gevopy.tools.HallOfFame(3)
    pool: gevopy.tools.Pool
    generation: int = 0

    class Logger(logging.LoggerAdapter):
        # pylint: disable=missing-class-docstring
        def process(self, msg, kwargs):
            return f"[gen:{self.extra['exe'].generation}]: {msg}", kwargs

    def __repr__(self) -> str:
        return (
            "Evolutionary algorithm execution report:\n"
            f"  Executed generations: {self.generation}\n"
            f"  Best genotype: {self.halloffame[0].item.id}\n"
            f"  Best score: {self.best_score}\n"
        )

    @property
    def best_score(self):
        """Best score reached by the evaluated genotypes during the run.
        :return: Float (not only positive)
        """
        try:  # If not started, halloffame is empty and raises IndexError
            return self.halloffame[0].score
        except IndexError:  # Empty if not started
            return None

    @property
    def worse_score(self):
        """Worst score stored in the evaluated hall of fame during the run.
        :return: Float (not only positive)
        """
        try:  # If not started, halloffame is empty and raises IndexError
            return self.halloffame[-1].score
        except IndexError:  # Empty if not started
            return None


class EndConditions(BaseModel, extra=Extra.forbid):
    """Class to validate and define the end conditions for an experiment
    session execution. 
    :param max_generation: The maximum number of loops to run
    :param min_generation: The minimum number of loops to run
    :param max_score: The best score required to stop the evolution
    :param min_score: The worst hall of fame required to stop
    """
    max_generation: PositiveInt = None
    min_generation: PositiveInt = None
    max_score: float = None
    min_score: float = None

    @root_validator(pre=True)
    def at_least_one_parameter(cls, values):
        if any(x in values for x in cls.schema()['properties'].keys()):
            return values
        raise ValueError("Undefined end condition")

    def completed(self, execution: Execution):
        """Evaluates if the final generation or required score is reached.
        :param execution: The session execution to evaluate
        :return: True if evolution conditions are met, False otherwise
        """
        if self.min_generation:
            if execution.generation < self.min_generation:
                return False  # Keep running even if score met
        if self.max_score:
            if execution.best_score >= self.max_score:
                return True  # Stop if max score reached
        if self.min_score:
            if execution.worse_score >= self.min_score:
                return True  # Stop if min score reached
        if self.max_generation:
            if execution.generation >= self.max_generation:
                return True  # Stop if max generation reached
        return False  # If any of the defined


def save_genotypes(session: Session):
    """Saves an iterator of genotypes into the session database.
    :param session: Experiment session where to execute evolution
    """
    iserial = (p.dict(serialize=True) for p in session.get_genotypes())
    session.database.add_genotypes(iserial)  # Iter to speed up


def eval_genotypes(session: Session, fitness: Fitness):
    """Executes the fitness evaluation on the session population.
    :param session: Experiment session where to execute evolution
    :param fitness: Fitness object to evaluate genotypes
    :return: Pool of scores and genotypes
    """
    if not isinstance(fitness, Fitness):
        raise ValueError("Expected 'FitnessModel' type for 'fitness'")
    return fitness(session.population)


def generate_offspring(execution: Execution, algorithm: Algorithm):
    """Replaces population with offspring generated from algorithm.
    :param execution: Execution object for the evolution function
    :param algorithm: Algorithm to run for producing the offspring
    :return: List of genotypes
    """
    if not isinstance(algorithm, gevopy.algorithms.Algorithm):
        raise ValueError("Expected 'Algorithm' type for 'algorithm'")
    return algorithm(execution.pool)


def execute_evolution(session: Session, end_conditions: EndConditions, **kwds):
    """Executes an evolution algorithm inside a session.    
    :param session: Experiment session where to execute evolution
    :param end_conditions: Conditions to stop evolution process
    :param kwds: Additional parameters from Execution data model
    """
    algorithm, fitness = session.algorithm, session.fitness
    execution = Execution(**kwds)
    logger = logging.getLogger(f"{__package__}.Experiment")
    logger = Execution.Logger(logger, {"session": session, "exe": execution})

    try:  # Try an except to return exection pointer to user
        logger.info("Start of evolutionary experiment execution")
        while True:
            execution.pool = eval_genotypes(session, fitness)
            execution.halloffame.update(execution.pool)
            execution.generation += 1  # Increase generation index
            save_genotypes(session)
            if end_conditions.completed(execution):
                logger.info("Experiment execution completed successfully")
                return execution  # End of evolution process
            else:
                logger.info("Completed cycle; %s", execution.best_score)
                session.population = generate_offspring(execution, algorithm)
    except KeyboardInterrupt:  # Interrupted by user
        logger.error("Experiment cancelled by the user 'CTRL+C'")
        return execution
    except Exception as error:  # Unexpected exception
        logger.error("Error %s raised during experiment execution", error)
        raise error
