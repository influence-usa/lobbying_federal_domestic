import codecs
import networkx as nx
import re

def steralize(universe):
    for k1,k2,v in universe.edges(data=True):
        if "alis" in v:
            v["alis"] = ", ".join(list(v["alis"]))
            
    for k,v in universe.nodes(data=True):            
        if "names" in v:
            v["names"] = ", ".join(sorted(list(v["names"])))            


def save(universe):
    stamp = re.sub("[ :\.]","-",str(datetime.datetime.now()))[:-7]
    f  = codecs.open("output-{}.graphml".format(stamp),"w",encoding="utf-8")
    fn = codecs.open("fresh-output.graphml","w",encoding="utf-8")
    nx.write_graphml(universe,f)
    nx.write_graphml(universe,fn)    
    print("Saved in {}".format(f))

                        
def project(universe,fo,pred,extract):
    beings = filter(lambda x: x[1]["type"] == "Being", universe.nodes(data=True))
    lst = []
    for b in beings:
        ns = nx.neighbors(universe,b[0])
        if pred(universe.node[ns[0]]):
            fs = list(set(map(lambda x: extract(universe.node[x]), ns)))
            fs = sorted(fs)
            lst.append(fs)

    print("Writing {} with {} groups".format(fo,len(lst)))
    with codecs.open(fo,"w",encoding="utf-8") as f:        
        for b in sorted(lst,key=lambda x:x[0].lower()):
            for el in b:
                f.write(el)
                f.write('\n')
            f.write('\n')
            f.write('\n')
    
