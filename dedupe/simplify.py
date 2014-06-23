from collections import defaultdict
from glob   import glob
import networkx as nx
import json
import os
from pprint import pprint
import re
import subprocess
import sys
import time
import uuid


def main():    
    universe = nx.read_graphml(sys.argv[1])
    
    beings = filter(lambda x: x[1]["type"] == "Being", universe.nodes(data=True))
    clients = filter(lambda x: x[1]["type"] == "client", universe.nodes(data=True))
    firm = filter(lambda x: x[1]["type"] == "firm", universe.nodes(data=True))        
    print len(beings)
    print len(clients)
    print len(firm)
    
    for b in beings:
        ns = nx.neighbors(universe,b[0])
        rep = ns[0]
        for n in ns[1:]:
            for nn in nx.neighbors(universe,n):
                universe.add_edge(rep,nn) #doesn't preserve directions or properties, yolo
            universe.remove_node(n)
        universe.remove_node(b[0])
        
    beings = filter(lambda x: x[1]["type"] == "Being", universe.nodes(data=True))
    clients = filter(lambda x: x[1]["type"] == "client", universe.nodes(data=True))
    firm = filter(lambda x: x[1]["type"] == "firm", universe.nodes(data=True))        
    print len(beings)
    print len(clients)
    print len(firm)
            
    nx.write_graphml(universe,"simplified-{}.graphml".format(int(time.time())))
if __name__ == "__main__":
    main()
