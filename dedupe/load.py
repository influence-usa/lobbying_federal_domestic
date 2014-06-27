import codecs
import copy
import json
from glob   import glob
import networkx as nx
import os
import pickle
import uuid

from text import preProcess
from being import being, represents

processed_files = 'processed_files'

def carefulDict(jOb,d,props):
    for k,kvs in props:
        v = jOb
        found = True
        for vs in kvs:
            if vs in v:
                v = v[vs]
            else:
                found = False
                break
        if found:
            d[k] = preProcess(v)

def loadForm(f,t):
    t = str(t)
    jOb = {}
    corruption = "{http://www.PureEdge.com/XFDL/Custom}"    
    try:
        fo = codecs.open(f,"r",encoding="utf-8")
        jOb = json.loads(fo.read())[u'LOBBYINGDISCLOSURE{}'.format(t)]
    except KeyError:
        try:
            corruptedjOb = json.loads(open(f).read())[corruption+u'LOBBYINGDISCLOSURE{}'.format(t)]
            jOb = {}
            for (k,v) in corruptedjOb.iteritems():
                jOb[k.split(corruption)[-1]]=v
        except KeyError:
            return None

    client = {        
        #Type
        "type":"client",
        "filename": f
    }

    #PRINCIPAL might be a way of getting around the brokers     
    carefulDict(
        jOb,client,
        [("name",["clientName"]),         
         ("address",["updates","clientAddress"]),
         ("city",   ["updates","clientCity"]),
         ("country",["updates","clientCountry"]),
         ("state",  ["updates","clientState"]),
         ("zip",    ["updates","clientZip"]),        
         ("address",["clientAddress"]),
         ("city",   ["clientCity"]),
         ("country",["clientCountry"]),
         ("state",  ["clientState"]),
         ("zip",    ["clientZip"]),
         ("description", ["clientGeneralDescription"]),
         ("specific_issuse", ["specific_issuse"])])
            

    firm = {
        #Type
        "type":"firm",
        "filename": f
    }
    
    carefulDict(
        jOb,firm,
        [("firstname",   ["firstName"]),
         ("lastname",    ["lastName"]),
         ("orgname",     ["organizationName"]),
         ("printedname", ["printedName"]),        
         ("address1",    ["address1"]),
         ("address2",    ["address2"]),        
         ("city",        ["city"]),
         ("country",     ["country"]),
         ("state",       ["state"]),
         ("zip",         ["zip"]),
         ("p_city",      ["principal_city"]),
         ("p_country",   ["principal_country"]),
         ("p_state",     ["principal_state"]),
         ("p_zip",       ["principal_zip"])])
    
    #Relationship
    #"houseID", "senateID", "specific_issues","alis"
    employs = {
        #actual data
        "relation": "employs",
        "houseID":     preProcess(jOb["houseID"]),
        "senate":      preProcess(jOb["senateID"]),
    }
    return (client, firm, employs)

def loadData():
    universe = nx.Graph()
    data = None
    if os.path.exists(processed_files):
        print ("Processed files have been saved, reading those instead")
        with open(processed_files,"r") as f:
            data = pickle.load(f)
    else:
        print("Loading and processing files now")
        data  = map(lambda x: loadForm(x,1),glob(os.environ["HOUSEXML"]+"/LD1/*/*/*.json")[0:10])
        data += map(lambda x: loadForm(x,2),glob(os.environ["HOUSEXML"]+"/LD2/*/*/*.json")[0:10])        
        
        print "Saving processed files"
        with open(processed_files,"w") as f:
            pickle.dump(data,f,2)
        
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
    return universe
