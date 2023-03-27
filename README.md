<h1 align="left">
<img src="README_files/gevopy-logo2.png" width="600">
</h1><br>

![qc.sec](https://github.com/BorjaEst/gevopy/actions/workflows/qc-sec.yml/badge.svg)
![qc.sty](https://github.com/BorjaEst/gevopy/actions/workflows/qc-sty.yml/badge.svg)
![qc.uni](https://github.com/BorjaEst/gevopy/actions/workflows/qc-uni.yml/badge.svg)

Awesome Genetics for Evolutionary Algorithms library created by Borja Esteban.

## Install it from PyPI
```bash
$ pip install gevopy
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


```python
from gevopy import genetics, random
from gevopy.genetics import Field

class MyGenotype(genetics.GenotypeModel):
    chromosome_1: genetics.Haploid = Field(default_factory=lambda: random.haploid(12))
    chromosome_2: genetics.Haploid = Field(default_factory=lambda: random.haploid(10))
    simple_attribute: float = 1.0

[MyGenotype() for _ in range(2)]
```




    [{'id': UUID('8b77fc1d-befe-4ad3-924c-1774223b7b60'),
      'experiment': None,
      'created': datetime.datetime(2023, 3, 4, 15, 24, 49, 325435),
      'parents': [],
      'generation': 1,
      'score': None,
      'chromosome_1': Haploid([0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0], dtype=uint8),
      'chromosome_2': Haploid([1, 0, 1, 1, 1, 0, 0, 1, 0, 1], dtype=uint8),
      'simple_attribute': 1.0},
     {'id': UUID('a4460974-a45a-4ed2-8937-55ea211bb520'),
      'experiment': None,
      'created': datetime.datetime(2023, 3, 4, 15, 24, 49, 325564),
      'parents': [],
      'generation': 1,
      'score': None,
      'chromosome_1': Haploid([1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0], dtype=uint8),
      'chromosome_2': Haploid([1, 0, 1, 1, 1, 0, 0, 1, 0, 1], dtype=uint8),
      'simple_attribute': 1.0}]



> Note Genotype attrubutes *id*, *experiment*, *created*, *parents*,
*generation*, *score* and *clone* are attributes used by the library.
Overwriting of this attributes might lead to unexpected behaviors.

### Fitness
Create your fitness using the parent class `fitness.FitnessModel` and defining
the class method `score`. The fitness to use on the experiment will be an 
instance of the defined class. You can use the init arguments `cache` and
`scheduler` (from Dask) to optimize how the evaluation flow is executed.


```python
from gevopy import fitness

class MyFitness(fitness.FitnessModel):
    def score(self, phenotype):
        x1 = phenotype.chromosome_1.count(1)
        x2 = phenotype.chromosome_2.count(0)
        return x1 - x2

MyFitness(cache=True, scheduler="threads")
```




    <__main__.MyFitness at 0x7f19e0744f40>



> You can additionally define `setup` as method to execute once at the begining
of each generation before phenotypes are evaluated.

> The only accepted values for scheduler are `synchronous`, `threads` and `processes`.
By default `threads` is used.

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


```python
from gevopy.tools import crossover, mutation, selection
from gevopy import algorithms

class MyAlgorithm(algorithms.Standard):
    selection1 = selection.Tournaments(tournsize=3)
    selection2 = selection.Uniform()
    crossover = crossover.Uniform(indpb=0.01)
    mutation = mutation.SinglePoint(mutpb=0.2)

MyAlgorithm()
```




    MyAlgorithm(selection1=<gevopy.tools.selection.Tournaments object at 0x7f19906ca680>, mutation=<gevopy.tools.mutation.SinglePoint object at 0x7f19906ca710>, selection2=<gevopy.tools.selection.Uniform object at 0x7f19906ca770>, crossover=<gevopy.tools.crossover.Uniform object at 0x7f19906c8ee0>, survival_rate=0.4)



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


```python
import gevopy as ea

experiment = ea.Experiment()
with experiment.session() as session:
    session.add_phenotypes([MyGenotype() for _ in range(20)])
    session.algorithm = MyAlgorithm(survival_rate=0.2)
    session.fitness = MyFitness(cache=True, scheduler="synchronous")
    statistics = session.run(max_generation=20, max_score=10)

experiment.close()
statistics
```

    Evolutionary algorithm execution report:
      Executed generations: 12
      Best phenotype: 7b13630f-d07c-4ff6-8be1-df6d6ceb06ca
      Best score: 10


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

### Why pydantic instead of dataclass?
Pydantic supports validation of fields during and after the
initialization process and makes parsing easier. 
Parsing is a relevant step if you are planing to save your
phenotypes into the connected database.

### Limitations
Collections containing collections can not be stored in properties.
Property values can only be of primitive types or arrays in Neo4J Cypher queries.
