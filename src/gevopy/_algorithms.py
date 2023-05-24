import typing


# Global module variable prepared to store defined algorithm functions
available_algorithms = set()
Algorithm = typing.Callable[[str], None]


class algorithm_definition(object):
    def __init__(self, algorithm_id):
        available_algorithms.add(algorithm_id)

    def __call__(self, algorithm_function):
        return algorithm_function


@algorithm_definition(algorithm_id="standard")
def standard(population: str) -> None:
    raise NotImplementedError  # TODO: return a single genotype
