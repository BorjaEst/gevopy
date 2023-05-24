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
 - **Fitness**: Provide the methods to evaluate genotypes.
 - **Algorithm**: Evolution procedure for phenotypes.
 - **Experiment**: Evolution session with genotypes.

Now the following sections will introduce a fast initialization to the package.
Do not hesitate to extend your knowledge by using all the additional provided
examples at the folder [examples](./examples).


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
genotypes into the connected database.

### Limitations
Collections containing collections can not be stored in properties.
Property values can only be of primitive types or arrays in Neo4J Cypher queries.
