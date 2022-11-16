"""The :mod:`genetics` module is intended to contain generic and specific
classes to design your Genotype models.

Define your Genotypes following the `dataclass` principles from `pydantic` by
using the base model `GenotypeModel`. All dataclass attributes are accepted in
addition to an special type `Chromosome` provided in the module. To start
use the already defined chromosome subclasses such `Haploid` and `Diploid`
depending on the complexity of your genetic model.
"""

import copy
import uuid
from datetime import datetime
from typing import List, MutableSequence

import numpy as np
from pydantic import BaseModel, Field, PositiveInt

from gevopy import random as ea_random


class Chromosome(np.ndarray, MutableSequence):
    """A chromosome is a long DNA molecule with part or all of the genetic
    material of an organism. In the case of Evolutionary Algorithms it
    contains the information required to evaluate a phenotype.

    This library bases chromosomes on numpy.ndarray to and therefore when
    creating one, the steps defined at `subclassing ndarray` must be followed.
    Additionally it subclasses from `collections.abc.MutableSequence` to
    provide additional and standard python methods such as `count`.

    In order to suport serialization/deserialization the new method must
    accept only the first input parameter for the function np.array.
    """

    def __new__(cls, data):
        """Standard python method required to subclass np.ndarray.
        :param cls: Chromosome ndarray subclass type
        :param data: Any object exposing the array interface or sequence
        :param pairs: Number of pairs the chromosome represents
        :return: A new generated Chromosome instance
        """
        return np.array(data, dtype="uint8").view(cls)

    def __array_finalize__(self, obj):
        """Mechanism that numpy provides to allow subclasses to handle
        the various ways that new instances get created.
        :param obj: New instance provided for slicing and `view`
        """
        if obj is None:
            return

    def insert(self, index, value):
        """Method insert is unsupported on chromosome types"""
        raise AttributeError(f"Unsupported operation by '{self.__class__}'")

    def __delitem__(self, index):
        """Method delitem is unsupported on chromosome types"""
        raise AttributeError(f"Unsupported operation by '{self.__class__}'")

    def __mutate__(self):
        """Performs the chromosome mutation operation.
        :return: Chromosome with mutated values
        """
        raise NotImplementedError

    def __eq__(self, other):
        """Standard python method to compares 2 chromosomes.
        :param other: Chromosome to compare with
        :return: Boolean, True if are equal, otherwise False
        """
        return np.array_equal(self, other)

    def __cross__(self, other):
        """Magic method to compare a chromosome bitwise.
        :param other: Chromosome to compare with
        :return: List of chromosome bits where equal
        """
        return super().__eq__(other)

    @classmethod
    def __get_validators__(cls):
        """Pydantic magic method for custom validation and deserialization.
        :yield: Validation method for construction
        """
        yield cls.validate_type

    @classmethod
    def validate_type(cls, val):
        """Validation method for construction and deserialization.
        :param val: Value to pass to __new__ data
        :return: Deserialized chromosome
        """
        return cls(data=val)


class Haploid(Chromosome):
    """The word haploid describes a condition, a cell, or an organism that
    contains half of the set of homologous chromosomes present in the somatic
    cell. Homologous chromosomes are two chromosomes that pair up by having
    the same gene sequence, loci, chromosomal length, and centromere location.

    Half of the homologous pairs are maternal (coming from the mother) whereas
    the other half, paternal (coming from the father). Thus, in other words,
    a haploid is when a cell, for instance, contains half of the total
    homologous chromosomes, i.e. a single set of chromosomes that are unpaired.
    """

    @classmethod
    @property
    def states(cls):
        """Returns the number of possible chromosome states.
        :return: Chromosome with inverted values
        """
        return 2

    def __invert__(self):
        """Computes and returns the bit-wise inversion of the chromosome.
        :return: Chromosome with inverted values
        """
        return np.logical_not(self).view("uint8")

    def __mutate__(self):
        """Computes and returns the bit-wise mutation of the chromosome.
        :return: Chromosome with mutated values
        """
        return ea_random.haploid(self.size)


class Diploid(Chromosome):
    """In genetics and biology, the term diploid refers to the cell containing
    two sets of homologous chromosomes wherein each chromosome in a set is
    obtained from each of the two-parent cells.

    As example, the fusion of two haploid sex cells results in the formation
    of a diploid cell called a zygote.
    """

    @classmethod
    @property
    def states(cls):
        """Returns the number of possible chromosome states.
        :return: Chromosome with inverted values
        """
        return 4

    def __invert__(self):
        """Computes and returns the bit-wise inversion of the chromosome.
        :return: Chromosome with inverted values
        """
        return np.bitwise_and(super().__invert__(), 3)

    def __mutate__(self):
        """Computes and returns the bit-wise mutation of the chromosome.
        :return: Chromosome with mutated values
        """
        return ea_random.diploid(self.size)


class Triploid(Chromosome):
    """Similar to haploid and diploid, cells can contain three sets of
    homologous chromosomes, increasing the amount of combinations for each
    bit (trinary) position.

    In biology triploidy is a rare chromosomal abnormality.
    """

    @classmethod
    @property
    def states(cls):
        """Returns the number of possible chromosome states.
        :return: Chromosome with inverted values
        """
        return 8

    def __invert__(self):
        """Computes and returns the bit-wise inversion of the chromosome.
        :return: Chromosome with inverted values
        """
        return np.bitwise_and(super().__invert__(), 7)

    def __mutate__(self):
        """Computes and returns the bit-wise mutation of the chromosome.
        :return: Chromosome with mutated values
        """
        return ea_random.triploid(self.size)


class GenotypeModel(BaseModel):
    """Evolution Genotype is the most basic but flexible form of genetics.
    It is a chromosomes container with an unique identifier. Different
    organisms might have different numbers of chromosomes.

    When subclassing a genotype note the following attributes are reserved:
     - id: A unique identifier for the phenotype
     - experiment: Name of the experiment the phenotype belongs, can be None
     - created: Datetime when the phenotype was instantiated
     - parents: List of phenotype ids used to generate the phenotype
     - generation: Positive integer indicating the evolution generations
     - score: Float indicating the phenotype score (None, when not evaluated)
     - clone: Method to produce a genotype deep copy with different id
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    experiment: str = None
    created: datetime = Field(default_factory=datetime.utcnow)
    parents: List[uuid.UUID] = []
    generation: PositiveInt = Field(default=1)
    score: float = None

    class Config:  # pylint: disable=missing-class-docstring
        json_encoders = {Chromosome: lambda x: x.astype("uint8").tolist()}

    def clone(self):
        """Clones the phenotype producing a copy with different id and
        an empty score.
        :return: Phenotype copy
        """
        clone = copy.deepcopy(self)
        clone.id = uuid.uuid4()  # Generate new id
        clone.score = None  # Reset the clone score
        return clone

    def __repr__(self):
        """Representation method for phenotype. It displays the class name
        together with the phenotype id.
        :return: String representing the genotype instance (phenotype)
        """
        return f"{self.__class__.__name__} {self.id}"
