import json, sys, urllib.request
URL = "http://127.0.0.1:4599/api/graphql"
def q(query, variables=None):
    req = urllib.request.Request(URL, json.dumps({"query": query, "variables": variables or {}}).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)
def fields(type_name):
    d = q('query($n:String!){__type(name:$n){fields{name args{name type{name kind ofType{name kind ofType{name}}}} type{name kind ofType{name}}} inputFields{name type{name kind ofType{name}}}}}', {"n": type_name})
    return d["data"]["__type"]
if __name__ == "__main__":
    t = fields(sys.argv[1])
    for f in (t.get("fields") or t.get("inputFields") or []):
        if len(sys.argv) < 3 or any(s.lower() in f["name"].lower() for s in sys.argv[2].split(",")):
            print(f["name"], json.dumps(f.get("args", ""))[:300])
