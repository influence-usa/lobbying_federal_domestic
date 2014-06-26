from collections import defaultdict
import copy
import datetime
import networkx as nx
import norvig
import itertools
import re

from load import loadData
from text import preProcess
from save import steralize, save, project
from being import mergeTheirBeings, findBeing, groupMerge

#Questions
#alliance of/ alliance to?
#how to handle formely?
#center for/to'
#city of
#ad hoc informal coalitions

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

    groupMerge(universe,
               lambda v: v["type"] == "client" and v["name"] != "",
               lambda v: mineNames(v["name"]))

    groupMerge(universe,
               lambda v: v["type"] == "firm" and v["orgname"] != "",
               lambda v: mineNames(v["orgname"]))

    groupMerge(universe,
               lambda v: v["type"] == "firm" and v["printedname"] != "",
               lambda v: mineNames(v["printedname"]))
            
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
    
