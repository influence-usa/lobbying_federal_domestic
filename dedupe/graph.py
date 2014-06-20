import copy
from collections import defaultdict
import datetime
from glob   import glob
import networkx as nx
import json
import os
from pprint import pprint
import re
import subprocess
import time
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

#Questions
#alliance of/ alliance to?
#how to handle formely?
#center for/to'
#city of
#d/b/a doing business as 
# if there is a 3-5 letter nonsense verb at the end of a word, remove it?
#ad hoc informal coalitions

def preProcess(s):
    s = s.encode("ascii","replace")
    s = re.sub('\n', ' ', s)
    s = s.strip().strip('"').strip("'").lower().strip()
    return replaceWhitespace(s)

#processClientName(preProcess("assn of J.H.Christ & The-All-Mighty l c llc lp"))
#'asociation of j h christ and the all mighty'
# preprocess ("aia") out
def processClientName(org):
    s = org
    s = re.sub('\?','\'',s)       #replace ? with '            
    s = re.sub('[,\.]',' ',s)    #replace ,. with space
    s = re.sub('\\bu s a\\b','usa',s) #replace u.s.a. with usa
    s = re.sub('\\bu s\\b','us',s) #replace u.s.a. with usa    
    s = re.sub('\\bassn\\b','asociation',s) # replace "assn" with "association"
    s = re.sub('&',' and ',s)#replace "&" with " and "
    if "city" not in s:
        s = re.sub("\bco\b"," ",s)
        
    useless =  ["l l c","llc",
                "l c","lc",
                "l l p","llp",
                "l p","lp",
                "ltd","l t d","company","corporation","corp","companies","incorporated","inc"] 
    #remove various stopwords
    for sub in useless:
        s=re.sub("\\b"+sub+"\\b"," ",s) #TODO: look into "co" company vs. colorado

        # reverse chicago, city of
    #on behalf of cassidy & associates
    #on behalf of akin gump
    #"on behalf of akin gump strauss hauer & feld"
    breakers = ["on behalf of", "obo","o/b/o", "on behalf",
                "public policy partners (",
                "the livingston group - (client",                                                
                "the livingston group (client:",
                "the livingston group (for ",
                "the livingston group ( for ",                
                "the livingston group (",
                "the livingston group(",
                "the livingston group/",
                "akin gump strauss hauer and feld ("
                "(the livingston group)",                                                
                "the livingston group-",
                "van scoyoc associates (",
                "the implementation group (",
                "jefferson consulting group (",                
                "alcalde and fay (",
                "govbiz advantage (for",
                "govbiz advantage ("                
    ]
    for b in breakers:
        if b in s:
            s = s.split(b)[-1]
    while ")" == s[0]:
        s = s[1:]
    while "(" == s[-1]:
        s = s[:-1]        
    while ")" == s[-1] and "(" not in s:
        s = s[:-1]
    while "(" == s[-1] and ")" not in s:
        s = s[:-1]

        
    #ImmaLetYouFinish = [
    #                     "capitol strategies ",  "alcalde and fay \(","white house consulting",
    #                     "the ickes and enright group","corporation", 
    #                     "dla piper us for", "obo" ]
    #remove "alcalde & fay (" "alenxander strategy group (" "apco worldwide ("    
    # for s in ImmaLetYouFinish:
    #     if s in name:
    #         a = name.split(s)[-1]
    #         if len(a) > 2:
    #             name = replaceWhitespace(a)

    #remove on behalf of
    return preProcess(s)


    
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
        "label": processClientName(preProcess(jOb["clientName"])),
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

        universe.add_node(cbeing,copy.copy(being))
        universe.add_node(cnode,client)
        universe.add_edge(cnode,cbeing,copy.copy(beingr))
        
        universe.add_node(fbeing,copy.copy(being))
        universe.add_node(fnode,firm)
        universe.add_edge(fnode,fbeing,copy.copy(beingr))
        
        universe.add_edge(fnode,cnode,employs)
    return universe

def mergeTheirBeings(universe,al,bl):
    a = findBeing(universe,al)
    b = findBeing(universe,bl)        
    if a != b:
        for v in nx.neighbors(universe,b):
            universe.add_edge(v,a,copy.copy(beingr))
            universe.remove_edge(v,b)
        av = universe.node[a]
        bv = universe.node[b]        
        if "names" in av and "names" in bv:    
            av["names"] = av["names"].union(bv["names"])
        elif "names" not in av and "names" in bv:    
            av["names"] = bv["names"]            
    return al

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

def formerSplitter(name):
    splitters = ["\"fka\"","fka:","fka","f/k/a/",
                 "formerly known as",
                 "formerly know as",
                 "formerly filed as",
                 "formerly reported as",                                  
                 "formerly",
                 "formally known as",                 
                 "formally",
                 "former",
                 "d/b/a",
                 "dba ",
    ]
    for s in splitters:
        if s in name:
            return name.split("\b"+s+"\b")
    return [name]

def mergeExactMatches(universe):
    nodes = universe.nodes(data=True)
    l = len(nodes)
    
    firmsOrg = defaultdict(list)
    firmsPrinted = defaultdict(list)    
    clients = defaultdict(list)    
    
    for k,v in nodes:
        if v["type"] == "client":
            if v["name"] != "":
                for split in map(processClientName,formerSplitter(v["name"])):
                    clients[split].append(k)
        if v["type"] == "firm":
            if v["orgname"] != "":
                firmsOrg[v["orgname"]].append(k)
            if v["printedname"] != "":                
                firmsPrinted[v["printedname"]].append(k)

    for grouping in [firmsOrg,firmsPrinted,clients]:
        for k,v in grouping.iteritems():
            merged = reduce(lambda x,y: mergeTheirBeings(universe,x,y),v)
            found = findBeing(universe,merged)
            if "names" in universe.node[found]:
                universe.node[found]["names"].add(k)
            else:
                universe.node[found]["names"] = set([k])        

    for (k,v) in universe.nodes(data=True):            
        if k in universe and v["type"] == "Being" and len(nx.neighbors(universe,k)) == 0:
            universe.remove_node(k)


def save(universe):
    for k1,k2,v in universe.edges(data=True):
        if "alis" in v:
            v["alis"] = ", ".join(list(v["alis"]))
            
    for k,v in universe.nodes(data=True):            
        if "names" in v:
            v["names"] = ", ".join(sorted(list(v["names"])))            
    stamp = re.sub("[ :\.]","-",str(datetime.datetime.now()))[:-7]
    f = "output-{}.graphml".format(stamp)
    nx.write_graphml(universe,f)
    print("Saved in {}".format(f))

    
def main():
    print("Loading data")
    universe = loadData()
    print("Matching")
    mergeExactMatches(universe)
    print("Saving")
    save(universe)


 
if __name__ == "__main__":
    main()
    
