import uuid

import pydantic


class GenotypeModel(pydantic.BaseModel):
    pass


class HasGenotypes(object):
    def __init__(self, *args, **kwds):
        self.evaluators = {}
        self.genotypes = []

    def add_evaluator(self, genotype_class, cache=False):
        # TODO: How to cache
        if not issubclass(genotype_class, GenotypeModel):
            raise TypeError("Expected GenotypeModel class on evaluator.")

        def decorator_evaluator(fitness_function):
            self.evaluators[genotype_class] = fitness_function
            self.genotypes.append(genotype_class)
            return fitness_function
        return decorator_evaluator


class HasPopulations(HasGenotypes):
    def __init__(self, *args, **kwds):
        HasGenotypes.__init__(self, *args, **kwds)
        self.populations = {}

    def spawn_population(self, genotype_class, n, name=None):
        if not issubclass(genotype_class, GenotypeModel):
            raise TypeError("Expected GenotypeModel class as genotype_class.")
        if not isinstance(n, int):
            raise TypeError("Expected ammount of genotypes (n) as integer.")
        name = name or str(uuid.uuid4())
        self.populations[name] = [genotype_class() for _ in range(n)]
        return name

    def kill_population(self, name):
        if not isinstance(name, str):
            raise TypeError("Expected string for population name identifier.")
        try:
            del self.populations[name]
        except KeyError:
            raise KeyError(f"Population {name} not found in {self}")
