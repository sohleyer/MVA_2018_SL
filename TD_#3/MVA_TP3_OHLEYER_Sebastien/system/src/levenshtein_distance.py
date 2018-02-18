"""
Levenshtein distance.

Written by Sebastien Ohleyer
"""

import numpy as np

def levenshtein_distance(s1,s2):
    """
    Compute the Levenshtein distance between two strings.

    Args:
        s1, s2: two strings between the Levenshtein distance need to be computed

    Return:
        Levenshtein distance between s1 and s2
    """

    m = np.zeros((len(s1)+1, len(s2)+1))
    
    for i in range(len(s1)+1):
        m[i,0] = i
    for j in range(len(s2)+1):
        m[0,j] = j
        
    for i in range(1,len(s1)+1):
        for j in range(1,len(s2)+1):
            if s1[i-1] == s2[j-1]:
                m[i,j] = min( m[i-1,j]+1, m[i,j-1]+1, m[i-1,j-1] )
            else:
                m[i,j] = min( m[i-1,j]+1, m[i,j-1]+1, m[i-1,j-1]+1 )
    return m[len(s1), len(s2)]