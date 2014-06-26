from being import groupMerge, countTypes, matchTypeAndHasFields
from load import loadData
from norvig import correctSentence
from pprint import pprint
from save import steralize, save, project
from text import mineNames

def main():
    print("Loading universe...")
    universe = loadData()
    model = {k : float("inf") for k in ["corporation","company","corporations",
                                        "associates","association","associated",
                                        "companies","incorporated","associations"]}

    def mnf(f):
        return lambda v: mineNames(correctSentence(model,v[f]))

    groupMerge(universe,
               matchTypeAndHasFields("client",["name"]),               
               mnf("name"),
               description="Merged clients based on *corrected* name")
        
    groupMerge(universe,
               matchTypeAndHasFields("firm",["orgname"]),
               mnf("orgname"),
               description="Merging firms based on *corrected* orgname")

    groupMerge(universe,
               matchTypeAndHasFields("firm",["printedname"]),
               mnf("printedname"),               
               description="Merging firms based on *corrected* printedname")    
    
    project(universe,"clientnames.txt",
            lambda v: v["type"] == "client",
            lambda v: v["name"])
    
if __name__ == "__main__":
    main()
    
