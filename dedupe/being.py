from collections import defaultdict
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
    return al

def cullHermits(universe):
    for (k,v) in universe.nodes(data=True):            
        if k in universe and v["type"] == "Being" and len(nx.neighbors(universe,k)) == 0:
            universe.remove_node(k)

def countTypes(universe):
    beings = filter(lambda x: x[1]["type"] == "Being", universe.nodes(data=True))
    d = defaultdict(lambda: 1)
    for b in beings:
        ns = nx.neighbors(universe,b[0])
        d[universe.node[ns[0]]["type"]] += 1
    return d
            
def groupMerge(universe, pred, extract,description=None):
    if description != None:
            print(description)        
            start = countTypes(universe)

    nodes = filter(lambda t: pred(t[1]),universe.nodes(data=True))
    d = defaultdict(list)
    for k,v in nodes:
        for s in extract(v):
            d[s].append(k)
    for k,v in d.iteritems():
        merged = reduce(lambda x,y: mergeTheirBeings(universe,x,y),v)
        found = findBeing(universe,merged)
        
    cullHermits(universe)
    if description != None:
            d = countTypes(universe)
            txt = "" 
            for k,v in d.iteritems():
                txt += k + " " + str(v-start[k]) + " "
            print(txt)
            print("")
    
def matchTypeAndHasFields(t,fs):
    return lambda v: v["type"] == t and all([v[f] != "" for f in fs])
    
