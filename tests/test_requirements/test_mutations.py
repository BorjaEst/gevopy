"""Requirements module for mutations."""
# pylint: disable=redefined-outer-name
from inspect import signature


def test_are_callable(mutations):
    """Test mutations are callable with arity 1"""
    for genotype in mutations:
        for mutation in mutations[genotype]:
            assert callable(mutation)
            assert len(signature(mutation).parameters) == 1


def test_return_none(mutated):
    """Test corsovers return none value."""
    for value in mutated:
        assert value is None
