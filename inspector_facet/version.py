VERSION = "UNKNOWN"

try:
    with open("inspector_facet/version.txt") as ifp:
        VERSION = ifp.read().strip()
except:
    pass
