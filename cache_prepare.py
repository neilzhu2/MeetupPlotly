import requests
import json

CACHE_FNAME = 'cache_file.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params = {}):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params = {}, style = 'json'): #style = 'json' or 'html'
    unique_ident = params_unique_combination(baseurl,params)
    if unique_ident in CACHE_DICTION:
        if 'error_msg' not in CACHE_DICTION[unique_ident]:
            # print("Getting cached data...")
            print(">", end='')
            return CACHE_DICTION[unique_ident]
    else:
        # print("Making a request for new data...")
        print(".", end='')
        # Make the request and cache the new data
        resp = requests.get(baseurl, params=params).text
        if style == 'json':
            CACHE_DICTION[unique_ident] = json.loads(resp)
        elif style == 'html':
            CACHE_DICTION[unique_ident] = resp
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]
