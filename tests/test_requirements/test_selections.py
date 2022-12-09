"""Module to test selection operations for evolution algorithms."""
# pylint: disable=redefined-outer-name

from inspect import signature

from pytest import fixture, mark

from gevopy.tools import Pool, selection


# Module fixtures ---------------------------------------------------
@fixture(scope="class", autouse=True)
def score_phenotypes(population):
    """Fixture to add a score to a population of phenotypes"""
    for index, phenotype in enumerate(population):
        phenotype.score = index


@fixture(scope="class")
def pool(population):
    """Fixture to return a pool of phenotypes"""
    return Pool(population)


@fixture(scope="class", params=[0, 1, 5, 20])
def selection_size(request):
    """Parametrization for the number of phenotypes to select"""
    return request.param


@fixture(scope="class")
def selected(selection, pool, selection_size):
    """Fixture to return a selection of phenotypes"""
    return selection(pool, selection_size)


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Selection instances attributes"""

    def test_is_callable(self, selection):
        """Test selection is a callable with arity 2"""
        assert callable(selection)
        assert len(signature(selection).parameters) == 2


class ExecutionRequirements:
    """Tests group for Selection execution features"""

    def test_returned_size(self, selected, selection_size):
        """Test returned list length matches the selection size"""
        assert len(selected) == selection_size

    def test_selected_from_pool(self, selected, pool):
        """Test all returned objects come from the original pool"""
        assert all(x in pool for x in selected)


# Parametrization ---------------------------------------------------
class TestPonderated(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'Ponderated' selection"""

    @fixture(scope="class")
    def selection(self):
        """Parametrization to define the selection method to use"""
        return selection.Ponderated()

    @mark.skip(reason="TODO: Help needed for asserts")
    def test_selected(self, selected, pool):  # pylint: disable=unused-argument
        """Tests the correct selection of phenotypes"""
        assert NotImplementedError


class TestUniform(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'Uniform' selection"""

    @fixture(scope="class")
    def selection(self):
        """Parametrization to define the selection method to use"""
        return selection.Uniform()

    @mark.skip(reason="TODO: Help needed for asserts")
    def test_selected(self, selected, pool):  # pylint: disable=unused-argument
        """Tests the correct selection of phenotypes"""
        assert NotImplementedError


class TestBest(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'Best' selection"""

    @fixture(scope="class")
    def selection(self):
        """Parametrization to define the selection method to use"""
        return selection.Best()

    def test_selected(self, selected, pool):
        """Tests the correct selection of phenotypes"""
        assert all(ph == pool[0] for ph in selected)


class TestWorst(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'Worst' selection"""

    @fixture(scope="class")
    def selection(self):
        """Parametrization to define the selection method to use"""
        return selection.Worst()

    def test_selected(self, selected, pool):
        """Tests the correct selection of phenotypes"""
        assert all(ph == pool[-1] for ph in selected)


class TestTournaments(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'Torunaments' selection"""

    @fixture(scope="class")
    def selection(self, tournsize):
        """Parametrization to define the selection method to use"""
        return selection.Tournaments(tournsize)

    @fixture(scope="class", params=[2, 5])
    def tournsize(self, request):
        """Parametrization to define the tournament size"""
        return request.param

    @mark.skip(reason="TODO: Help needed for asserts")
    def test_selected(self, selected, pool):  # pylint: disable=unused-argument
        """Tests the correct selection of phenotypes"""
        assert NotImplementedError
