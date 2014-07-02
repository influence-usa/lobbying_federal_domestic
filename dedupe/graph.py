from being import groupMerge, countTypes, matchTypeAndHasFields
from load import loadData
from pprint import pprint
from save import steralize, save, project
from text import extractNames

def main():
    print("Loading universe...")
    universe = loadData()

    groupMerge(universe,
               matchTypeAndHasFields("client",["name"]),               
               lambda v: [v["name"]],
               description="Merged clients based on exact name match")

    groupMerge(universe,
               matchTypeAndHasFields("client",["name"]),               
               lambda v: extractNames(v["name"]),
               description="Merged clients based on extracted and cleaned name match")

    p = matchTypeAndHasFields("client",["address","city","country","state","zip"])
    groupMerge(universe,
               lambda v: p(v) and v["state"] not in ["DC","VA","MD"] and v["city"] != "DC",
               lambda v: [(v["address"],v["city"],v["country"],v["state"],v["zip"])],
               description="Merging clients based on exact matching of address fields (sans DC area)")
            
    # groupMerge(universe,
    #            matchTypeAndHasFields("firm",["orgname"]),
    #            mnf("orgname"),
    #            description="Merging firms based on *corrected* orgname")

    # groupMerge(universe,
    #            matchTypeAndHasFields("firm",["printedname"]),
    #            mnf("printedname"),               
    #            description="Merging firms based on *corrected* printedname")
        
    project(universe,"clientnames.txt",
            lambda v: v["type"] == "client",
            lambda v: ", ".join([v["name"],v["address"],v["city"],v["country"],v["state"],v["zip"]]).lower())

    
if __name__ == "__main__":
    main()
    
