"""Evolution algorithms with python."""

import contextlib
import logging

from gevopy.database import GraphSession

# Application logger
module_logger = logging.getLogger(__name__)


class Experiment():
    def __init__(self, driver=None):
        self.driver = driver

    @contextlib.contextmanager
    def session(self, *args, **kwds):
        with GraphSession(self.driver, *args, **kwds) as session:
            yield session

    def run(self):
        with self.session() as session:
            return Execution(session=session).run()


class Execution():
    def __init__(self, session):
        self.db = session

    def run(self):
        self.db.add_phenotypes([])
        self.db.get_phenotypes([])

