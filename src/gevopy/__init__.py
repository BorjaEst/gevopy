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

    def __init__(self, population, fitness, name=None, database=None):
        """Constructor base for a evolution experiments.
        :param population: List of phenotypes
        :param fitness: Fitness instance to evaluate phenotypes
        :param name: Experiment name, if none, generates an uuid4 string
        :param database: Neo4j database connection driver, defaults to None
        """
        self.__logg = logging.getLogger(f"{__name__}.Experiment")
        self.__name = name if name else str(uuid.uuid4())
        self.__logg = self.Logger(self.logger, {"name": self.name})
        self.__phenotypes = []
        self.fitness = fitness
        self.database = database
        self.add_phenotypes(population)

    class Logger(logging.LoggerAdapter):
        """Adds `Experiment.name` to the logs if available."""

        def process(self, msg, kwargs):
            return f"[{(self.extra['name'], msg)}] {kwargs}"

    @property
    def database(self):
        """Neo4j driver used to interface the database.
        :return: Neo4j.Driver instance or None
        """
        if isinstance(self.__db, Neo4jInterface):
            return self.__db.driver
        elif isinstance(self.__db, EmptyInterface):
            return None
        else:
            raise RuntimeError(f"Unexpected value:'{self.__db}' for database")

    @database.setter
    def database(self, value):
        if isinstance(value, neo4j.Driver):
            self.logger.info("Enabled neo4j graph database feature")
            self.__db = Neo4jInterface(value)
        elif value is None:
            self.logger.info("Disabled neo4j graph database feature")
            self.__db = Neo4jInterface(value)
        else:
            raise ValueError("Expected 'neo4j.Driver' for 'database'")

    @property
    def name(self):
        """Name generated or provided to the experiment.
        :return: string
        """
        return self.__name

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

    def add_phenotypes(self, phenotypes):
        """Adds phenotypes to the experiment and the database (if driver).
        :param phenotypes: List of phenotypes to add to the experiment
        """
        if not isinstance(phenotypes, list) or phenotypes == []:
            raise ValueError("Expected non empty 'list' for 'phenotypes'")
        if any(not isinstance(x, genetics.GenotypeModel) for x in phenotypes):
            raise ValueError("Phenotypes must inherit from GenotypeModel")

        self.logger.debug("Adding phenotypes:\n%s", phenotypes)
        for phenotype in phenotypes:  # Add experiment to phenotypes
            phenotype.experiment = self.name
        self.__db.add_phenotypes(phenotypes)
        self.__phenotypes += phenotypes

    def get_phenotypes(self, serialize=False):
        """Returns an iterable with all the intern experiment phenotypes.
        :param serialize: If phenotypes should be returned as serialized dict
        :return: Iterable of experiment phenotypes
        """
        if serialize:
            return (p.dict(serialize=True) for p in self.__phenotypes)
        return iter(self.__phenotypes)

    @contextlib.contextmanager
    def session(self, *args, **kwds):
        """Function to generate a context session to interface the experiment.
        :param args: Same as neo4j.Driver session possitional arguments
        :param kwds: Same as neo4j.Driver session key arguments
        """
        with GraphSession(self.database, *args, **kwds) as session:
            self.logger.debug("New session with:\n%s\n%s", args, kwds)
            yield session

    def run(self, algorithm=DEFAULT_ALGORITHM, **kwds):
        """Executes the algorithm until a stop condition is met.
        :param algorithm: Algorithm to run each execution generation cycle
        :param kwds: Same as gevopy.Execution key arguments
        :return: Generated Execution instance
        """
        self.logger.info("Run start for algorithm: %s", algorithm)
        return Execution(**kwds).run(self, algorithm)


class Execution():
    """Base class for evolution algorithm execution. This class uses an
    experiment session to run evolution cycles and generations on a population
    of phenotypes. It also includes statistics about the execution process.

    Note that if neither max_generation or max_score are defined, the
    constructor raises ValueError for required valid end conditions.
    """

    def __init__(self, max_generation=None, max_score=None):
        """Constructor base for a evolutionary algorithm execution.
        :param session: Experiment session used to run the exolution
        :param max_generation: The maximum number of loops to run
        :param max_score: The score required to stop the evolution
        """
        if not max_generation and not max_score:
            raise ValueError("Required valid end conditions for Execution")

        self.__logg = logging.getLogger(f"{__name__}.Execution")
        self.__halloffame = tools.HallOfFame(3)
        self.__generation = 0
        self.max_generation = max_generation
        self.max_score = max_score

    @property
    def logger(self):
        """Experiment logger, used to trace and print experiment info.
        :return: Experiment.Logger
        """
        return self.__logg

    @property
    def generation(self):
        """Number of generation the execution has run.
        :return: Integer higher or equal to 0
        """
        return self.__generation

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
    def best_score(self):
        """Best score reached by the evaluated phenotypes during the run.
        :return: Float (not only positive)
        """
        try:  # If not started, halloffame is empty and raises IndexError
            return self.__halloffame[0]
        except IndexError:  # Empty if not started
            return None

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

    class RunLogger(logging.LoggerAdapter):
        """Adds `Experiment.name` and `generation` to the logs."""

        def process(self, msg, kwargs):
            return f"[{(self.extra['exp'], self.extra['gen'], msg)}] {kwargs}"

    def run(self, experiment, algorithm):
        """Executes the algorithm until a stop condition is met.
        :param experiment: Experiment used for the evolution execution
        :param algorithm: Algorithm to run each execution generation cycle
        :return: Completed Execution instance (statistics)
        """
        if not isinstance(experiment, Experiment):
            raise ValueError("Expected 'Experiment' type for 'experiment'")

        logger_extra = dict(exp=experiment.name, gen=self.generation)
        run_logger = self.RunLogger(self.logger, logger_extra)

        try:
            resource = acquire_resource(*args, **kwds)

        finally:  # Code to release resource:
            if experiment.database:
                session = stack.enter_context(session)
            else:
                session = None

        with contextlib.ExitStack() as stack:
            if experiment.database:
                session = stack.enter_context(session)
            else:
                session = None
            try:
                run_logger.info("Start of evolutionary experiment execution")
                self.eval(session, experiment)
                experiment.eval_phenotypes()  # Evaluate offspring phenotypes
                if experiment.database:  # If db available save phenotypes
                    session.add_phenotypes(experiment.get_phenotypes())
                while offspring := self.cycle(session, experiment, algorithm):
                    run_logger.debug("Cycle offspring: %s", offspring)
                    run_logger.info(self.best_score)
                    if experiment.database:  # If db available save phenotypes
                        session.add_phenotypes(experiment.get_phenotypes())
            except Exception as error:
                run_logger.info("Error raised during experiment execution")
                raise error
            else:
                run_logger.info("Experiment execution completed successfully")
                return self

    def cycle(self, session, experiment, algorithm):
        """Spawns and evaluates genotype generations with the input algorithm.
        :param session: Experiment session opened during evolution runtime
        :param experiment: Evolutionary experiment with evolution properties
        :param algorithm: Evolutionary algorithm to apply on each generation
        :return: Offspring if experiment is not completed, None otherwise
        """
        self.__generation += 1  # Increase generation index for the execution
        experiment.generate_offspring(algorithm)  # Replace pop with offspring
        return self.eval(session, experiment)

    def eval(self, session, experiment):
        """Set up the execution process of the experiment evolution algorithm.
        :param session: Experiment session opened during evolution runtime
        :param experiment: Evolutionary experiment with evolution properties
        :return: Offspring if experiment is not completed, None otherwise
        """
        experiment.eval_phenotypes()  # Evaluate offspring phenotypes
        self.__halloffame.update(experiment.get_phenotypes(), self.generation)
        if experiment.database:
        session.add_phenotypes(experiment.get_phenotypes(serialize=True))

        return experiment.get_phenotypes() if not self.completed else None

    @property
    def completed(self):
        """Evaluates if the final generation or required score is reached.
        :return: True if evolution conditions are met, False otherwise
        """
        if self.max_generation and self.max_generation <= self.generation:
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
            f"\tExecuted generations:\t{self.generation}\n"
            f"\tBest phenotype:\t{self.__halloffame[0].id}"
            f"\tBest score:\t{self.best_score}\n"
        )
