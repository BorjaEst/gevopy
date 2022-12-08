"""Evolution algorithms with python.
The :mod:`__init__` module is intended to initialise the package and contain
the master classes to carry on the evolution. From this module, the user
can call for the `Experiment` in order to generate an instance with the
required methods and data to evolve some initial population to a desired
state.
"""

import contextlib
import logging
import uuid

import neo4j

from gevopy import algorithms, genetics, tools
from gevopy.database import Neo4jInterface, EmptyInterface
from gevopy.fitness import FitnessModel
from gevopy.tools import crossover, mutation, selection

# https://docs.python.org/3/howto/logging-cookbook.html
module_logger = logging.getLogger(__name__)

# Default algorithm for base experiment
DEFAULT_ALGORITHM = algorithms.Standard(
    selection1=selection.Ponderated(),
    selection2=selection.Uniform(),
    crossover=crossover.OnePoint(),
    mutation=mutation.SinglePoint(mutpb=0.1),
    survival_rate=0.2,
)


class Experiment():
    """Base class for evolution experiments.
    Provides the essential attributes to create and run an experiment.
    """

    class Logger(logging.LoggerAdapter):
        """Adds `Experiment.name` to the logs if available."""

        def process(self, msg, kwargs):
            return f"[{(self.extra['name'], msg)}] {kwargs}"

    def __init__(self, fitness, name=None, database=EmptyInterface()):
        """Constructor base for a evolution experiments.
        :param fitness: Fitness instance to evaluate phenotypes
        :param name: Experiment name, if none, generates an uuid4 string
        :param database: Database interface object, defaults to EmptyInterface 
        """
        self.name = name if name else str(uuid.uuid4())
        self.fitness = fitness
        self.database = database

    @property
    def name(self):
        """Name generated or provided to the experiment.
        :return: string
        """
        return self.__name

    @name.setter
    def name(self, value):
        self.__logg = logging.getLogger(f"{__name__}.Experiment")
        self.__logg = self.Logger(self.logger, {"name": value})
        self.__name = f"{value}"

    @property
    def database(self):
        """Database interface used to write and read from database.
        :return: gevopy.database object instance or None
        """
        return self.__db

    @database.setter
    def database(self, value):
        if not isinstance(value, (Neo4jInterface, EmptyInterface)):
            raise ValueError("Expected 'gevopy.database' interface")
        self.__db = value

    @property
    def logger(self):
        """Experiment logger, used to trace and print experiment info.
        :return: Experiment.Logger
        """
        return self.__logg

    @property
    def fitness(self):
        """Fitness function used to evaluate all phenotypes.
        :return: Evolution algorithm `Fitness` instance
        """
        return self.__fitness

    @fitness.setter
    def fitness(self, value):
        if not isinstance(value, FitnessModel):
            raise ValueError("Expected 'gevopy.FitnessModel' instance")
        self.__fitness = value

    @contextlib.contextmanager
    def session(self, *args, **kwds):
        """Function to generate a context session to interface the experiment.
        :param args: Same as neo4j.Driver session possitional arguments
        :param kwds: Same as neo4j.Driver session key arguments
        """
        with self.__db.session(*args, **kwds) as db_session:
            self.logger.debug("New session with:\n%s\n%s", args, kwds)
            yield Session(experiment=self, database=db_session)


class Session():
    """Base class for evolution experiment sessions.
    Provides the essential attributes to prepare the execution conditions.
    """

    def __init__(self, experiment, database):
        self.__experiment = experiment
        self.__population = []
        self.__db = database

    @property
    def population(self):
        """Returns the list of current phenotypes at the session.
        :return: List of experiment phenotypes
        """
        return self.__population

    @property
    def logger(self):
        """Session logger, borrowed from the contained experiment.
        :return: Generated Execution instance
        """
        return self.__experiment.logger

    def save_phenotypes(self, phenotypes):
        """Saves the phenotypes to the experiment database.
        :param phenotypes: List of phenotypes to add to the experiment
        """
        if any(not isinstance(x, genetics.GenotypeModel) for x in phenotypes):
            raise ValueError("Phenotypes must inherit from GenotypeModel")
        iserial_phenotypes = (p.dict(serialize=True) for p in phenotypes)
        self.__db.add_phenotypes(iserial_phenotypes)  # Iterator to speed up

    def run(self, **execution_kwds):
        """Executes the algorithm until a stop condition is met.
        :param max_generation: The maximum number of loops to run
        :param max_score: The score required to stop the evolution
        :return: Generated Execution instance
        """
        self.logger.info("Run start for experiment session")
        return Execution(**execution_kwds).run(session=self)

    def add_phenotypes(self, phenotypes, save=True):
        """Adds phenotypes to the experiment and the database.
        :param phenotypes: List of phenotypes to add to the experiment
        :param save: Flag to save new population status in database
        """
        if not isinstance(phenotypes, list) or phenotypes == []:
            raise ValueError("Expected non empty 'list' for 'phenotypes'")
        if any(not isinstance(x, genetics.GenotypeModel) for x in phenotypes):
            raise ValueError("Phenotypes must inherit from GenotypeModel")
        for phenotype in phenotypes:  # Add experiment to phenotypes
            phenotype.experiment = self.__experiment.name
        if save:
            self.save_phenotypes(phenotypes)
        self.__population += phenotypes

    def eval_phenotypes(self, fitness, save=True):
        """Executes the fitness evaluation on the session population.
        :param algorithm: Algorithm to run each execution generation cycle
        :param save: Flag to save new population status in database
        """
        if not isinstance(fitness, FitnessModel):
            raise ValueError("Expected 'FitnessModel' type for 'fitness'")
        fitness(self.__population)
        if save:
            self.save_phenotypes(self.__population)

    def generate_offspring(self, algorithm, save=True):
        """Replaces population with offspring generated from algorithm.
        :param algorithm: Algorithm to run for producing the offspring
        :param save: Flag to save new population status in database
        """
        if not isinstance(algorithm, algorithms.Algorithm):
            raise ValueError("Expected 'Algorithm' type for 'algorithm'")
        self.__population = algorithm(self.__population)
        if save:
            self.save_phenotypes(self.__population)


class Execution():
    """Base class for evolution algorithm execution. This class uses an
    experiment session to run evolution cycles and generations on a population
    of phenotypes. It also includes statistics about the execution process.

    Note that if neither max_generation or max_score are defined, the
    constructor raises ValueError for required valid end conditions.
    """

    def __init__(self, max_generation=None, max_score=None):
        """Constructor base for a evolutionary algorithm execution.
        :param max_generation: The maximum number of loops to run
        :param max_score: The score required to stop the evolution
        """
        if not max_generation and not max_score:
            raise ValueError("Required valid end conditions for Execution")
        self._halloffame = tools.HallOfFame(3)
        self._generation = 0
        self.max_generation = max_generation
        self.max_score = max_score

    @property
    def max_generation(self):
        """Configured maximum of generations to run before the stop.
        :return: Integer higher than 0
        """
        return self.__max_generation

    @max_generation.setter
    def max_generation(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected 'int' type or None as max generation")
        if value <= 0:
            raise ValueError("Expected value higher than 0 for int")
        self.__max_generation = value

    @property
    def max_score(self):
        """Configured maximum score to reach by phenotypes before the stop.
        :return: Float (not only positive)
        """
        return self.__max_score

    @max_score.setter
    def max_score(self, value):
        if not isinstance(value, (int, float)) or value is not None:
            raise ValueError("Expected 'float', 'int' or None for max score")
        self.__max_score = value

    @property
    def best_score(self):
        """Best score reached by the evaluated phenotypes during the run.
        :return: Float (not only positive)
        """
        try:  # If not started, halloffame is empty and raises IndexError
            return self._halloffame[0]
        except IndexError:  # Empty if not started
            return None

    class RunLogger(logging.LoggerAdapter):
        """Adds `Experiment.name` and `generation` to the logs."""

        def process(self, msg, kwargs):
            return f"[{(self.extra['exp'], self.extra['gen'], msg)}] {kwargs}"

    def run(self, session):
        """Executes the algorithm until a stop condition is met.
        :param session: Experiment session used for the evolution execution
        :return: Completed Execution instance (statistics)
        """
        if not isinstance(session, Session):
            raise ValueError("Expected 'Session' type for 'session'")
        logger = self.RunLogger(session.logger, dict(gen=self._generation))
        fitness, algorithm = session.fitness, session.algorithm
        try:
            logger.info("Start of evolutionary experiment execution")
            session.eval_phenotypes(fitness, save=True)  # Evaluate first pop
            while not self.completed:
                logger.info("New execution cycle; %s", self.best_score)
                self._generation += 1  # Increase generation index
                session.generate_offspring(algorithm, save=False)
                session.eval_phenotypes(fitness, save=True)
                self._halloffame.update(session.population, self._generation)
        except Exception as error:
            logger.info("Error raised during experiment execution")
            raise error
        else:
            logger.info("Experiment execution completed successfully")
            return self

    @property
    def completed(self):
        """Evaluates if the final generation or required score is reached.
        :return: True if evolution conditions are met, False otherwise
        """
        if self.max_generation and self.max_generation <= self._generation:
            return True
        if self.max_score and self.max_score <= self.best_score:
            return True
        return False

    def __repr__(self) -> str:
        """Representation for Execution class. Prints execution statistics.
        :return: Statistical representation for the evolutionary execution
        """
        return (
            "- Evolutionary algorithm execution report -----\n"
            f"\tExecuted generations:\t{self._generation}\n"
            f"\tBest phenotype:\t{self._halloffame[0].id}"
            f"\tBest score:\t{self.best_score}\n"
        )
