#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, os, pickle, sys
import dedupe.serializer as serializer

def print_member(m):
    print("{}".format(m["exact_name"]))
    print("{}".format(m["description"]))
    if m["country"] != "usa":
        print("{}, {}, {}, {}".format(m["address"],m["city"],m["state"],m["zip"],m["country"]))
    else:
        print("{}, {}, {}".format(m["address"],m["city"],m["state"],m["zip"]))
    alis=reduce(lambda x,y : str(x)+","+str(y),m["alis"],"")[1:] 
    print("{}".format(alis))
    print("{}".format(m["specific_issues"]))
    print("{}/{}".format(m["houseID"],m["senate"]))    
    print("\n")

def asker():
    arg = sys.argv[1]
    p = pickle.load(open(arg))

    match = []
    distinct = []
    for group in p:
        if len(group) < 6:
            os.system("clear")
            map(print_member,group)
            print("Are these all part of the same group?(y)es/(s)ome same, some not/(n)o/(u)nsure")
            answer = raw_input()
            if answer == "y":
                for i in range(0,len(group)):
                    for j in range(i+1,len(group)):
                        match.append((group[i],group[j]))
            elif answer == "n" and len(group) == 2:
                distinct.append(tuple(group))
            elif answer == "n":
                for i in range(0,len(group)):
                    for j in range(i+1,len(group)):
                        distinct.append((group[i],group[j]))            
            elif answer == "s":
                for i in range(0,len(group)):
                    for j in range(i+1,len(group)):
                        im = group[i]
                        jm = group[j]
                        os.system("clear")
                        print_member(im)
                        print_member(jm)                    
                        print("Are these the same records?(y)es/(n)o/(u)nsure")
                        answer = raw_input()
                        if   answer == "y":
                            match.append((im,jm))
                        elif answer == "n":
                            distinct.append((im,jm))                        
            json.dump({"distinct": distinct, "match": match},
                      open("asked.json","w"),
                      default=serializer._to_json,
                      indent=4,
                      sort_keys=True)
        
if __name__ == "__main__":
    asker()


    
