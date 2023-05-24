from pydantic import BaseModel, Extra, validator

from gevopy import _algorithms, _schedulers, _selections, config
from gevopy.genetics import GenotypeModel, HasPopulations
from gevopy.tools import HasEvolTools


class App(HasPopulations, HasEvolTools):
    def __init__(self, name: str, **config) -> None:
        if not isinstance(name, str):
            raise TypeError("Expected string type for application name.")
        HasPopulations.__init__(self, **config)
        HasEvolTools.__init__(self, **config)
        self.config = config
        self.config['name'] = name


def run(
    application: App,
    scheduler: _schedulers.Scheduler = config.DEFAULT_SCHEDULER,
    selection: _selections.Selection = config.DEFAULT_SELECTION,
    algorithm: _algorithms.Algorithm = config.DEFAULT_ALGORITHM,
    **end_conditions
):
    execution = Execution(**end_conditions)
    try:  # Try an except to return exection pointer to user
        print("Start of evolutionary experiment execution")
        while True:
            execution.pool = eval_genotypes(session, fitness)
            execution.halloffame.update(execution.pool)
            execution.generation += 1  # Increase generation index
            save_genotypes(session)
            if execution.completed():
                print("Experiment execution completed successfully")
                return execution  # End of evolution process
            else:
                print("Completed cycle; %s", execution.best_score)
                session.population = generate_offspring(execution, algorithm)
    except KeyboardInterrupt:  # Interrupted by user
        print("Experiment cancelled by the user 'CTRL+C'")
        return execution
    except Exception as error:  # Unexpected exception
        print("Error %s raised during experiment execution", error)
        return execution



class Execution(BaseModel, extra=Extra.forbid):
    """Base class for evolution algorithm execution. This class uses an
    experiment session to run evolution cycles and generations on a population
    of genotypes. It also includes statistics about the execution process.
    """
    max_score: float | int = None,
    max_generations: int = None,
    score: float | int = None
    generation: int = 0

    @validator('max_score')
    def max_score_is_numeric(cls, max_score, values, **kwds):
        if max_score and not isinstance(max_score, [float, int]):
            raise TypeError("Expected type float|int for max_score")
        return max_score

    @validator('max_generations')
    def max_generations_is_int(cls, max_generations, values, **kwargs):
        if max_generations and not isinstance(max_generations, int):
            raise TypeError("Expected type int for max_generations")
        return max_generations

    @validator('max_generations')
    def max_generations_positive(cls, max_generations, values, **kwargs):
        if max_generations and max_generations <= 0:
            raise ValueError("Expected positive int for max_generations")
        return max_generations

    def completed(self):
        """Evaluates if the final generation or required score is reached.
        :return: True if evolution conditions are met, False otherwise
        """
        if self.min_generation:
            if self.generation < self.min_generation:
                return False  # Keep running even if score met
        if self.max_score:
            if self.best_score >= self.max_score:
                return True  # Stop if max score reached
        if self.min_score:
            if self.worse_score >= self.min_score:
                return True  # Stop if min score reached
        if self.max_generation:
            if self.generation >= self.max_generation:
                return True  # Stop if max generation reached
        return False  # If any of the defined
