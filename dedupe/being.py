import copy
from networkx import nx

being  = {"label": "Being", "shape":"rectangle", "type": "Being"}
represents = {"label":"represents", "relation":"represents"}

def findBeing(universe,l):
    beings = []
    for lb,d in universe[l].iteritems():
        if d["relation"] == "represents":
            beings.append(lb)
            
    if len(beings) == 0:
        raise Exception("Cannot find a being for \"{}\"".format(l))
    elif len(beings) == 1:
        return beings[0]
    else:
        raise Exception("Found {} beings for {}: {}".format(len(beings),l,",".join(beings)))

def mergeTheirBeings(universe,al,bl):
    a = findBeing(universe,al)
    b = findBeing(universe,bl)        
    if a != b:
        for v in nx.neighbors(universe,b):
            universe.add_edge(v,a,copy.copy(represents))
            universe.remove_edge(v,b)
        av = universe.node[a]
        bv = universe.node[b]        
        if "names" in av and "names" in bv:    
            av["names"] = av["names"].union(bv["names"])
        elif "names" not in av and "names" in bv:    
            av["names"] = bv["names"]            
    return al


#def groupMerge(universe, pred, split, process):

