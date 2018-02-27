MVA - Algorithms for Speech and NLP TD 4
========================================

Basic probabilistic parser for French based on the CYK (Cocke–Younger–Kasami or CKY) algorithm and the Probabilistic Context-Free Grammar (PCFG) model.

## How to use the system ?

Simply run the run_parser.sh bash file
```
cat ../sequoia-corpus+fct.mrg_strict.txt | ./run_parser.sh
```


## Requirements

- numpy
- graphviz
- tqdm