"""Module to test mutation operations for evolution algorithms."""
# pylint: disable=redefined-outer-name

from inspect import ismethod, signature

from pytest import fixture, mark

from gevopy import genetics
from gevopy.tools import mutation


# Module fixtures ---------------------------------------------------
@fixture(scope="class")
def phenotype(mutation, original):
    """Fixture to return a mutated phenotype from base"""
    return mutation(original)


@fixture(scope="class")
def original(genotype):
    """Fixture to generate a base phenotype to mutate"""
    return genotype()


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Mutation instances attributes"""

    def test_is_callable(self, mutation):
        """Test mutation is a callable with arity 1"""
        assert callable(mutation)
        assert len(signature(mutation).parameters) == 1

    def test_attr_mutate_chromosome(self, mutation):
        """Test attribute mutate_chromosome is a method"""
        assert hasattr(mutation, "mutate_chromosome")
        assert ismethod(mutation.mutate_chromosome)


class ExecutionRequirements:
    """Tests group for Mutation execution features"""

    def test_keeps_genotype(self, original, phenotype):
        """Test mutation does not alter phenotype"""
        assert isinstance(phenotype, genetics.GenotypeModel)
        assert type(original) == type(phenotype)


# Parametrization ---------------------------------------------------
class TestSinglePoint(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'SinglePoint' mutation"""

    @fixture(scope="class")
    def mutation(self, mutpb):
        """Parametrization to define the mutation method to use"""
        return mutation.SinglePoint(mutpb=mutpb)

    @mark.parametrize("mutpb", [0.0], indirect=True)
    def test_mutpb_000(self, original, phenotype):
        """Tests that no mutation does not modity chromosome"""
        assert original.chromosome == phenotype.chromosome
        
    @mark.parametrize("mutpb", [1.0], indirect=True)
    def test_mutpb_100(self, original, phenotype):
        """Tests that mutation does modity chromosome"""
        assert original.chromosome != phenotype.chromosome
