# Package imports
import sys
import time
import re
import numpy as np
from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm
from clean_utils import clean_tweet, clean_tweet_list, is_number, merge_tweet_file
from levenshtein_distance import levenshtein_distance

corpus_file = sys.argv[1]
context2vec_dir = sys.argv[2]
model_param_file = sys.argv[3]
first_raw = int(sys.argv[4])
last_raw = int(sys.argv[5])
n_results = int(sys.argv[6])
verbose = int(sys.argv[7])

sys.path.append(context2vec_dir)
from common.model_reader import ModelReader
from explore_context2vec_func import explore_context2vec

#############################
print "Opening file..."
f = open(corpus_file)


#############################
print "Merge raws of same retweet..."
rtweet_list = merge_tweet_file(f)


#############################
print 'Clean tweets...'
rtweet_list = clean_tweet_list(rtweet_list, first_raw, last_raw)


#############################
print "Correcting tweets..."
start = time.time()
model_reader = ModelReader(model_param_file)
w = model_reader.w
word2index = model_reader.word2index
index2word = model_reader.index2word
model = model_reader.model

#some key to delete from the lexicon
key_to_delete = ['.', '?', '<UNK>', '<BOS>', '<EOS>']
for key in key_to_delete:
	index2word.remove(key)

stop = time.time()
print "Time to import model context2vec:", stop-start

target_exp = re.compile('\[.*\]')
tokenizer = RegexpTokenizer(r'\w+') # setup tokenizer

normalised_rtweet_list = []
for idx,tweet in tqdm(enumerate(rtweet_list)):
    if verbose==1:
    	print idx, tweet

    tokenize_tweet = tokenizer.tokenize(tweet)
    for token in tokenize_tweet:
        if is_number(token):
            continue
            
        #find incorrect words
        if token not in word2index:  
            if verbose==1:
            	print ">> incorrect word:", token
            
            #generate context
            context = re.sub(token, '[]', tweet)
            context_proposition = explore_context2vec(context, w, word2index, index2word, model, target_exp, n_results)
            
            #find clother word in context
            min_dist = np.inf 
            for proposition in context_proposition:
                dist = levenshtein_distance(token,proposition)
                if dist < min_dist:
                    min_dist = dist
                    correct_word = proposition[0]
            if verbose==1:
            	print ">> correction:", correct_word
            	print '>> Levenshtein distance:', min_dist
            correct_tweet = re.sub(token, correct_word, tweet)
        else:
            correct_tweet = tweet
    if verbose==1:
    	print correct_tweet, '\n'
    normalised_rtweet_list.append(correct_tweet)

print 'Writing file...'
normalised_corpus = open('normalised_'+corpus_file, 'w')
for tweet in normalised_rtweet_list:
  normalised_corpus.write("%s\n" % tweet)
print 'Normalised corpus written, see: ', 'normalised_'+corpus_file
