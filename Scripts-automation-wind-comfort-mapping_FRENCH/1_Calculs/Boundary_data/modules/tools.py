import json

commentBeacon = "#"

def LoadJson(fileName):
    if '.json' not in fileName:
        fileName = fileName+'.json'

    with open(fileName) as JSON:
        content = json.loads(JSON.read())
    
    uncommentedContent = []
    for c in content:
        if commentBeacon in c.keys(): # Deleting pseudo commenting entries
            D = {k:c[k] for k in c.keys() if k != commentBeacon}
            
            if len(D) == 0: # If imported dict is only commentary, no importation
                continue
            else:
                uncommentedContent.append(D)

        else:
            D = c
            uncommentedContent.append(D)
    return uncommentedContent
