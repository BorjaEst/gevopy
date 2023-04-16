"""Module to test mutation operations for evolution algorithms."""
# pylint: disable=redefined-outer-name

from inspect import ismethod, signature

from pytest import fixture, mark

from gevopy import genetics
from gevopy.tools import mutation


# Module fixtures ---------------------------------------------------
@fixture(scope="class")
def mutated(mutation, original):
    """Fixture to return a mutated genotype from base"""
    return mutation(original)


@fixture(scope="class")
def original(genotype):
    """Fixture to generate a base genotype to mutate"""
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

    def test_keeps_genotype(self, original, mutated):
        """Test mutation does not alter genotype"""
        assert isinstance(mutated, genetics.GenotypeModel)
        assert type(original) is type(mutated)

    def test_mutated_diff(self,  original, mutated):
        """Test mutation returns different object than genotype"""
        assert original is not mutated

    def test_all_ids_keep(self,  original, mutated):
        """Test mutation does not alter genotype id"""
        assert original.id == mutated.id


# Parametrization ---------------------------------------------------
class TestSinglePoint(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'SinglePoint' mutation"""

    @fixture(scope="class", params=[0.1, 0.2, 0.5])
    def mutation(self, request):
        """Parametrization to define the mutation method to use"""
        return mutation.SinglePoint(mutpb=request.param)

    @mark.parametrize("mutation", [0.0], indirect=True)
    def test_mutpb_000(self, original, mutated):
        """Tests that no mutation does not modity chromosome"""
        assert original.chromosome == mutated.chromosome

    @mark.parametrize("mutation", [1.0], indirect=True)
    def test_mutpb_100(self, original, mutated):
        """Tests that mutation does modity chromosome"""
        assert original.chromosome != mutated.chromosome
