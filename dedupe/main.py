import collections
import csv
import dedupe
import json
import logging
import optparse
import os
import re
from numpy import nan
from pprint import pprint
from glob import glob
import name_cleaver

settings_file = 'learned_settings'
training_file = 'trained.json'

def pprintm(x):
    pprint(x)
    return x

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
    ImmaLetYouFinish = ["on behalf of","livingston group","alcalde & fay","white house consulting",
                        "the ickes and enright group"]
    #if length > 3 then change string otherwise don't
    for s in ImmaLetYouFinish:
        if s in str:
            a = str.split(s)[-1]
            if len(a) > 2:
                str = a
        
    #remove stray end )?
    #strip out
    #informal coalitions
    #llc
    #tribal reservations
    #obo - on behalf of
    #fka - formerly known as
    #through
    #prev. rptd - previously reported
    return str

def readData():
    corruption = "{http://www.PureEdge.com/XFDL/Custom}"
    clients = {}
    for f in glob(os.environ["HOUSEXML"]+"/LD1/*/*/*.json"):
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
            "houseID":     go("houseID"),
            "alis":        frozenset(filter(lambda x: x != u"",jOb["alis"])),
            "address":     go("clientAddress"),
            "city":        go("clientCity"),
            "country":     go("clientCountry"),
            "description": go("clientGeneralDescription"),
            "name":        processName(go("clientName")),
            "state":       go("clientState"),
            "zip":         go("clientZip"),
        }
        clients[jOb["houseID"]] = client
    return clients

print 'Reading into clients ...'
clients = readData()

# Training

if os.path.exists(settings_file):
    print 'reading from', settings_file
    deduper = dedupe.StaticDedupe(settings_file)

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
              'name':        {'type': 'String'},              
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


# ## Blocking

print 'blocking...'

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
clustered_dupes = deduper.match(clients, threshold)

print '# duplicate sets', len(clustered_dupes)

# ## Writing Results

# Write our original data back out to a CSV with a new column called 
# 'Cluster ID' which indicates which records refer to each other.

#print(clustered_dupes)

cluster_membership = collections.defaultdict(lambda : 'x')

# import sys
# orig_stdout = sys.stdout
# f = open("output.txt","w")
# sys.stdout=f

# for (cluster_id, cluster) in enumerate(clustered_dupes):
#     print("Group {}".format(cluster_id))
#     for record_id in cluster:
#         for k,v in clients.iteritems():
#             if k == record_id:
#                 pprint(k)
#                 pprint(v)

#     print("\n")

# sys.stdout=orig_stdout
# f.close()

# with open(output_file, 'w') as f:
#     writer = csv.writer(f)

#     with open(input_file) as f_input :
#         reader = csv.reader(f_input)

#         heading_row = reader.next()
#         heading_row.insert(0, 'Cluster ID')
#         writer.writerow(heading_row)

#         for row in reader:
#             row_id = int(row[0])
#             cluster_id = cluster_membership[row_id]
#             row.insert(0, cluster_id)
#             writer.writerow(row)

#             ####

