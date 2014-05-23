import collections, csv, dedupe, json, name_cleaver, os, re, uuid
from numpy  import nan
from pprint import pprint
from glob   import glob

settings_file = 'learned_settings'
training_file = 'trained.json'

def sameOrNotComparator(field_1, field_2) :
    if field_1 and field_2 :
        if field_1 == field_2 :
            return 1
        else:
            return 0
    else :
        return nan

def preProcess(column):
    """
    Do a little bit of data cleaning with the help of
    [AsciiDammit](https://github.com/tnajdek/ASCII--Dammit) and
    Regex. Things like casing, extra spaces, quotes and new lines can
    be ignored.
    """

    column = column.encode("ascii","replace")
    column = dedupe.asciiDammit(column)
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    return column

def processName(str):
    ImmaLetYouFinish = ["on behalf of","livingston group","livingston group, llc (for",
                        "capitol strategies, llc ",  "alcalde & fay","white house consulting",
                        "the ickes and enright group"]
    #if length > 3 then change string otherwise don't
    for s in ImmaLetYouFinish:
        if s in str:
            a = str.split(s)[-1]
            if len(a) > 2:
                str = a

    #St. Joesph's
    #national x asscn
    
    #remove stray end )?
    #strip out
    #informal coalitions
    #llc
    #city of
    #tribal reservations
    #obo - on behalf of
    #fka - formerly known as
    #through
    #prev. rptd - previously reported
    return str

def loadData():
    print 'Reading into clients ...'
    corruption = "{http://www.PureEdge.com/XFDL/Custom}"
    clients = {}
    for f in glob(os.environ["HOUSEXML"]+"/LD1/2013/*/*.json"):
        jOb = {}
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
                continue
                
        go = lambda x: preProcess(jOb[x])
        client = {
            "exact_name":        go("clientName"),
            "rough_name":  processName(go("clientName")),            
            "address":     go("clientAddress"),
            "city":        go("clientCity"),
            "country":     go("clientCountry"),
            "state":       go("clientState"),
            "zip":         go("clientZip"),
            
            "alis":        frozenset(filter(lambda x: x != u"",jOb["alis"])),
            
            "houseID":     go("houseID"),
            "senate":      go("senateID"),            

            "description": go("clientGeneralDescription"),
            "specific_issues":      go("specific_issues"),
        }
        clients[uuid.uuid4().hex] = client
    return clients

# Training
def train(clients):
    if os.path.exists(settings_file):
        print 'reading from', settings_file
        return dedupe.StaticDedupe(settings_file)

    else:
        fields = {'address':     {'type': 'String',
                                  'Has Missing': True},
                  'city':        {'type': 'String',
                                  'Has Missing': True},
                  'country':     {'type': 'Custom',
                                  'Has Missing': True,
                                  'comparator': sameOrNotComparator},
                  'description': {'type': 'String',
                                  'Has Missing': True},
                  'specific_issues': {'type': 'String',
                                      'Has Missing': True},                            
                  'exact_name':  {'type': 'Custom',
                                  'comparator': sameOrNotComparator},
                  'rough_name':  {'type': 'String'},                            
                  'state':       {'type': 'Custom',
                                  'Has Missing': True, 
                                  'comparator': sameOrNotComparator},
                  'zip':         {'type': 'Custom',
                                  'Has Missing': True, 
                                  'comparator': sameOrNotComparator},
                  'houseID':     {'type': 'Custom',
                                  'Has Missing': True,
                                  'comparator': sameOrNotComparator},
                  'alis':     {'type': 'Set'}
        }

        # Create a new deduper object and pass our data model to it.
        deduper = dedupe.Dedupe(fields)

        # To train dedupe, we feed it a random sample of records.
        deduper.sample(clients, 150000)


        # If we have training data saved from a previous run of dedupe,
        # look for it an load it in.
        # __Note:__ if you want to train from scratch, delete the training_file
        if os.path.exists(training_file):
            print 'reading labeled examples from ', training_file
            deduper.readTraining(training_file)

        # ## Active learning
        # Dedupe will find the next pair of records
        # it is least certain about and ask you to label them as duplicates
        # or not.
        # use 'y', 'n' and 'u' keys to flag duplicates
        # press 'f' when you are finished
        print 'starting active labeling...'

        dedupe.consoleLabel(deduper)

        deduper.train()

        # When finished, save our training away to disk
        deduper.writeTraining(training_file)

        # Save our weights and predicates to disk.  If the settings file
        # exists, we will skip all the training and learning next time we run
        # this file.
        deduper.writeSettings(settings_file)
        return deduper

def cluster(deduper):
    # ## Clustering

    # Find the threshold that will maximize a weighted average of our precision and recall. 
    # When we set the recall weight to 2, we are saying we care twice as much
    # about recall as we do precision.
    #
    # If we had more data, we would not pass in all the blocked data into
    # this function but a representative sample.

    threshold = deduper.threshold(clients, recall_weight=2)

    # `match` will return sets of record IDs that dedupe
    # believes are all referring to the same entity.
    print 'clustering...'
    return deduper.match(clients, threshold)
     
if __name__ == "__main__":
    clients = loadData()
    deduper = train(clients)
    clustered_dupes = cluster(deduper)

    print '# duplicate sets', len(clustered_dupes)
    # ## Writing Results

    # Write our original data back out to a CSV with a new column called 
    # 'Cluster ID' which indicates which records refer to each other.    

    for (cluster_id, cluster) in enumerate(clustered_dupes):
        print("Group {}".format(cluster_id))
        for uuid in cluster:
            pprint(clients[uuid])
        print("\n")


