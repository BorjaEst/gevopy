"""Module to test genotype requirements"""
# pylint: disable=redefined-outer-name

import uuid
from collections.abc import MutableSequence
from datetime import datetime

from pytest import fixture

from gevopy import genetics


# Module fixtures ---------------------------------------------------
@fixture(scope="class")
def clone(phenotype):
    """Fixture to return a phenotype clone"""
    return phenotype.clone()


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Genotype instances attributes"""

    def test_attr_chromosome(self, phenotype):
        """Test phenotype has a correct 'chromosome' attribute"""
        assert hasattr(phenotype, "chromosome")
        assert isinstance(phenotype.chromosome, MutableSequence)

    def test_attr_id(self, phenotype):
        """Test phenotype has a correct 'id' attribute"""
        assert hasattr(phenotype, "id")
        assert isinstance(phenotype.id, uuid.UUID)

    def test_attr_created(self, phenotype):
        """Test phenotype has a correct 'created' attribute"""
        assert hasattr(phenotype, "created")
        assert isinstance(phenotype.created, datetime)

    def test_attr_parents(self, phenotype):
        """Test phenotype has a correct 'parents' attribute"""
        assert hasattr(phenotype, "parents")
        assert isinstance(phenotype.parents, list)

    def test_attr_generation(self, phenotype):
        """Test phenotype has a correct 'generation' attribute"""
        assert hasattr(phenotype, "generation")
        assert isinstance(phenotype.generation, int)
        assert phenotype.generation > 0

    def test_attr_score(self, phenotype):
        """Test phenotype has a correct 'score' attribute"""
        assert hasattr(phenotype, "score")
        assert isinstance(phenotype.score, type(None))

    def test_is_instance_genotype(self, phenotype):
        """Test phenotype is instance of GenotypeModel"""
        assert isinstance(phenotype, genetics.GenotypeModel)


class CloneRequirements:
    """Tests group for phenotype clone function"""

    def test_clone_id(self, phenotype, clone):
        """Test clone 'id' is different from phenotype"""
        assert clone.id != phenotype.id

    def test_clone_chromosome(self, phenotype, clone):
        """Test clone 'chromosome' is equal to phenotype"""
        assert clone.chromosome == phenotype.chromosome

    def test_clone_parents(self, phenotype, clone):
        """Test clone 'parents' are equal to phenotype"""
        assert clone.parents == phenotype.parents

    def test_clone_generation(self, phenotype, clone):
        """Test clone 'generation' is equal to phenotype"""
        assert clone.generation == phenotype.generation


# Parametrization ---------------------------------------------------
class TestGenotype(AttrRequirements, CloneRequirements):
    """Parametrization for testing Genotypes"""

    @fixture(scope="class")
    def phenotype(self, genotype):
        """Fixture to return a genotype instance"""
        return genotype()
