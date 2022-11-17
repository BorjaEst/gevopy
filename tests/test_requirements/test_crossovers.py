"""Module to test crossover operations for evolution algorithms."""
# pylint: disable=redefined-outer-name

from inspect import ismethod, signature

from pytest import fixture, mark

from gevopy import genetics
from gevopy.tools import crossover


# Module fixtures ---------------------------------------------------
@fixture(scope="class")
def children(crossover, parents):
    """Fixture to return crossovered phenotypes from base"""
    return crossover(parents[0], parents[1])


@fixture(scope="class")
def parents(genotype):
    """Fixture to generate a base phenotypes to cross"""
    return genotype(), genotype()


@fixture(scope="class")
def generation(parents):
    """Fixture to calculate the parents generation"""
    return max([ph.generation for ph in parents])


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Crossover instances attributes"""

    def test_is_callable(self, crossover):
        """Test crossover is a callable with arity 2"""
        assert callable(crossover)
        assert len(signature(crossover).parameters) == 2

    def test_attr_cross_chromosomes(self, crossover):
        """Test attribute cross_chromosome is a method"""
        assert hasattr(crossover, "cross_chromosomes")
        assert ismethod(crossover.cross_chromosomes)


class ExecutionRequirements:
    """Tests group for Crossover execution features"""

    def test_keeps_genotype(self, parents, children):
        """Test crossover does not alter phenotype"""
        assert all(isinstance(x, genetics.GenotypeModel) for x in children)
        assert all(type(p) is type(x) for p, x in zip(parents, children))

    def test_id_change(self, parents, children):
        """Test ids on offsprings are different from parents"""
        assert children[0].id not in [p.id for p in parents]
        assert children[1].id not in [p.id for p in parents]

    def test_parents(self, parents, children):
        """Test children parents attr is correctly set"""
        assert set(children[0].parents) == set(ph.id for ph in parents)
        assert set(children[1].parents) == set(ph.id for ph in parents)

    def test_generation(self, generation, children):
        """Test children generation attr is correctly set"""
        assert children[0].generation == generation + 1
        assert children[1].generation == generation + 1


# Parametrization ---------------------------------------------------
class TestOnePoint(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'OnePoint' crossover"""

    @fixture(scope="class")
    def crossover(self):
        """Parametrization to define the crossover method to use"""
        return crossover.OnePoint()

    def test_chromosome(self, parents, children):
        """Test chromosomes are different from parents"""
        assert parents[0].chromosome != children[0].chromosome
        assert parents[1].chromosome != children[1].chromosome


class TestTwoPoint(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'TwoPoint' crossover"""

    @fixture(scope="class")
    def crossover(self):
        """Parametrization to define the crossover method to use"""
        return crossover.TwoPoint()

    def test_chromosome(self, parents, children):
        """Test chromosomes are different from parents"""
        assert parents[0].chromosome != children[0].chromosome
        assert parents[1].chromosome != children[1].chromosome


class TestMultiPoint(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'MultiPoint' crossover"""

    @fixture(scope="class", params=[1, 2, 5])
    def crossover(self, request):
        """Parametrization to define the crossover method to use"""
        return crossover.MultiPoint(n=request.param)

    def test_chromosome(self, parents, children):
        """Test chromosomes are different from parents"""
        assert parents[0].chromosome != children[0].chromosome
        assert parents[1].chromosome != children[1].chromosome


class TestUniform(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'Uniform' crossover"""

    @fixture(scope="class", params=[0.1, 0.2, 0.5])
    def crossover(self, request):
        """Parametrization to define the crossover method to use"""
        return crossover.Uniform(indpb=request.param)

    @mark.parametrize("crossover", [0.0], indirect=True)
    def test_indpb_000(self, parents, children):
        """Tests that no crossover does not modity chromosome"""
        assert parents[0].chromosome == children[0].chromosome
        assert parents[1].chromosome == children[1].chromosome

    @mark.parametrize("crossover", [1.0], indirect=True)
    def test_indpb_100(self, parents, children):
        """Tests that crossover does modity chromosome"""
        assert parents[0].chromosome != children[0].chromosome
        assert parents[1].chromosome != children[1].chromosome
