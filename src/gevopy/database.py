"""This modules interfaces the application with neo4j sotred data."""
import contextlib
import logging

import neo4j

# Database logger
module_logger = logging.getLogger(__name__)

# Database constants definitions
UNIT_TIMEOUT = 4


class GraphSession(contextlib.AbstractContextManager):
    """Neo4j database interface as evolution graph. It replacess all neo4j
    session methods by customised transactions ready to execute.

    Similar to the neo4j session, this class has context manager properties,
    therefore its methods must be executed inside a 'with' context.
    """

    def __init__(self, driver, *args, **kwds):
        self.logger = logging.getLogger(f"{__name__}.GraphSession")
        self.driver = driver
        self.args = args
        self.kwds = kwds
        self.__db = None

    def __enter__(self):
        self.logger.debug('Opening session: %s %s', self.args, self.kwds)
        self.__db = self.driver.session(*self.args, **self.kwds)
        return self

    def __exit__(self, *exc_details):
        self.logger.debug('Exiting session: %s', exc_details)
        self.__db.close()
        self.__db = None

    @property
    def db(self):
        """Returns the composed session from neo4j database stored inside.
        :return: An instance of neo4j.Session
        """
        if not self.__db:
            raise RuntimeError("Graph database session out of context")
        return self.__db

    def add_phenotypes(self, phenotypes):
        """Creates new phenotypes in the database and returns the ids.
        :param phenotypes: List of serialized phenotypes to store
        :return: List of ids from the created phenotypes
        """
        return self.db.execute_write(add_phenotypes, phenotypes)

    def get_phenotypes(self, ids):
        """Reads the database and returns the matching id phenotypes.
        :param ids: Ids from the phenotypes to collect
        :return: Serialized phenotypes matching the input ids
        """
        ids = [str(id) for id in ids]
        phenotypes = self.db.execute_read(get_phenotypes, ids)
        return [dict(x) for x in phenotypes]


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
    return [record["x"] for record in result]
