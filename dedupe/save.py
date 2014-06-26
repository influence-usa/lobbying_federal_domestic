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

                        
def project(universe):
    beings = filter(lambda x: x[1]["type"] == "Being", universe.nodes(data=True))x
    clients ={}
    firms = {}
    for b in beings:
        ns = nx.neighbors(universe,b[0])
        if universe.node[ns[0]]["type"] == "client":
            n = universe.node[b[0]]["names"]
            clients[n] = set(map(lambda x: universe.node[x]["name"], ns))
        if universe.node[ns[0]]["type"] == "firm":
            if len(ns) != 1:            
                n = universe.node[b[0]]["names"]
                firms[n] = set(map(lambda x: universe.node[x]["orgname"], ns))


    print("Found {} unique clients".format(len(clients)))
    print("Found {} unique firms".format(len(firms)))    
            
    print("Writing clientnames.txt")
    with open("clientnames.txt","w") as f:        
        for k in sorted(clients.keys()):
            if len(clients[k]) == 1 and list(clients[k])[0] == k:
                f.write(list(clients[k])[0])
            elif len(clients[k]) == 1 and list(clients[k])[0] != k:
                f.write(list(clients[k])[0]+" ==> "+k)            
            else:
                f.write(k)
                f.write('\n')
                f.write("%%%%%%%%%%%%%%%%%%%%")
                f.write('\n')
                for n in clients[k]:
                    f.write(n)
                    f.write('\n')
            f.write('\n')
            f.write('\n')            

    print("Writing firmnames.txt")
    with open("firmnames.txt","w") as f:        
        for k in sorted(firms.keys()):
            if len(firms[k]) == 1 and list(firms[k])[0] == k:
                f.write(list(firms[k])[0])
            elif len(firms[k]) == 1 and list(firms[k])[0] != k:
                f.write(list(firms[k])[0]+" ==> "+k)            
            else:
                f.write(k)
                f.write('\n')
                f.write("%%%%%%%%%%%%%%%%%%%%")
                f.write('\n')
                for n in firms[k]:
                    f.write(n)
                    f.write('\n')
            f.write('\n')
            f.write('\n')            

    
