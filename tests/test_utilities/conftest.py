"""Module to test crossover utilities for evolution algorithms."""
# pylint: disable=redefined-outer-name
import pytest

from gevopy import utils


@pytest.fixture(scope="function", autouse=True)
def apply_crossover(chromosome_1, chromosome_2, points):
    """Crosses chromosomes on the indicated list of points"""
    utils.crosslist(chromosome_1, chromosome_2, points)
