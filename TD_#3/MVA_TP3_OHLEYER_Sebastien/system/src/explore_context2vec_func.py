'''
A simple interactive utility for exploring context2vec models.

>> c1 c2 [] c3 c4 ...
returns the top-10 target words whose embedding is most similar to the sentential context embedding (target-to-context similarity)

>> [t]
returns the top-10 target words whose embedding is most similar to the target embedding of t (target-to-target similarity)

>> c1 c2 [t] c3 c4 ...
returns the top-10 target words whose combined similarity to both sentential context and target embedding is highest 
(not giving very good results at the moment...)


Written by Sebastien Ohleyer and widely inspired by eval_context2vec.py in package context2vec (the main work here was to make
these functions callable from our system).
'''

#!/usr/bin/env python
import numpy
import six
import sys
import traceback
import re

from chainer import cuda
#from context2vec.common.context_models import Toks
#from context2vec.common.model_reader import ModelReader

class ParseException(Exception):
    def __init__(self, str):
        super(ParseException, self).__init__(str)


def parse_input(line, target_exp):
    sent = line.strip().split()
    target_pos = None
    for i, word in enumerate(sent):
        if target_exp.match(word) != None:
            target_pos = i
            if word == '[]':
                word = None
            else:
                word = word[1:-1]
            sent[i] = word
    return sent, target_pos
    

def mult_sim(w, target_v, context_v):
    target_similarity = w.dot(target_v)
    target_similarity[target_similarity<0] = 0.0
    context_similarity = w.dot(context_v)
    context_similarity[context_similarity<0] = 0.0
    return (target_similarity * context_similarity)
 


def explore_context2vec(line, w, word2index, index2word, model, target_exp, n_result):
    """
    Generate context with pre-trained context2vec model.

    Args:
        line: str line to perform context2vec. Omitted word is symbolised by []
        w: ModelReader.w
        word2index: ModelReader.word2index
        index2word: ModelReader.index2word
        model: ModelReader.model
        target_exp: Compilation of re package
        n_result: number of result to generate

    Return:
        results: context2vec results
    """
    results = []
    try:
        #line = six.moves.input('>> ')
        sent, target_pos = parse_input(line, target_exp)
        if target_pos == None:
            raise ParseException("Can't find the target position.") 
        
        if sent[target_pos] == None:
            target_v = None
        elif sent[target_pos] not in word2index:
            raise ParseException("Target word is out of vocabulary.")
        else:
            target_v = w[word2index[sent[target_pos]]]

        if len(sent) > 1:
            context_v = model.context2vec(sent, target_pos) 
            context_v = context_v / numpy.sqrt((context_v * context_v).sum())
        else:
            context_v = None
        
        if target_v is not None and context_v is not None:
            similarity = mult_sim(w, target_v, context_v)
        else:
            if target_v is not None:
                v = target_v
            elif context_v is not None:
                v = context_v                
            else:
                raise ParseException("Can't find a target nor context.")   
            similarity = (w.dot(v)+1.0)/2 # Cosine similarity can be negative, mapping similarity to [0,1]

        count = 0
        for i in (-similarity).argsort():
            if numpy.isnan(similarity[i]):
                continue
#            print('{0}: {1}'.format(index2word[i], similarity[i]))
            count += 1
            results.append((index2word[i], similarity[i]))
            if count == n_result:
                break

    except ParseException as e:
        print "ParseException: {}".format(e)                
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** print_tb:"
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print "*** print_exception:"
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    return results
