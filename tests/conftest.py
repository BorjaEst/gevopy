"""Module for evolution generic fixtures"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
import importlib
import pathlib

import pytest


examples = [ex.stem for ex in pathlib.Path('./examples').glob("*.py")]


@pytest.fixture(scope="session", params=examples)
def app(request):
    """Return the application from each example in the repository.
    (if) Set the application example to work on testing mode.
    """
    app = importlib.import_module(f"examples.{request.param}").app
    # app.config.update(TESTING=True)
    return app


@pytest.fixture(scope="session")
def genotypes(app):
    """
    """
    return [genotype_class() for genotype_class in app.genotypes]
