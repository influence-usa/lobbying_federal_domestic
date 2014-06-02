import collections, csv, dedupe, json, os, pickle, re, time, uuid
from numpy  import nan
from pprint import pprint
from glob   import glob
import dedupe.serializer as serializer

processed_files = 'processed_files'
settings_file = 'learned_settings'
training_file = 'trained.json'
output_pickle = 'clusters.pickle'
nprocesses = os.environ["NPROCESS"]

def sameOrNotComparator(field_1, field_2) :
    if field_1 and field_2 :
        if field_1 == field_2 :
            return 1
        else:
            return 0
    else :
        return nan

def replaceWhitespace(str):
    return re.sub('  +', ' ', str)

def preProcess(column):
    """
    Do a little bit of data cleaning with the help of
    [AsciiDammit](https://github.com/tnajdek/ASCII--Dammit) and
    Regex. Things like casing, extra spaces, quotes and new lines can
    be ignored.
    """

    column = column.encode("ascii","replace")
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()    
    return replaceWhitespace(column)

def processName(name):
    name = replaceWhitespace(re.sub('[-\.,()]', ' ', name))
    
    Goodbye = {"&": "and",
               "twenty first century": "21st century"}
    for k,v in Goodbye.iteritems():
        if k in name:
            name = re.sub(k,v,name)        
        
    ImmaLetYouFinish = ["on behalf of","livingston group for","livingston group",
                        "capitol strategies ",  "alcalde and fay","white house consulting",
                        "the ickes and enright group","corporation", 
                        "dla piper us for", "obo" ]
    for s in ImmaLetYouFinish:
        if s in name:
            a = name.split(s)[-1]
            if len(a) > 2:
                name = replaceWhitespace(a)

    GetOuttaHere = ["american"," l p","corporation","international","national",
                    "association","incorporated"," l l c", "tribe", " u s "
                    "university of", "coalition", "professional","town of",
                    "group","technologies"," u s a","company","limited",
                    "political action committee","city of","informal coalitions",
                    "associates"    ]
    for s in GetOuttaHere:
        if s in name:
            a = re.sub(s,' ',name)
            if len(a) > 2:
                name = replaceWhitespace(a)

    Shwaties =["llc","inc","corp","llp","of","the"]
    for s in Shwaties:
        if s in name.split():
            a = re.sub(s,' ',name)
            if len(a) > 2:
                name = replaceWhitespace(a)
                
            
    return name
    #St. Joesph's    
    #remove stray end )?
    #strip out
    #tribal reservations
    #fka - formerly known as
    #through
    #prev. rptd - previously reported

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
            # We'll do it live
            return None

    client = {
        "exact_name":  preProcess(jOb["clientName"]),
        "rough_name":  processName(preProcess(jOb["clientName"])),            
        "address":     preProcess(jOb["clientAddress"]),
        "city":        preProcess(jOb["clientCity"]),
        "country":     preProcess(jOb["clientCountry"]),
        "state":       preProcess(jOb["clientState"]),
        "zip":         preProcess(jOb["clientZip"]),
        
        "alis":        frozenset(filter(lambda x: x != u"",jOb["alis"])),
        
        "houseID":     preProcess(jOb["houseID"]),
        "senate":      preProcess(jOb["senateID"]),            
        "filename": f,
        "description":     preProcess(jOb["clientGeneralDescription"]),
        "specific_issues": preProcess(jOb["specific_issues"]),
    }
    return client

    
def loadData():
    print 'Reading into clients ...'    
    if os.path.exists(processed_files):
        print ("File %s exists reading now" % processed_files)
        with open(processed_files,"r") as f:
            return pickle.load(f)
    else:
        print "Loading and processing files now"
        clients = {}
        for c in map(loadFile,glob(os.environ["HOUSEXML"]+"/LD1/*/*/*.json")):
            if c != None:
                clients[uuid.uuid4().hex] = c
        with open(processed_files,"w") as f:
            pickle.dump(clients,f,2)
        return clients

# Training
def train(clients):
    
    if os.path.exists(settings_file):
        print 'reading from', settings_file
        return dedupe.StaticDedupe(settings_file,num_processes=nprocess)

    else:
        fields = {'city':        {'type': 'String', 'Has Missing': True},
                  'country':     {'type': 'String', 'Has Missing': True},
                  'zip':         {'type': 'String', 'Has Missing': True},
                  'houseID':     {'type': 'String', 'Has Missing': True},
                  'state':       {'type': 'String', 'Has Missing': True},                  
                  'address':     {'type': 'Text', 'Has Missing': True,
                                  'corpus': [] #map(lambda x: x['address'],clients.values())
                              },
                  
                  'description': {'type': 'Text', 'Has Missing': True,
                                  'corpus': [] #map(lambda x: x['description'],clients.values())
                              },
                  'specific_issues': {'type': 'Text', 'Has Missing': True,
                                      'corpus': [] #map(lambda x: x['specific_issues'],clients.values())
                                  },
                  'rough_name':  {'type': 'Text',
                                  'corpus': [] #map(lambda x: x['rough_name'],clients.values())
                              },
                  'alis':     {'type': 'Set',
                               'corpus': [] #map(lambda x: x['alis'],clients.values())
                           },

                  'exact_name':  {'type': 'Custom',
                                  'comparator': sameOrNotComparator},
        }
        for k,v in list(fields.iteritems()):
            if k != 'exact_name':
                fields[k+"-exact_name"] = {'type':'Interaction',
                                           'Interaction Fields': ["exact_name", k]}
        # Create a new deduper object and pass our data model to it.
        deduper = dedupe.Dedupe(fields,num_processes=nprocess)

        # To train dedupe, we feed it a random sample of records.
        deduper.sample(clients, 150000)

        
        # If we have training data saved from a previous run of dedupe,
        # look for it an load it in.
        # __Note:__ if you want to train from scratch, delete the training_file
        if os.path.exists(training_file):
            print 'reading labeled examples from ', training_file
            deduper.readTraining(training_file)
            
        for f in ["closenames","exactnames"]:
            labels = json.load(open(f+".json"), cls=serializer.dedupe_decoder)            
            deduper.markPairs(labels)
            
        # ## Active learning
        # Dedupe will find the next pair of records
        # it is least certain about and ask you to label them as duplicates
        # or not.
        # use 'y', 'n' and 'u' keys to flag duplicates
        # press 'f' when you are finished
        print 'starting active labeling...'

        #dedupe.consoleLabel(deduper)

        deduper.train()

        # When finished, save our training away to disk
        deduper.writeTraining(training_file)

        # Save our weights and predicates to disk.  If the settings file
        # exists, we will skip all the training and learning next time we run
        # this file.
        #deduper.writeSettings(settings_file)
        return deduper
    
def main():
    clients = loadData()
    deduper = train(clients)

    print 'threshold...'    
    threshold = deduper.threshold(clients, recall_weight=2)
    print 'matchering...'        
    clustered_dupes = deduper.match(clients, threshold)

    print '# duplicate sets', len(clustered_dupes)
    print '# duplicate sets', map(len,clustered_dupes)    
    # ## Writing Results

    # Write our original data back out to a CSV with a new column called 
    # 'Cluster ID' which indicates which records refer to each other.    

    for (cluster_id, cluster) in enumerate(clustered_dupes):
         print("Group {}".format(cluster_id))
         for uuid in cluster:
             pprint(clients[uuid])
         print("\n")
         
    with open(output_pickle+int(time.time()),"w") as f:
            pickle.dump(clustered_dupes,f,2)
         
if __name__ == "__main__":
    main()

