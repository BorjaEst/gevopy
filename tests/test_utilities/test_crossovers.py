"""Module to test crossover utilities for evolution algorithms."""
# pylint: disable=redefined-outer-name

import numpy as np
from pytest import fixture, mark

from gevopy import utils


@fixture(scope="function", autouse=True)
def apply_crossover(chromosome_1, chromosome_2, points):
    """Crosses chromosomes on the indicated list of points"""
    utils.cross_chromosomes(chromosome_1, chromosome_2, points)


@mark.parametrize("chromosome_1", [np.array([11, 12, 13, 14])])
@mark.parametrize("chromosome_2", [np.array([21, 22, 23, 24])])
@mark.parametrize("points", [[0, 0, 0]])
def test_000_cross_chromosomes(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 000"""
    assert all(chromosome_1 == [21, 22, 23, 24])
    assert all(chromosome_2 == [11, 12, 13, 14])


@mark.parametrize("chromosome_1", [np.array([11, 12, 13, 14])])
@mark.parametrize("chromosome_2", [np.array([21, 22, 23, 24])])
@mark.parametrize("points", [[0, 0, 1]])
def test_001_cross_chromosomes(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 001"""
    assert all(chromosome_1 == [11, 22, 23, 24])
    assert all(chromosome_2 == [21, 12, 13, 14])


@mark.parametrize("chromosome_1", [np.array([11, 12, 13, 14])])
@mark.parametrize("chromosome_2", [np.array([21, 22, 23, 24])])
@mark.parametrize("points", [[0, 0, 4]])
def test_004_cross_chromosomes(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 004"""
    assert all(chromosome_1 == [11, 12, 13, 14])
    assert all(chromosome_2 == [21, 22, 23, 24])


@mark.parametrize("chromosome_1", [np.array([11, 12, 13, 14])])
@mark.parametrize("chromosome_2", [np.array([21, 22, 23, 24])])
@mark.parametrize("points", [[0, 1, 2]])
def test_012_cross_chromosomes(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positiosn 012"""
    assert all(chromosome_1 == [21, 12, 23, 24])
    assert all(chromosome_2 == [11, 22, 13, 14])


@mark.parametrize("chromosome_1", [np.array([11, 12, 13, 14])])
@mark.parametrize("chromosome_2", [np.array([21, 22, 23, 24])])
@mark.parametrize("points", [[1, 2, 3]])
def test_123_cross_chromosomes(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 123"""
    assert all(chromosome_1 == [11, 22, 13, 24])
    assert all(chromosome_2 == [21, 12, 23, 14])
