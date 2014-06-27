from being import groupMerge, countTypes, matchTypeAndHasFields
from load import loadData
from norvig import correctSentence
from pprint import pprint
from save import steralize, save, project
from text import extractNames

def main():
    print("Loading universe...")
    universe = loadData()
    model = {k : float("inf") for k in ["corporation","company","corporations",
                                        "associates","association","associated",
                                        "companies","incorporated","associations",
                                        "national","china","rational"]}

    def mnf(f):
        return lambda v: extractNames(correctSentence(model,v[f].lower()))

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
    
    #Spell checking names is slow, makes some mistakes without a full
    #list of words and only resolves ~32 entities. Not worth the time
    #at the moment.
    
    # groupMerge(universe,
    #            matchTypeAndHasFields("client",["name"]),               
    #            mnf("name"),
    #            description="Merged clients based on extracted, cleaned and *corrected* name")
        
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
    
