"""Examples module for users on how to generate genotypes and testing

Note that the example names are not really matching with the reality as it
might be impossible to fully represent biological genotypes. However they
might serve well for ilustration purposes.
"""
from dataclasses import dataclass

from gevopy import random
from gevopy.genetics import Diploid, GenotypeModel, Haploid, field


# ------------------------------------------------------------------
# Bacteria ---------------------------------------------------------
# This genotypes are known to have asexual reproduction and with a
# unique chromosome. In this example values can be only between 0 and 1
# See https://docs.python.org/3/library/dataclasses.html
@dataclass
class Bacteria(GenotypeModel):
    """Simple and most basic haploid genotype"""
    chromosome: Haploid = field(default_factory=lambda: random.haploid(12))


# ------------------------------------------------------------------
# JackJumper -------------------------------------------------------
# Although males are know to be composed by haploids, this is a good
# example of how to design a chromosome where values can take more
# values than 1 or 0 (0-3) due to that each value in the chromosome
# might be composed by 2 bits ([00][00]-...-[00][00]).
# See https://docs.python.org/3/library/dataclasses.html
@dataclass
class JackJumper(GenotypeModel):
    """This anst are known to have a single pair of chromosomes"""
    chromosome: Diploid = field(default_factory=lambda: random.diploid(12))
