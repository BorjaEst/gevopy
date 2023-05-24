"""Requirements module for crossover."""
# pylint: disable=redefined-outer-name
from inspect import signature
from gevopy import GenotypeModel


def test_are_callable(crossovers):
    """Test crossovers are callable with arity 2."""
    for genotype in crossovers:
        for crossover in crossovers[genotype]:
            assert callable(crossover)
            assert len(signature(crossover).parameters) == 2


def test_crossover_applied(genotypes, children):
    """Test that children are differnet from original."""
    genotypes_dict = {x.id: x for x in genotypes}
    for child in children:
        assert str(genotypes_dict[child.id]) != str(child)
