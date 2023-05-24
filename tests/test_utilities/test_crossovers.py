"""Module to test crossover utilities for evolution algorithms."""
# pylint: disable=redefined-outer-name
from pytest import mark


@mark.parametrize("chromosome_1", [[11, 12, 13, 14]])
@mark.parametrize("chromosome_2", [[21, 22, 23, 24]])
@mark.parametrize("points", [[0, 0, 0]])
def test_cross_at_000(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 000"""
    assert chromosome_1 == [21, 22, 23, 24]
    assert chromosome_2 == [11, 12, 13, 14]


@mark.parametrize("chromosome_1", [[11, 12, 13, 14]])
@mark.parametrize("chromosome_2", [[21, 22, 23, 24]])
@mark.parametrize("points", [[0, 0, 1]])
def test_cross_at_001(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 001"""
    assert chromosome_1 == [11, 22, 23, 24]
    assert chromosome_2 == [21, 12, 13, 14]


@mark.parametrize("chromosome_1", [[11, 12, 13, 14]])
@mark.parametrize("chromosome_2", [[21, 22, 23, 24]])
@mark.parametrize("points", [[0, 0, 4]])
def test_cross_at_004(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 004"""
    assert chromosome_1 == [11, 12, 13, 14]
    assert chromosome_2 == [21, 22, 23, 24]


@mark.parametrize("chromosome_1", [[11, 12, 13, 14]])
@mark.parametrize("chromosome_2", [[21, 22, 23, 24]])
@mark.parametrize("points", [[0, 1, 2]])
def test_cross_at_012(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positiosn 012"""
    assert chromosome_1 == [21, 12, 23, 24]
    assert chromosome_2 == [11, 22, 13, 14]


@mark.parametrize("chromosome_1", [[11, 12, 13, 14]])
@mark.parametrize("chromosome_2", [[21, 22, 23, 24]])
@mark.parametrize("points", [[1, 2, 3]])
def test_cross_at_123(chromosome_1, chromosome_2):
    """Tests arrays are crossed at positions 123"""
    assert chromosome_1 == [11, 22, 13, 24]
    assert chromosome_2 == [21, 12, 23, 14]
