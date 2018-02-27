import fileinput

from tree import *
from pcfg import *

import numpy as np
np.warnings.filterwarnings('ignore')
np.random.seed(13)

# STEP 1, read on std input
tree_repr_db = []
for line in fileinput.input():
    tree_repr = line.strip()
    if len(tree_repr) == 0:
        continue

    while tree_repr[-1] == ' ':
        tree_repr = tree_repr[:-1]

    tree_repr_db.append(tree_repr)
    pass

# STEP 2, 90% train, 10% test
N = len(tree_repr_db)
train_indices = sorted(list(np.random.choice(range(N),int(N*0.9),replace=False)))
test_indices = sorted(list(set(range(N)).difference(set(train_indices))))

train_set = list(np.array(tree_repr_db)[train_indices])
test_set = list(np.array(tree_repr_db)[test_indices])
print("######## LOADING DATA ########\n\t{} sentences in db\n\t{} in train set\n\t{} in test set".format(N,len(train_set),len(test_set)))

# STEP 3, LEARNING THE GRAMMAR
print("\n######## LEARNING PCFG ########")

def remove_functional(s):
    '''
        e.g. NP-MOD -> NP
    '''
    return s.split('-')[0]

bin_forest = []
for tree_repr in train_set:
    t = tree(repr_to_root(tree_repr,label_filter=remove_functional))
    t_b = t.get_binarized()
    bin_forest.append(t_b)

pcfg = PCFG()
pcfg.learn_from_bin_forest(bin_forest)
print("PCFG statistics:\n")
print("\t{} terminals\n\t{} variables\n\t{} binary rules\n\t{} preterminal rules".format(len(pcfg.terminals),len(pcfg.variables),len(pcfg.binary_rules),len(pcfg.preterminal_rules)))

# STEP 4, parsing the test set with CKY
print("\n######## PARSING TEST SET (CKY) ########")

mean_perc = []

for i,tree_repr in enumerate(test_set):
    #tree_repr = "( (SENT (NP-SUJ (DET La) (NC pose) (PP (P d') (NP (DET un) (NC panneau) (NC stop)))) (VN (V paraît)) (VPinf-ATS (VN (VINF être)) (NP-OBJ (DET la) (NC formule) (NP (DET la) (ADV mieux) (ADJ adaptée) (VPinf-MOD (P pour) (VN (VINF assurer)) (NP-OBJ (DET la) (NC sécurité) (PP (P+D des) (NP (NC usagers)))))))) (PONCT .)))"
    print("\n######## RUNNING CKY ON TEST EXAMPLE {}/{} ########".format(i+1,len(test_set)))
    print()
    t = tree(repr_to_root(tree_repr,label_filter=remove_functional))
    sentence = t.get_sentence().split()
    print("INPUT SENTENCE:")
    print(t.get_sentence())
    print()
    # CKY outputs CNF repr which corresponds to binary tree
    computed_repr_CNF = pcfg.CKY(sentence)
    computed_bin_tree = tree(repr_to_root(computed_repr_CNF))
    
    # we un binzarize it to get the natural repr
    computed_tree = computed_bin_tree.get_un_binarized()[0]
    computed_repr = computed_tree.to_repr()

    print()
    print("COMPUTED PARSE TREE:")
    print(computed_repr)

    print()
    print("GOLDEN STANDARD:")
    print(t.to_repr())

    print()
    print("F1 PRECISION/RECALL, PERCEVAL, METRIC:")

    sc = perceval_metric(t,computed_tree)
    print(sc)
    mean_perc.append(sc)

print("\n######## MEAN PERCEVAL RESULT ########")
print(np.mean(mean_perc))