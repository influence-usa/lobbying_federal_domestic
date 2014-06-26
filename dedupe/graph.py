import codecs
from collections import defaultdict
import copy
import datetime
from glob   import glob
import networkx as nx
import norvig
import itertools
import json
import os
import pickle
from pprint import pprint
import re
import subprocess
import time
import uuid

processed_files = 'processed_files'

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
    org = s
    s = s.encode("ascii","ignore")    
    s = re.sub('\n', ' ', s)
    s = s.strip().strip('"').strip("'").lower().strip()
    s = replaceWhitespace(s)
    if s == 'legi\\x company': #LEGI\X is ridiclous 
        s = "legi-x company"        
    return s

useless = ["l l c","llc", "l c","lc", "l l p","llp", "l p","lp", "pllc",
           "pllp",
           "incorperated", "ltd","l t d","company",
           "corporations",
           "corps",
           "corporation","corp","companies","incorporated","inc"] 

#processClientName(preProcess("assn of J.H.Christ & The-All-Mighty l c llc lp"))
#'asociation of j h christ and the all mighty'
# preprocess ("aia") out
def processClientName(org):
    #convert a.b.c.d. to abcd
    s = org
    if "city" not in s:
        s = re.sub("\\bco\\b"," ",s)    
    s = re.sub('\?','\'',s)       #replace ? with '            
    s = re.sub('[,\.]',' ',s)    #replace ,. with space
    s = re.sub('\\bu s a\\b','usa',s) #replace u.s.a. with usa
    s = re.sub('\\bu s\\b','us',s) #replace u.s.a. with usa
    s = re.sub('\\bu s\\b','na',s) #replace n a with na        
    s = re.sub('\\bassn\\b','asociation',s) # replace "assn" with "association"
    s = re.sub('&',' and ',s)#replace "&" with " and "
        
    #remove various stopwords
    for sub in useless:
        s=re.sub("\\b"+sub+"\\b"," ",s) #TODO: look into "co" company vs. colorado

        # reverse chicago, city of
    #on behalf of cassidy & associates
    #on behalf of akin gump
    #"on behalf of akin gump strauss hauer & feld"
    breakers = ["on behalf of", "obo","o/b/o", "on behalf",
                "public policy partners",
                "the livingston group",                                                
                "akin gump strauss hauer and feld"
                "\(the livingston group\)",                                                
                "the livingston group",
                "van scoyoc associates",
                "the implementation group",
                "jefferson consulting group",                
                "alcalde and fay",
                "govbiz advantage"]
    s = preProcess(s)
    for b in breakers:
        if b in s and len(s) > len(b) + 4:
            s = re.split("\\b"+b+"\\b",s)[-1]

    old = None
    while old != s:
        s=preProcess(s)
        if s=='':
            return ''
        old = s
        if s[0] == "(" and s[-1] == ")":
            s = s[1:-1]

        for c in ["-",")",":","/","for\\b","client"]:            
            while c == s[0:len(c)]:
                s = s[len(c):]
                if s=='':
                    return ''

        for c in ["(",":","/"]:
            while c == s[-len(c)]:
                s = s[:-len(c)]
                if s=='':
                    return ''

        while ")" == s[-1] and "(" not in s:
            s = s[:-1]
            
        while "(" == s[-1] and ")" not in s:
            s = s[:-1]
            
        
    #remove acronyms
    #greater richmond transit company (grtc) ==> greater richmond transit (grtc)
    #housing action resource trust (hart) ==> housing action resource trust
    #ousing action resource trust ("hart")

    g = re.match(r"([\w' ]*)\((.*)\)$",s)
    mappings = {
        "and":["a",""],
        "for":["f",""],
        "in":["i",""],                
        "southwest":["s","sw"]
    }
    if g is not None:
        gs = g.groups()
        ws = []
        for w in filter(lambda x: x != "",gs[0].split(" ")):
            if w in mappings:
                ws.append(mappings[w])
            else:
                ws.append([w[0]])
        words = map("".join,list(itertools.product(*ws)))
        if gs[1] in words:
            s = preProcess(gs[0])
            
    s = re.sub('-',' ',s)
    
    return preProcess(s)


    
def loadFile(f):
    jOb = {}
    corruption = "{http://www.PureEdge.com/XFDL/Custom}"    
    try:
        fo = codecs.open(f,"r",encoding="utf-8")
        jOb = json.loads(fo.read())[u'LOBBYINGDISCLOSURE1']
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
        "p_zip":         preProcess(jOb["principal_zip"]),
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
    data = None
    if os.path.exists(processed_files):
        print ("File %s exists reading now" % processed_files)
        with open(processed_files,"r") as f:
            data = pickle.load(f)
    else:
        print("Loading and processing files now")
        data = map(loadFile,glob(os.environ["HOUSEXML"]+"/LD1/*/*/*.json"))
        print "Saving processed files"
        with open(processed_files,"w") as f:
            pickle.dump(data,f,2)
        
    print(len(data))
    text = ""
    for col in data:
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
        text += " "+client["name"]
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
    if "\"fka\"" in name: # The " mess up the word boundaries 
        return re.split("\"fka\"",name)
    
    splitters = ["fka:","fka","f/k/a","f/k/a/",
                 "formerly known as",
                 "formerly know as",
                 "formerly filed as",
                 "formerly reported as",                                  
                 "formerly",
                 "formally known as",
                 "also known as",                                  
                 "formally", 
                 "former", #united natural products alliance (former utah natural products alliance)?
                 "d/b/a",
                 "dba",
    ]#todo: compile regex ahead of times
    for s in splitters:
        if s in name and name != "dba international":
            return re.split("\\b"+s+"\\b",name)
    return [name]

def mineNames(s):
    return filter(lambda x: x !="", map(processClientName,formerSplitter(s)))

def mergeEasyMatches(universe):
    nodes = universe.nodes(data=True)
    l = len(nodes)
    
    firmsOrg = defaultdict(list)
#    firmsPrinted = defaultdict(list)    
    clients = defaultdict(list)    
    
    for k,v in nodes:
        if v["type"] == "client":
            if v["name"] != "":
                for split in mineNames(v["name"]):
                    clients[split].append(k)
        if v["type"] == "firm":
            if v["orgname"] != "":
                for split in mineNames(v["orgname"]):
                    firmsOrg[split].append(k)
            # if v["printedname"] != "":                
            #     firmsPrinted[v["printedname"]].append(k)

    for grouping in [firmsOrg,clients]:
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
            
def mergeFancyMatches(universe):
    nodes = universe.nodes(data=True)
    l = len(nodes)
    
    beings = filter(lambda x: x[1]["type"] == "Being", universe.nodes(data=True))
    text = ""
    for b in beings:
        if "names" in b[1]:
            s = " ".join(b[1]["names"])
            text += " " + s
    print("Training norvig!")
    m = sorted(norvig.train(text).iteritems(),key=lambda x:-x[1])
    m = filter(lambda x: len(x[0]) > 4, m)
    m = sorted(map(lambda x: x[0],m)[0:10])
    print("Ignoring norvig!")
    model = {k : float("inf") for k in ["corporation","company","corporations",
                                        "associates","association","associated",
                                        "companies","incorporated","associations"
                                    ]}
    # for s in useless:
    #     if " " not in s:
    #         model[s] = float("inf")
    firmsOrg = defaultdict(list)
#    firmsPrinted = defaultdict(list)    
    clients = defaultdict(list)    

    for k,v in nodes:
        if v["type"] == "client":
            if v["name"] != "":
                for split in mineNames(norvig.correctSentence(model,v["name"])):
                    clients[split].append(k)
        if v["type"] == "firm":
            if v["orgname"] != "":
                for split in mineNames(norvig.correctSentence(model,v["orgname"])):
                    firmsOrg[split].append(k)
            # if v["printedname"] != "":                
            #     firmsPrinted[v["printedname"]].append(k)

    for grouping in [firmsOrg,clients]:
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
    beings = filter(lambda x: x[1]["type"] == "Being", universe.nodes(data=True))
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


def main():
    print("Loading universe")
    universe = loadData()
    print("Matching universe the easy way")
    mergeEasyMatches(universe)
    print("Matching universe the *fancy* way")    
    mergeFancyMatches(universe)
    print("Steralizing universe")        
    steralize(universe)
    print("Projecting universe")    
    project(universe)


 
if __name__ == "__main__":
    main()
    
