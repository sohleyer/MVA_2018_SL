#!/bin/bash

CORPUSFILE="$1"
FIRST_RAW="$2"
LAST_RAW="$3"
N_RESULTS="$4"
VERBOSE="$5"
CONTEXT2VECDIR="./context2vec/"
MODELPARAMS="./MODEL_DIR/context2vec.ukwac.model.params"

echo "Path to the raw corpus to be normalised: $CORPUSDIR"
echo "context2vec directory: $CONTEXT2VECDIR"
echo "Raws to be normalised (as a list slice): [$FIRST_RAW:$LAST_RAW]"
echo "Number of context2vec results to consider: $N_RESULTS\n"


echo "Run src/normalise_corpus.py"
python src/normalise_corpus.py $CORPUSFILE $CONTEXT2VECDIR $MODELPARAMS $FIRST_RAW $LAST_RAW $N_RESULTS $VERBOSE