import re

def replaceWhitespace(s):
    return re.sub('  +', ' ', s)

def preProcess(s):
    org = s
    s = s.encode("ascii","ignore")    
    s = re.sub('\n', ' ', s)
    s = s.strip().strip('"').strip("'").lower().strip()
    s = replaceWhitespace(s)
    if s == 'legi\\x company': #LEGI\X is ridiclous 
        s = "legi-x company"        
    return s
