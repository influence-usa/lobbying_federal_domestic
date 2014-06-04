#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, pickle, sys
import simplejson as json
import dedupe.serializer as serializer

def merger():
    def load(filename):
        return json.load(open(filename,"r"),
                         cls=serializer.dedupe_decoder)
    input1 = load(sys.argv[1])
    input2 = load(sys.argv[2])
    output = open(sys.argv[3],"w")
    outdict = {"distinct": input1["distinct"]+input2["distinct"],
               "match":    input1["match"]+input2["match"]}
    json.dump(outdict,output,default=serializer._to_json)
        
if __name__ == "__main__":
    merger()


    
