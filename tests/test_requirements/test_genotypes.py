"""Module to test genotype requirements"""
# pylint: disable=redefined-outer-name

import uuid
from collections.abc import MutableSequence
from datetime import datetime

from pytest import fixture

from gevopy import genetics


# Module fixtures ---------------------------------------------------
@fixture(scope="class")
def clone(genotype):
    """Fixture to return a genotype clone"""
    return genotype.clone()


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Genotype instances attributes"""

    def test_attr_chromosome(self, genotype):
        """Test genotype has a correct 'chromosome' attribute"""
        assert hasattr(genotype, "chromosome")
        assert isinstance(genotype.chromosome, MutableSequence)

    def test_attr_id(self, genotype):
        """Test genotype has a correct 'id' attribute"""
        assert hasattr(genotype, "id")
        assert isinstance(genotype.id, uuid.UUID)

    def test_attr_created(self, genotype):
        """Test genotype has a correct 'created' attribute"""
        assert hasattr(genotype, "created")
        assert isinstance(genotype.created, datetime)

    def test_attr_parents(self, genotype):
        """Test genotype has a correct 'parents' attribute"""
        assert hasattr(genotype, "parents")
        assert isinstance(genotype.parents, list)

    def test_attr_generation(self, genotype):
        """Test genotype has a correct 'generation' attribute"""
        assert hasattr(genotype, "generation")
        assert isinstance(genotype.generation, int)
        assert genotype.generation > 0

    def test_is_instance_genotype(self, genotype):
        """Test genotype is instance of GenotypeModel"""
        assert isinstance(genotype, genetics.GenotypeModel)


class CloneRequirements:
    """Tests group for genotype clone function"""

    def test_clone_id(self, genotype, clone):
        """Test clone 'id' is different from genotype"""
        assert clone.id != genotype.id

    def test_clone_chromosome(self, genotype, clone):
        """Test clone 'chromosome' is equal to genotype"""
        assert clone.chromosome == genotype.chromosome

    def test_clone_parents(self, genotype, clone):
        """Test clone 'parents' are equal to genotype"""
        assert clone.parents == genotype.parents

    def test_clone_generation(self, genotype, clone):
        """Test clone 'generation' is equal to genotype"""
        assert clone.generation == genotype.generation


# Parametrization ---------------------------------------------------
class TestGenotype(AttrRequirements, CloneRequirements):
    """Parametrization for testing Genotypes"""

    @fixture(scope="class")
    def genotype(self, genotype):
        """Fixture to return a genotype instance"""
        return genotype()
