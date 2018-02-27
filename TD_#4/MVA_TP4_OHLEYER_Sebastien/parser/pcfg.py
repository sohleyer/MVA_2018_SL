import tqdm
import numpy as np

class PCFG:
    def __init__(self):
        self.variables = {}
        # counting terminals
        self.terminals = {}
        # dict of dicts X -> (Y,Z) for X -> Y Z rules
        self.binary_rules = {}
        # dict of dicts X -> w for X -> w rules
        self.preterminal_rules = {}
        
    def learn_from_bin_forest(self,forest):
        
        for tree in tqdm.tqdm(forest):
            for node in tree.enumerate_nodes():
                if node.isTerminal:
                    if not node.label in self.terminals:
                        self.terminals[node.label] = 0
                    self.terminals[node.label] += 1
                    continue
                if not node.isTerminal:
                    self.variables[node.label] = True
                    
                if not node.isPreTerminal:
                    source  = node.label
                    target = (node.sons[0].label,node.sons[1].label)
                    if not source in self.binary_rules:
                        self.binary_rules[source] = {}
                    if not target in self.binary_rules[source]:
                        self.binary_rules[source][target] = 0
                    self.binary_rules[source][target] += 1
                else:
                    source = node.label
                    target = node.sons[0].label
                    
                    if not source in self.preterminal_rules:
                        self.preterminal_rules[source] = {}
                    if not target in self.preterminal_rules[source]:
                        self.preterminal_rules[source][target] = 0
                    self.preterminal_rules[source][target] += 1
        
        # replace literals that appear only once by <unk>
        for term in self.terminals:
            if self.terminals[term] == 1:
                self.terminals[term] = 0
        
        to_replace = []      
        for source in self.preterminal_rules:
            for target in self.preterminal_rules[source]:
                if self.terminals[target] == 0:
                    to_replace.append((source,target))
                    
        for s,t in to_replace:
            del self.preterminal_rules[s][t]
            if not '<unk>' in self.preterminal_rules[s]:
                self.preterminal_rules[s]['<unk>'] = 0
            self.preterminal_rules[s]['<unk>'] += 1

        # Normalize:
        for source in self.binary_rules:
            for target in self.binary_rules[source]:
                self.binary_rules[source][target] /= len(self.binary_rules[source])
        for source in self.preterminal_rules:
            s = sum(self.preterminal_rules[source].values())
            for target in self.preterminal_rules[source]:
                self.preterminal_rules[source][target] /= s
    
    def CKY(self,sentence):
        N = len(sentence)
        pi = {}
        bp = {}
        
        for i in range(N):
            terminal = sentence[i]
            if not terminal in self.terminals or self.terminals[terminal] == 0:
                terminal = '<unk>'
            for X in self.variables:
                pi[i,i,X] = 0
                if X in self.preterminal_rules and terminal in self.preterminal_rules[X]:
                    pi[i,i,X] = self.preterminal_rules[X][terminal]
        
        
        for l in tqdm.tqdm(range(N-1)):
            for i in range(N-l-1):
                j = i+l+1
                for X_0 in self.binary_rules:
                    max_score = None
                    best_rule = None
                    best_cut = 0
                    
                    for s in range(i,j):
                        for Y,Z in self.binary_rules[X_0]:
                            q_val = self.binary_rules[X_0][Y,Z]

                            if not (i,s,Y) in pi:
                                pi[i,s,Y] = 0
                            if not (s+1,j,Z) in pi:
                                pi[s+1,j,Z] = 0
                                
                            v1 = pi[i,s,Y]
                            v2 = pi[s+1,j,Z]
                            # log trick not to multiply probs
                            curr_score = np.log(q_val)+np.log(v1)+np.log(v2)
                            if max_score == None or curr_score > max_score:
                                max_score = curr_score
                                best_rule = X,Y,Z
                                best_cut = s
                    
                    pi[i,j,X_0] = np.exp(max_score)
                    bp[i,j,X_0] = (best_rule,best_cut)
        return self.get_tree_after_CKY(bp,sentence,0,N-1,'SENT')
    
    def get_tree_after_CKY(self,bp,sentence,i,j,X):
        
        if i == j:
            expr = "("+X+" "+sentence[i] + ")"
            return expr
        
        rule, cut = bp[i,j,X]
        Y,Z = rule[1:]
        left_child = self.get_tree_after_CKY(bp,sentence,i,cut,Y)
        right_child = self.get_tree_after_CKY(bp,sentence,cut+1,j,Z)
        expr = "(" + X + " " + left_child + " " + right_child + ")"
        
        return expr