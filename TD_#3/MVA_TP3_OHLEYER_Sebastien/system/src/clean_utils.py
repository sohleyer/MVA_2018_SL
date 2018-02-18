"""
Some useful functions to clean tweets.

Written by Sebastien Ohleyer.
"""

import time
import re 
from tqdm import tqdm


def is_number(input_str):
    """
    Check if a string is a number.

    Args:
        input_str: input string

    Return:
        output string
    """
    try:
        float(input_str)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(input_str)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

 
def put_space(input_str):
    """
    Put spaces between words starting with capital letters using Regex in Python

    Args:
        input_str: input string

    Return:
        output string
    """
    # regex [A-Z][a-z]* means any string starting with capital character followed by many lowercase letters 
    words = re.findall('[A-Z][a-z]*', input_str.group(0))
 
    # Change first letter of each word into lowercase
    result = []
    for word in words:
        word = chr( ord (word[0]) + 32) + word[1:]
        result.append(word)
    return ' '.join(result)


def clean_tweet(tweet):
    """
    Perform different cleaning operations.

    Args:
        tweet: input tweet

    Return:
        cleaning tweet
    """
    # Remove URL
    clean_tweet = re.sub(r"http\S+", "", tweet)
    
    # Remove 'RT'
    clean_tweet = re.sub(r"RT ", "", clean_tweet)
    
    # Remove tags
    clean_tweet = re.sub(r"@\S+ ", "", clean_tweet)
    
    # Remove \n
    clean_tweet = re.sub(r"\n", " ", clean_tweet)
    
    # Remove hex characters
    clean_tweet = re.sub(r'[^\x00-\x7f]',r'', clean_tweet) 
    
    # Deal with #
    clean_tweet = re.sub(r'#\S+',put_space, clean_tweet)

    # Remove # and *
    clean_tweet = re.sub(r'#','', clean_tweet)
    clean_tweet = re.sub(r'\*','', clean_tweet)
    
    # Convert uppercase to lowercase
    clean_tweet = clean_tweet.lower() # need to remove uppercase to compute edit distance to the words in dictionary
    
    return clean_tweet


def clean_tweet_list(rtweet_list, first_raw, last_raw):
    start = time.time()
    tweets_to_clean = list(rtweet_list)
    rtweet_list = []
    for tweet in tqdm(tweets_to_clean[first_raw:last_raw]):
        tweet_cleaned = clean_tweet(tweet)
        rtweet_list.append(tweet_cleaned)
    stop = time.time()
    print 'Time to clean tweets: ', stop-start, '\n'
    return rtweet_list


def merge_tweet_file(file):
    raw_list = list(file)
    rtweet_list = []
    for raw in raw_list:
        if raw[:2] == 'RT':
            rtweet_list.append(raw)
        else:
            rtweet_list[-1] = rtweet_list[-1] + raw

    print 'Number of raws:', len(raw_list)
    print 'Number of effective retweets:', len(rtweet_list), '\n'
    return rtweet_list


