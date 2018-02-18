MVA - Algorithms for Speech and NLP TD 3
========================================

Normalisation system that can change raw English tweets into (partially) normalised tweets, suitable for further NLP processing. The system use two types of information for performing this normalisation task: contextual information and formal similarity information.

## How to use the system ?

Simply run the run_system.sh bash file
```
sh run_system.sh
```

It takes 5 arguments in the following order:
- CORPUS_FILE: simply the name of the .txt file, previously put in *system* directory
- FIRST_RAW: the first raw where to start normalisation (int)
- LAST_RAW: the last raw where to stop normalisation (int)
- N_RESULTS: number of context2vec results to consider (int)
- VERBOSE: 1 to print each incorrect word and its correction (0 or 1)

As an example, one can run
```
sh run_system.sh CorpusBataclan_en.1M.raw.txt 0 100 10000 1
```

Note that normalised corpus will be written in normalised_CORPUS_FILE in the *system* directory.

IMPORTANT NOTE: two variables need to be changed: CONTEXT2VECDIR (context2vec directoty) and MODELPARAMS (context2vec model parameter file).

## Requirements

- numpy
- nltk (v3.0)
- context2vec
- tqdm