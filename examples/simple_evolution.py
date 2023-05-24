"""TODO: Add some description
"""
import random
# from random import randint
from typing import List

from pydantic import Field

import gevopy
from gevopy.utils import crosslist
from numpy.random import randint
import uuid

app = gevopy.App(__name__)


class Genotype(gevopy.GenotypeModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    x1: List[int] = Field(default_factory=lambda: randint(0, 9, size=100))

    def phenotype(self):
        return {'id': self.id, 'x': self.x1}


@app.add_crossover([Genotype])
def crossover(genotype1, genotype2):
    indexes = set(random.randint(0, 100) for _ in range(3))
    crosslist(genotype1.x1, genotype2.x1, sorted(indexes))


@app.add_mutation([Genotype])
def mutation(genotype):
    indexes = list(set(random.randint(0, 100) for _ in range(3)))
    genotype.x1[indexes] = random.randint(0, 9)


@app.add_evaluator(Genotype, cache=True)
def evaluator(genotype):
    phenotype = genotype.phenotype()
    return phenotype['x'].count(0)
