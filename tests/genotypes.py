"""Module for test genotypes"""
from gevopy import genetics, random


class OneHaploid(genetics.GenotypeModel):
    """Simple and most basic haploid genotype"""
    chromosome: genetics.Haploid = genetics.Field(
        default_factory=lambda: random.haploid(size=12)
    )


class OneDiploid(genetics.GenotypeModel):
    """Simple and most basic diploid genotype"""
    chromosome: genetics.Diploid = genetics.Field(
        default_factory=lambda: random.diploid(size=12)
    )
