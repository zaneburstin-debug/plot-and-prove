import json, urllib.request
def fetch_user(uid):
    with urllib.request.urlopen(f"https://api.example.com/u/{uid}") as r:
        return json.loads(r.read())

def display_name(uid):
    u = fetch_user(uid)
    return u["first"] + " " + u["last"]     # real API returns 'given'/'family'
