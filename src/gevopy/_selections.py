import typing
from gevopy import genetics

# Global module variable prepared to store defined selection functions
available_selections = set()
Selection = typing.Callable[[str], genetics.GenotypeModel]


class selection_definition(object):
    def __init__(self, selection_id):
        available_selections.add(selection_id)

    def __call__(self, selection_function):
        return selection_function


@selection_definition(selection_id="roulette_wheel")
def roulette_wheel(population: str) -> genetics.GenotypeModel:
    raise NotImplementedError  # TODO: return a single genotype


@selection_definition(selection_id="rank")
def rank(population: str) -> genetics.GenotypeModel:
    raise NotImplementedError  # TODO: return a single genotype


@selection_definition(selection_id="steady_state")
def steady_state(population: str) -> genetics.GenotypeModel:
    raise NotImplementedError  # TODO: return a single genotype


@selection_definition(selection_id="tournament")
def tournament(population: str) -> genetics.GenotypeModel:
    raise NotImplementedError  # TODO: return a single genotype


@selection_definition(selection_id="elitist")
def elitist(population: str) -> genetics.GenotypeModel:
    raise NotImplementedError  # TODO: return a single genotype


@selection_definition(selection_id="boltzmann")
def boltzmann(population: str) -> genetics.GenotypeModel:
    raise NotImplementedError  # TODO: return a single genotype
