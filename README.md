# gevopy
![qc.sec](https://github.com/BorjaEst/gevopy/actions/workflows/qc-sec.yml/badge.svg)
![qc.sty](https://github.com/BorjaEst/gevopy/actions/workflows/qc-sty.yml/badge.svg)
![qc.uni](https://github.com/BorjaEst/gevopy/actions/workflows/qc-uni.yml/badge.svg)

Awesome Genetics for Evolutionary Algorithms library created by Borja Esteban.

## Install it from PyPI
```bash
pip install gevopy
```

## Usage
This package is designed in order to create your own evolution scripts based on the following concepts:
 - **Chromosomes**: Genetic instructions for phenotypes.
 - **Genotype**: Genetic design to instantiate phenotypes.
 - **Phenotypes**: Genotype instances which perform a task.
 - **Fitness**: Provide the methods to evaluate phenotypes.
 - **Algorithm**: Evolution procedure for phenotypes.
 - **Experiment**: Evolution session with phenotypes.

Now the following sections will introduce a fast initialization to the package.
Do not hesitate to extend your knowledge by using all the additional provided
examples at the folder [examples](./examples).

### Genotypes
Define your Genotypes following the `dataclass` principles from `pydantic` by
using the base model `GenotypeModel`. All dataclass attributes are accepted in 
addition to an special type `Chromosome` provided in the module `genetics`.
To start use the already defined chromosome subclasses such `Haploid` and
`Diploid` depending on the complexity of your genetic model.
```py
from gevopy import genetics, random

class Genotype(genetics.GenotypeModel):
    chromosome_1: genetics.Haploid = Field(default_factory=lambda: random.haploid(12))
    chromosome_2: genetics.Haploid = Field(default_factory=lambda: random.haploid(10))
    simple_attribute: float = 1.0

phenotypes = [Genotype() for _ in range(20)]
```
> Note Genotype attrubutes *id*, *experiment*, *created*, *parents*,
*generation*, *score* and *clone* are attributes used by the library.
Overwriting of this attributes might lead to unexpected behaviors.

### Fitness
Create your fitness using the parent class `fitness.FitnessModel` and defining
the class method `score`. The fitness to use on the experiment will be an 
instance of the defined class. You can use the init arguments `cache` and
`parallel` to optimize how the evaluation flow is executed.

```py
from genopy import fitness

class MyFitness1(fitness.FitnessModel):
    def score(self, phenotype):
        return phenotype.chromosome.count(1)

fx = MyFitness1(cache=True, parallel=True)
```
> You can additionally define `setup` as method to execute once at the begining
of each generation before phenotypes are evaluated.

### Algorithm
The algorithm is the core of your experiment. It defines the rules of the
evolution process. You can create your own algorithm or use the already
existing templates. Algorithms are generally composed by 4 components:
 - **Selection**: Callable which provides the first list of candidates.
 - **Mating**: Callable which provides the second list of candidates.
 - **Crossover**: Callable to generate offspring from candidates.
 - **Mutation**: Callable to mutate phenotype's chromosomes.

Additionally, each algorithm template might contain additional arguments such a
`survival_rate` or `similarity`. Make sure you read and understand each of the 
arguments and steps.

```py
from gevopy.tools import crossover, mutation, selection
from gevopy import algorithms

class MyAlgorithm(algorithms.Standard):
    selection1 = selection.Tournaments(tournsize=3)
    selection2 = selection.Uniform()
    crossover = crossover.Uniform(indpb=0.01)
    mutation = mutation.SinglePoint(mutpb=0.2)

```
> The modules `tools.crossover`, `tools.mutation` and `tools.selection` contain
templates and utilities to simplify your algorithm definition.

### Experiment
The experiment is the final expression of your evolutionary algorithm.
it provides the methods to evolve and store phenotypes. Once an experiment
is instantiated, use the method `run` to force the evolution of the population
until a desired state.

The results of the experiment can be collected from the method output, calling
`best` method or adding a [Neo4j]() connection as `database` input when
instantiating the experiment to store all phenotypes during the execution.

```py
import gevopy as ea

experiment = ea.Experiment(
    fitness=MyFitness(cache=True, schedule="synchronous"),
    algorithm=MyAlgorithm(survival_rate=0.2),
)

with experiment.session() as session:
    session.add_phenotypes([MyGenotype() for _ in range(20)])
    session.run(max_generations=20, max_score=10)

```
>The method `run` forces the evolution of the experiment which is updated on
each cycle. After the method is completed, you can force again te evolution
process using higher inputs for `max_generations` or `max_score`.


## Development
Fork the repository, pick one of the issues at the [issues](https://github.com/BorjaEst/gevopy/issues)
and create a [Pull request](https://github.com/BorjaEst/gevopy/pulls).


## FAQ and Notes

### Why Graph Database?
Storing relationships at the record level makes sense in genotype 
relationships as it provides index-free adjacency.
Graph traversal operations such 'genealogy tree' or certain matches can
be performed with no index lookups leading to much better performance.
