import queue as q
from graphviz import Digraph

class node:
    def __init__(self,label,sons,isTerminal=False,isPreTerminal=False):
        self.label = label
        self.sons = sons
        self.isTerminal = isTerminal
        self.isPreTerminal = isPreTerminal
        return
    
class tree:
    def __init__(self,root=node("",[])):
        self.root = root
        return

    def enumerate_nodes(self):
        toVisit = q.Queue()
        toVisit.put(self.root)

        while not toVisit.empty():
            curr_n = toVisit.get()
            yield curr_n

            for son in curr_n.sons:
                toVisit.put(son)

    # requires graphviz
    def draw(self,file_name='parse_tree.gv'):
        dot = Digraph(comment='parse tree',format='png')
        
        # BFS to draw the tree
        toVisit = q.Queue()
        toVisit.put((self.root,-1))
        curr_id = 0
        while not toVisit.empty():
            
            curr_n,parent = toVisit.get()
            my_id = curr_id
            dot.node(str(my_id),curr_n.label)
            curr_id += 1
            if parent != -1:
                dot.edge(str(parent),str(my_id))
            
            for k,son in enumerate(curr_n.sons):
                toVisit.put((son,my_id))
            
        dot.render(file_name)
    
    def aggregate_sons(self,sons):
        '''
            Auxiliary function for get_binarized.
        '''
        if len(sons) == 1:
            return sons[0]
        curr_node = node("@"+".".join([s.label for s in sons]),[])
        curr_node.sons.append(sons[0])
        curr_node.sons.append(self.aggregate_sons(sons[1:]))
        return curr_node
    
    def get_binarized(self):
        '''
            e.g. returns the binarized version of the tree
        '''
        if self.root.isPreTerminal:
            return tree(self.root)
        
        to_return = tree()
        new_root = node(self.root.label,[])
        
        bin_sons = []
        for son in self.root.sons:
            bin_sons.append(tree(son).get_binarized().root)
        new_root.sons.append(bin_sons[0])
        
        if len(bin_sons) == 1:
            aggregate_son = node("@Empty",[node('\<epsilon\>',[],isTerminal=True)],isTerminal=False,isPreTerminal=True)
        elif len(bin_sons) == 2:
            aggregate_son = bin_sons[1]
        else:
            aggregate_son = self.aggregate_sons(bin_sons[1:])
            
        new_root.sons.append(aggregate_son)
        
        return tree(new_root)

    def get_un_binarized(self):
        if self.root.isPreTerminal:
            if self.root.label == "@Empty":
                if self.root.sons[0].label == '\<epsilon\>':
                    return []
                return [tree(self.root.sons[0])]
            return [self]

        if not '@' in self.root.label:
            t = tree(node(self.root.label,[]))
            for s in self.root.sons:
                for ss_t in tree(s).get_un_binarized():
                    t.root.sons.append(ss_t.root)
            return [t]

        to_return = []
        for s in self.root.sons:
            to_return += tree(s).get_un_binarized()

        return to_return

    def to_repr(self):
        if self.root.isTerminal:
            return self.root.label

        s_sons = ""
        for i,s in enumerate(self.root.sons):
            s_sons += tree(s).to_repr()
            if i != len(self.root.sons)-1:
                s_sons += " "

        ex,exb = "",""
        if self.root.label == "SENT":
            ex = "( "
            exb = ")"
        return ex+'('+self.root.label + " " + s_sons + ")"+exb

    def get_sentence(self):
        if self.root.isTerminal:
            return self.root.label

        return " ".join([tree(s).get_sentence() for s in self.root.sons]) 




def get_label(tree_repr, label_filter=lambda x: x):
    '''
        e.g. (VN (CLS Elle) (CLR se) (V veut)) --> VN
        assumes input tree isnt terminal (i.e. repr starts with `(` )
    '''
    return label_filter(tree_repr.split(" ")[0][1:])

def get_sub_trees(tree_repr):
    '''
        e.g. (VN (CLS Elle) (CLR se) (V veut))
                yields [(CLS Elle),(CLR se),(V veut)]
             (CLS Elle)
                yields [Elle]
    '''
    if tree_repr.count('(') == 1:
        yield tree_repr.split(" ")[1][:-1]
    
    count_par = 0
    args = []
    inside = False
    for i,x in enumerate(tree_repr[1:]):
        if x == '(':
            count_par += 1
        if x == ')':
            count_par -= 1
            
        if count_par == 1 and not inside:
            args.append([i+1])
            inside = True
        if count_par == 0 and inside:
            args[-1].append(i+1)
            inside = False
            yield tree_repr[args[-1][0]:args[-1][1]+1]
    
    

#(VN (CLS-SUJ Elle) (CLR se) (V veut))
def repr_to_root(tree_repr,label_filter=(lambda x: x)):
    '''
        e.g. ( (SENT (VN (CLS Elle) (CLR se) (V veut)) (ADV aussi) (NP-OBJ (NC message) (PP (P d') (NP (NC espoir) (PP (P en) (NP (DET l') (NC avenir)))))) (PONCT ") (PONCT .)))
    '''
    if tree_repr[0] == '(' and tree_repr[1] == ' ':
        return repr_to_root(tree_repr[2:-1],label_filter)
        
    if tree_repr[0] != '(':
        return node(tree_repr,[],True)
        
    curr_node = node(get_label(tree_repr,label_filter),[])
    sons = []
    for sub_tree_repr in get_sub_trees(tree_repr):
        sons.append(repr_to_root(sub_tree_repr,label_filter))
    
    if len(sons) == 1 and sons[0].isTerminal:
        curr_node.isPreTerminal = True
    curr_node.sons = sons
    return curr_node

def perceval_metric(gold,t):
    precision = 0
    recall = 0

    sub_sent_gold = {}
    g_n = 0
    for n in gold.enumerate_nodes():
        g_n += 1
        ss = tree(n).get_sentence()

        if not ss in sub_sent_gold:
            sub_sent_gold[ss] = 0
        sub_sent_gold[ss] += 1

    t_n = 0
    for n in t.enumerate_nodes():
        t_n += 1
        ss = tree(n).get_sentence()

        if ss in sub_sent_gold:
            if sub_sent_gold[ss] != 0:
                precision += 1
                sub_sent_gold[ss] -= 1

    recall = precision
    recall /= g_n
    precision /= t_n

    return 2*(precision*recall)/(precision+recall)
