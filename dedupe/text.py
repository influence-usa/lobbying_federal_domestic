import itertools
import re 


def replaceWhitespace(s):
    return re.sub('  +', ' ', s)

def preProcess(s):
    org = s
    s = s.encode("ascii","ignore")    
    s = re.sub('\n', ' ', s)
    s = s.strip().strip('"').strip("'").strip()
    s = replaceWhitespace(s)
    if s == 'legi\\x company': #LEGI\X is ridiclous 
        s = "legi-x company"        
    return s

#Questions
#alliance of/ alliance to?
#how to handle formely?
#center for/to'
#city of
#ad hoc informal coalitions

useless = ["l l c","llc", "l c","lc", "l l p","llp", "l p","lp", "pllc",
           "pllp",
           "incorperated", "ltd","l t d","company",
           "corporations",
           "corps",
           "corporation","corp","companies","incorporated","inc"] 

#processClientName(preProcess("assn of J.H.Christ & The-All-Mighty l c llc lp"))
#'asociation of j h christ and the all mighty'
# preprocess ("aia") out
def processClientName(org):
    #convert a.b.c.d. to abcd
    s = org
    if "city" not in s:
        s = re.sub("\\bco\\b"," ",s)    
    s = re.sub('\?','\'',s)       #replace ? with '            
    s = re.sub('[\',\.]',' ',s)    #replace ,. with space
    s = re.sub('\\bu s a\\b','usa',s) #replace u.s.a. with usa
    s = re.sub('\\bu s\\b','us',s) #replace u.s.a. with usa
    s = re.sub('\\bu s\\b','na',s) #replace n a with na        
    s = re.sub('\\bassn\\b','asociation',s) # replace "assn" with "association"
    s = re.sub('&',' and ',s)#replace "&" with " and "
        
    #remove various stopwords
    for sub in useless:
        s=re.sub("\\b"+sub+"\\b"," ",s) #TODO: look into "co" company vs. colorado

        # reverse chicago, city of
    #on behalf of cassidy & associates
    #on behalf of akin gump
    #"on behalf of akin gump strauss hauer & feld"
    breakers = ["on behalf of", "obo","o/b/o", "on behalf",
                "public policy partners",
                "the livingston group",                                                
                "akin gump strauss hauer and feld"
                "\(the livingston group\)",                                                
                "the livingston group",
                "van scoyoc associates",
                "the implementation group",
                "jefferson consulting group",                
                "alcalde and fay",
                "govbiz advantage",
                "capitol impact",
                "capitol insight",
                "dci group",
                "dci group az",
    ]
    s = preProcess(s)
    for b in breakers:
        if b in s and len(s) > len(b) + 4:
            s = re.split("\\b"+b+"\\b",s)[-1]
    for b in ["(for "]:
        if b in s and len(s) > len(b) + 4:
            s = re.split(re.escape(b),s)[-1]

            
    old = None
    while old != s:
        s=preProcess(s)
        if s=='':
            return ''
        old = s
        if s[0] == "(" and s[-1] == ")":
            s = s[1:-1]

        for c in ["-",")",":","/","for\\b","client"]:            
            while c == s[0:len(c)]:
                s = s[len(c):]
                if s=='':
                    return ''

        for c in ["(",":","/"]:
            while c == s[-len(c)]:
                s = s[:-len(c)]
                if s=='':
                    return ''

        while ")" == s[-1] and "(" not in s:
            s = s[:-1]
            
        while "(" == s[-1] and ")" not in s:
            s = s[:-1]
                                
    s = re.sub('-',' ',s)
    
    return preProcess(s)
    

def splitName(name):
    name = preProcess(name).lower()
    if "\"fka\"" in name: # The "'s mess up the word boundaries 
        return re.split("\"fka\"",name)
    
    splitters = ["fka:","fka","f/k/a","f/k/a/",
                 "formerly known as",
                 "formerly know as",
                 "formerly filed as",
                 "formerly reported as",                                  
                 "formerly",
                 "formally known as",
                 "also known as",                                  
                 "formally", 
                 "former", #united natural products alliance (former utah natural products alliance)?
                 "d/b/a",
                 "dba",
    ]#todo: compile regex ahead of times
    for s in splitters:
        if s in name and name != "dba international":
            return re.split("\\b"+s+"\\b",name)

    #remove acronyms
    #greater richmond transit company (grtc) ==> greater richmond transit (grtc)
    #housing action resource trust (hart) ==> housing action resource trust
    #ousing action resource trust ("hart")

    g = re.match(r"([\w' ]*)\((.*)\)$",s)
    mappings = {
        "and":["a",""],
        "for":["f",""],
        "in":["i",""],                
        "southwest":["s","sw"],
        "of":["o",""]
    }
    if g is not None:
        gs = g.groups()
        ws = []
        for w in filter(lambda x: x != "",gs[0].split(" ")):
            if w in mappings:
                ws.append(mappings[w])
            else:
                ws.append([w[0]])
        words = map("".join,list(itertools.product(*ws)))
        for w in words:
            if gs[1] == w:
                return [preProcess(w),preProcess(gs[0])]
        
    return [name]

def extractNames(s):
    return filter(lambda x: x !="", map(processClientName,splitName(s)))
