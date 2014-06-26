import codecs
import copy
import json
from glob   import glob
import networkx as nx
import os
import pickle
import uuid

from text import preProcess

processed_files = 'processed_files'
from being import being, represents

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
        #actual data
        "relation": "employs",
        "houseID":     preProcess(jOb["houseID"]),
        "senate":      preProcess(jOb["senateID"]),
        "alis":        frozenset(filter(lambda x: x != u"",jOb["alis"])),        
    }
    return (client, firm, employs)
    
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
        universe.add_edge(cnode,cbeing,copy.copy(represents))
        
        universe.add_node(fbeing,copy.copy(being))
        universe.add_node(fnode,firm)
        universe.add_edge(fnode,fbeing,copy.copy(represents))
        
        universe.add_edge(fnode,cnode,employs)
        text += " "+client["name"]
    return universe
