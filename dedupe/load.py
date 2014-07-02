import codecs
import copy
import json
from glob   import glob
import multiprocessing
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

corruption = "{http://www.PureEdge.com/XFDL/Custom}"

def clean(d):
    nd = {}
    for k,v in d.iteritems():
        nk = k.split(corruption)[-1]
        if type(v) == dict: ##TODO: map over arrays
            v = clean(v)
        nd[nk] = v
    return nd
            
    
def loadForm(f,t):
    t = str(t)
    jOb = {}
    fo = codecs.open(f,"r",encoding="utf-8")
    jOb = json.loads(fo.read())
    if corruption+u'LOBBYINGDISCLOSURE{}'.format(t) in jOb:
        jOb = clean(jOb)

    try:
        jOb = jOb[u'LOBBYINGDISCLOSURE{}'.format(t)]
    except KeyError:
        print("Weird, flipping form number just in case")
        jOb = jOb[u'LOBBYINGDISCLOSURE{}'.format(str(3-int(t)))]        

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

def loadForm1(x):
    return loadForm(x,1)

def loadForm2(x):
    return loadForm(x,2)

def loadData():
    universe = nx.Graph()
    data = None
    if os.path.exists(processed_files):
        print ("Processed files have been saved, reading those instead")
        with open(processed_files,"r") as f:
            data = pickle.load(f)
    else:
        print("Loading and processing files now")
        p = multiprocessing.Pool(8)
        data  = p.map(loadForm1,glob(os.environ["HOUSEXML"]+"/LD1/*/*/*.json"),10)
        data = p.map(loadForm2,glob(os.environ["HOUSEXML"]+"/LD2/*/*/*.json"),10)        
        
        print "Saving processed files"
        with open(processed_files,"w") as f:
            pickle.dump(data,f,2)

    print("Starting from {} records".format(len(data)))
    print("Building universe")
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
    print("Universe loaded and built")        
    return universe
