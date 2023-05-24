import collections
import itertools


class HasCrossovers(object):
    def __init__(self, *args, **kwds):
        self.crossovers = collections.defaultdict(list)

    def add_crossover(self, genotype_classes):
        if not isinstance(genotype_classes, list):
            raise TypeError("Expected list of GenotypeModel class.")

        def decorator_crossover(crossing_function):
            for pair in itertools.product(genotype_classes, repeat=2):
                self.crossovers[pair].append(crossing_function)
            return crossing_function
        return decorator_crossover

    def cross(self, genotype1, genotype2):
        index = (genotype1.__class__, genotype2.__class__)
        for crossing_function in self.crossovers[index]:
            crossing_function(genotype1, genotype2)


class HasMutations(object):
    def __init__(self, *args, **kwds):
        self.mutations = collections.defaultdict(list)

    def add_mutation(self, genotype_classes):
        if not isinstance(genotype_classes, list):
            raise TypeError("Expected list of GenotypeModel class.")

        def decorator_mutation(mutation_function):
            for gen in genotype_classes:
                self.mutations[gen].append(mutation_function)
            return mutation_function
        return decorator_mutation

    def mutate(self, genotype):
        for mutation_function in self.mutations[genotype.__class__]:
            mutation_function(genotype)


class HasEvolTools(HasCrossovers, HasMutations):
    def __init__(self, *args, **kwds):
        HasCrossovers.__init__(self, *args, **kwds)
        HasMutations.__init__(self, *args, **kwds)
