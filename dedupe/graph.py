from glob   import glob
import networkx as nx
import json
import os
from pprint import pprint
import re
import subprocess
import uuid

#Lobbyists
#"lobbyists"

#afflilatedOrgs
#"affiliatedOrgs"

#foreignEntities
#"foreignEntities"

#Flags
#"selfSelect"

#Unknown
#"prefix","affiliatedUrl"

#Time
#"effectiveDate","regType","reportType","reportYear","signedDate"
    
def replaceWhitespace(s):
    return re.sub('  +', ' ', s)

def preProcess(column):
    column = column.encode("ascii","replace")
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()    
    return replaceWhitespace(column)

def loadFile(f):
    jOb = {}
    corruption = "{http://www.PureEdge.com/XFDL/Custom}"    
    try:
        jOb = json.loads(open(f).read())[u'LOBBYINGDISCLOSURE1']
    except KeyError:
        try:
            corruptedjOb = json.loads(open(f).read())[corruption+u'LOBBYINGDISCLOSURE1']
            jOb = {}
            for (k,v) in corruptedjOb.iteritems():
                jOb[k.split(corruption)[-1]]=v
        except KeyError:
            return None

    #Client node
    #"clientAddress","clientCity","clientCountry","clientGeneralDescription","clientGovtEntity",
    #"clientName","clientState","clientZip","clientZipExt","prinClientCity","prinClientCountry",
    #"prinClientState","prinClientZip","prinClientZipExt"    
    client = {
        #Display data
        "label":       preProcess(jOb["clientName"]),
        "fillcolor": "darkolivegreen1",
        "style": "filled",
        
        #Type
        "type":"client",
        
        #Acutal data
        "name":        preProcess(jOb["clientName"]),
        "address":     preProcess(jOb["clientAddress"]),
        "city":        preProcess(jOb["clientCity"]),
        "country":     preProcess(jOb["clientCountry"]),
        "state":       preProcess(jOb["clientState"]),
        "zip":         preProcess(jOb["clientZip"]),
        
        "filename": f,
        "description":     preProcess(jOb["clientGeneralDescription"]),
        "specific_issues": preProcess(jOb["specific_issues"]),
    }

    #Firm node
    #"address1","address2","city","firstName","lastName","state","zip","zipext","country",
    #"principal_city","principal_country","principal_state","principal_zip","principal_zipext",
    #"organizationName","printedName","registrantGeneralDescription",
    
    firm = {
        #Display code
        "label":     preProcess(jOb["organizationName"]),
        "fillcolor": "deepskyblue",
        "style": "filled",
        #Type
        "type":"firm",

        #Actual data
        "firstname":   preProcess(jOb["firstName"]),
        "lastname":    preProcess(jOb["lastName"]),
        "orgname":     preProcess(jOb["organizationName"]),
        "printedname": preProcess(jOb["printedName"]),
        "description": preProcess(jOb["registrantGeneralDescription"]),                        
        
        "address1":    preProcess(jOb["address1"]),
        "address2":    preProcess(jOb["address2"]),        
        "city":        preProcess(jOb["city"]),
        "country":     preProcess(jOb["country"]),
        "state":       preProcess(jOb["state"]),
        "zip":         preProcess(jOb["zip"]),

        "p_city":        preProcess(jOb["principal_city"]),
        "p_country":     preProcess(jOb["principal_country"]),
        "p_state":       preProcess(jOb["principal_state"]),
        "P_zip":         preProcess(jOb["principal_zip"]),
        "filename": f
    }

    #Relationship
    #"houseID", "senateID", "specific_issues","alis"
    employs = {
        #display code
        "label": "employs",
        #actual data
        "relation": "employs",
        "houseID":     preProcess(jOb["houseID"]),
        "senate":      preProcess(jOb["senateID"]),
        "alis":        frozenset(filter(lambda x: x != u"",jOb["alis"])),        
    }
    return (client, firm, employs)

being  = {"label": "Being", "shape":"rectangle", "type": "Being"}
beingr = {"label":"represents", "relation":"represents"}
    
def loadData():
    print 'Reading into clients ...'    
    universe = nx.Graph()
    for col in map(loadFile,glob(os.environ["HOUSEXML"]+"/LD1/*/*/*.json")):
        if col == None:
            continue
        (client,firm,employs) = col        
        cnode = str(uuid.uuid1())
        fnode = str(uuid.uuid1())
        cbeing = str(uuid.uuid1())
        fbeing = str(uuid.uuid1())        

        universe.add_node(cbeing, being)
        universe.add_node(cnode,client)
        universe.add_edge(cnode,cbeing,beingr)
        
        universe.add_node(fbeing,being)        
        universe.add_node(fnode,firm)
        universe.add_edge(fnode,fbeing,beingr)
        
        universe.add_edge(fnode,cnode,employs)
    return universe

def mergeBeings(universe,a,b):
    for v in nx.neighbors(universe,b):
        universe.add_edge(v,a,beingr)
        universe.remove_edge(v,b)
    return None

def findBeing(l,universe):
    for lb,d in universe[l].iteritems():
        if d["relation"] == "represents":
            return lb
    raise Exception("Cannot find a being for \"{}\"".format(l))

def mergeExactMatches(universe):
    nodes = universe.nodes(data=True)
    l = len(nodes)
    sames = []
    for i in range(0,l):
        for j in range(i,l):
            la, a = nodes[i]
            lb, b = nodes[j]            
            if la != lb:
                if a["type"] == "client" and b["type"] == "client" and a["name"] == b["name"]:
                    sames.append((findBeing(la,universe),findBeing(lb,universe)))                    
                if a["type"] == "firm"   and b["type"] == "firm" and a["printedname"] == b["printedname"] and a["printedname"] != "":
                    sames.append((findBeing(la,universe),findBeing(lb,universe)))                    
                if a["type"] == "firm"   and b["type"] == "firm" and a["orgname"] == b["orgname"] and a["orgname"] != "":
                    sames.append((findBeing(la,universe),findBeing(lb,universe)))
                    
    [mergeBeings(universe,u,v) for u,v in sames]

    for u,v in sames:
        if u in universe and len(nx.neighbors(universe,u)) == 0:
            universe.remove_node(u)
        if v in universe and len(nx.neighbors(universe,v)) == 0:
            universe.remove_node(v)


def save(universe):
    for k1,k2,v in universe.edges(data=True):
        if "alis" in v:
            v["alis"] = ",".join(list(v["alis"]))
    nx.write_graphml(universe,"output.graphml")
    
def main():
    print("Loading data")
    universe = loadData()
    print("Matching")
    mergeExactMatches(universe)
    print("Saving")
    save(universe)


 
if __name__ == "__main__":
    main()
    
