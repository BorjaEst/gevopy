"""This modules interfaces the application with neo4j sotred data."""
import abc
import contextlib
import functools
import logging

import neo4j

# Database logger
module_logger = logging.getLogger(__name__)


# Database interfaces -----------------------------------------------

class Interface(abc.ABC):
    """Abstract class for Database Interface Object."""

    @abc.abstractmethod
    def close(self,  *args, **kwds):
        """Function to close the database driver.
        :param args: Same as database Driver close possitional arguments
        :param kwds: Same as database Driver close key arguments
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def closed(cls, session):
        """Function to evaluate if session from interface is closed or open.
        :param session: Database Session to evaluate
        :return: True if closed, otherwise False
        """
        raise NotImplementedError

    @classmethod
    def __get_validators__(cls):
        yield cls.class_validator

    @classmethod
    def class_validator(cls, value):
        """Validates the value is a correct Interface type."""
        if not isinstance(value, cls):
            raise TypeError("'Interface' type required")
        return value

    # abc.abstractcontextmanagermethod
    def session(self, *args, **kwds):
        """Function to generate a context session to interface the experiment.
        :param args: Same as database Driver session possitional arguments
        :param kwds: Same as database Driver session key arguments
        :return: Database session container with interface methods
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def add_phenotypes(cls, container, phenotypes):
        """Creates new phenotypes in the database and returns the ids.
        :param container: Session container for database session
        :param phenotypes: List/iter of serialized phenotypes to store
        :return: List of ids from the created phenotypes
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_phenotypes(cls, container, ids):
        """Reads the database and returns the matching id phenotypes.
        :param container: Session container for database session
        :param ids: Ids from the phenotypes to collect
        :return: Serialized phenotypes matching the input ids
        """
        raise NotImplementedError


class Neo4jInterface(Interface):
    """Neo4j database interface as evolution graph. It replacess all neo4j
    session methods by customised transactions ready to execute.

    Similar to the neo4j session, this class has context manager properties,
    therefore its methods must be executed inside a 'with' context.
    """
    logger = logging.getLogger(f"{__name__}.Neo4jInterface")

    def __init__(self, *args, **kwds):
        """Function to generate the neo4j interface object.
        :param args: Same as neo4j.Driver open possitional arguments
        :param kwds: Same as neo4j.Driver open key arguments
        """
        self.logger.debug('Opening driver: %s %s', args, kwds)
        self.__driver = neo4j.GraphDatabase.driver(*args, **kwds)

    def close(self,  *args, **kwds):
        """Function to close the neo4j driver.
        :param args: Same as neo4j.Driver close possitional arguments
        :param kwds: Same as neo4j.Driver close key arguments
        """
        self.logger.debug('Closing driver: %s %s', args, kwds)
        self.__driver.close(*args, **kwds)

    @classmethod
    def closed(cls, session):
        """Function to evaluate if session from interface is closed or open.
        :param session: neo4j Session to evaluate
        :return: True if closed, otherwise False
        """
        return session.closed()

    @contextlib.contextmanager
    def session(self, *args, **kwds):
        """Function to generate a context session to interface the experiment.
        :param args: Same as neo4j.Driver session possitional arguments
        :param kwds: Same as neo4j.Driver session key arguments
        :return: Database session container with interface methods
        """
        self.logger.debug('Session call: %s %s', args, kwds)
        with self.__driver.session(*args, **kwds) as db_session:
            self.logger.debug("Open neo4j database session: %s", db_session)
            yield SessionContainer(db_session, interface=self)
            self.logger.debug("Exit neo4j database session: %s", db_session)

    @classmethod
    def add_phenotypes(cls, container, phenotypes):
        """Creates new phenotypes in the database and returns the ids.
        :param container: Session container for neo4j session
        :param phenotypes: List/iter of serialized phenotypes to store
        :return: List of ids from the created phenotypes
        """
        phenotypes = list(phenotypes)
        cls.logger.debug('Adding phenotypes %s', phenotypes)
        return container.session.execute_write(add_phenotypes, phenotypes)

    @classmethod
    def get_phenotypes(cls, container, ids):
        """Reads the database and returns the matching id phenotypes.
        :param container: Session container for neo4j session
        :param ids: Ids from the phenotypes to collect
        :return: Serialized phenotypes matching the input ids
        """
        ids = list(str(id) for id in ids)
        cls.logger.debug('Getting phenotypes %s', ids)
        return container.session.execute_read(get_phenotypes, ids)


class EmptyInterface(Interface):
    """Neo4j database interface as evolution graph. It replacess all neo4j
    session methods by customised transactions ready to execute.

    Similar to the neo4j session, this class has context manager properties,
    therefore its methods must be executed inside a 'with' context.
    """
    logger = logging.getLogger(f"{__name__}.EmptyInterface")

    def __init__(self):
        """Function to generate the empty mock interface object.
        """
        self.logger.debug('Opening empty interface driver')

    def close(self,  *args, **kwds):
        """Function to close the empty mock interface object.
        """
        self.logger.debug('Closing empty interface driver')

    @classmethod
    def closed(cls, session):
        """Function to evaluate if session from interface is closed or open.
        :param session: Mock session to evaluate
        :return: True if closed, otherwise False
        """
        return ~session['open']

    @contextlib.contextmanager
    def session(self, *args, **kwds):
        """Function to generate a context session to interface the experiment.
        :param args: Ignored 
        :param kwds: Ignored
        :return: Database session container with interface methods
        """
        self.logger.debug('Session call: %s %s', args, kwds)
        db_session = dict(open=True)
        self.logger.debug("Open mock database session: %s", db_session)
        yield SessionContainer(db_session, interface=self)
        db_session['open'] = False
        self.logger.debug("Exit mock database session: %s", db_session)

    @classmethod
    def add_phenotypes(cls, _container, phenotypes):
        """Creates new phenotypes in the database and returns the ids.
        :param container: Session container (Not used)
        :param phenotypes: List/iter of serialized phenotypes to store
        :return: List of ids from the created phenotypes
        """
        phenotypes = list(phenotypes)
        cls.logger.debug('Adding phenotypes %s', phenotypes)
        return list(str(p.id) for p in phenotypes)

    @classmethod
    def get_phenotypes(cls, _container, ids):
        """Reads the database and returns the matching id phenotypes.
        :param container: Session container (Not used)
        :param ids: Ids from the phenotypes to collect
        :return: Serialized phenotypes matching the input ids
        """
        ids = list(str(id) for id in ids)
        cls.logger.debug('Getting phenotypes %s', ids)
        return []


# Session Containers ------------------------------------------------

class AbstractSession(abc.ABC):
    """Abstract class for Database Interface Session Object."""

    def __init__(self, session, interface):
        """Generic constructor for Database Session Container Objects.
        :param session: Real session from the database
        :param interface: Database interface with evolution methods
        """
        self.interface = interface
        self.session = session

    @classmethod
    def require_session(cls, meth):
        """Decorator to ensure the method/function is called in context."""
        @functools.wraps(meth)
        def wrapped_method(self, *args, **kwds):
            if not self.in_session:
                raise RuntimeError(f"{meth} out of {self.__class__} context")
            return meth(self, *args, **kwds)
        return wrapped_method

    @property
    @abc.abstractmethod
    def in_session(self):
        """Returns if the execution pointer is inside the instance context.
        :return: True if the call is inside instance context
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_phenotypes(self, phenotypes):
        """Creates new phenotypes in the database and returns the ids.
        :param phenotypes: List/iter of serialized phenotypes to store
        :return: List of ids from the created phenotypes
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_phenotypes(self, ids):
        """Reads the database and returns the matching id phenotypes.
        :param ids: Ids from the phenotypes to collect
        :return: Serialized phenotypes matching the input ids
        """
        raise NotImplementedError


class SessionContainer(AbstractSession):
    """Generic Database Session Container for Database Interface"""

    @property
    def in_session(self):
        """Returns if the execution pointer is inside the instance context.
        :return: True if the call is inside instance context
        """
        return ~self.interface.closed(self.session)

    @AbstractSession.require_session
    def add_phenotypes(self, phenotypes):
        """Creates new phenotypes in the database and returns the ids.
        :param phenotypes: List/iter of serialized phenotypes to store
        :return: List of ids from the created phenotypes
        """
        return self.interface.add_phenotypes(self, phenotypes)

    @AbstractSession.require_session
    def get_phenotypes(self, ids):
        """Reads the database and returns the matching id phenotypes.
        :param ids: Ids from the phenotypes to collect
        :return: Serialized phenotypes matching the input ids
        """
        return self.interface.get_phenotypes(self, ids)


# NEO4J Transactions ------------------------------------------------

# Transactions constants definitions
UNIT_TIMEOUT = 4


@neo4j.unit_of_work(timeout=UNIT_TIMEOUT)
def add_phenotypes(tx, phenotypes):
    """Transaction function to create new phenotypes in the database.
    :param tx: Neo4j transaction object
    :param phenotypes: List of serialized phenotype to store
    :return: List of ids from the created phenotypes
    """
    query = (
        "UNWIND $phenotypes AS phenotype "
        "MERGE (x:Phenotype { id: phenotype.id }) "
        "SET x = phenotype, x.parents = null, x.experiment = null "
        "WITH phenotype, x as child "
        "CALL { "
        "  WITH child, phenotype "
        "  UNWIND phenotype.parents as parent_id "
        "  MATCH (parent:Phenotype { id: parent_id }) "
        "  MERGE (parent)-[:HAS_CHILD]->(child) "
        "} "
        "WITH child as x, phenotype.experiment as experiment "
        "WHERE NOT experiment IS NULL "
        "CALL { "
        "  WITH x, experiment "
        "  MERGE (e:Experiment { name: experiment }) "
        "  MERGE (x)-[:IN_EXPERIMENT]->(e) "
        "} "
    )
    _result = tx.run(query, phenotypes=phenotypes)
    return [p['id'] for p in phenotypes]


@neo4j.unit_of_work(timeout=UNIT_TIMEOUT)
def get_phenotypes(tx, ids):
    """Transaction to returns the matching id phenotypes.
    :param tx: Neo4j transaction object
    :param ids: Ids from the phenotypes to collect
    :return: Serialized phenotypes matching the input ids
    """
    query = (
        "MATCH (x:Phenotype) WHERE x.id IN $phenotypes_ids "
        "OPTIONAL MATCH (x)-[:IN_EXPERIMENT]->(e:Experiment) "
        "OPTIONAL MATCH (y)-[:HAS_CHILD]->(x) "
        "WITH x, e, collect(y.id) as p "
        "RETURN x{.*, .score, experiment:e.name, parents:p } "
    )
    result = tx.run(query, phenotypes_ids=ids)
    return [dict(record["x"]) for record in result]
