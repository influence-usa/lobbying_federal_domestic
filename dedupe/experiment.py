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
    d ={}
    i=0
    for b in beings:
        ns = nx.neighbors(universe,b[0])
        if universe.node[ns[0]]["type"] == "client":
            if "names" in universe.node[b[0]]:
                n = universe.node[b[0]]["names"]
                d[n] = set(map(lambda x: universe.node[x]["name"], ns))
            else:                
                d["UNCLAIMED-{}".format(i)] = set(map(lambda x: universe.node[x]["name"], ns))
                i = i+1
            
    for k in sorted(d.keys()):
        if len(d[k]) == 1 and list(d[k])[0] == k:
            print(list(d[k])[0])
        elif len(d[k]) == 1 and list(d[k])[0] != k:
            print(list(d[k])[0]+" ==> "+k)            
        else:
            print(k)
            print("--------------------")
            for n in d[k]:
                print(n)
        print("\n")

if __name__ == "__main__":
    main()
