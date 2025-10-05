import firebase_admin
from firebase_admin import db
import requests
cred_obj = firebase_admin.credentials.Certificate('firebase.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':"https://volkan-f6d36-default-rtdb.firebaseio.com"
    })

ref = db.reference("/tokens")

import json
with open("tokens.json", "r") as f:
    file_contents = json.load(f)
def write_2_json(data,f):
   with open(f, "w", encoding="utf-8") as f:
        try:
           json.dump(data,f)
        except json.JSONDecodeError:
            data = {}


ref = db.reference("tokens")
data=ref.get()
for x in range(data["tokens"]["totalcount"]):
    creator_id=data["tokens"][f"{x}"]["created_by"]
    print(creator_id)
    resp=requests.get(f"https://hackatime.hackclub.com/api/v1/users/{creator_id}/stats?start_date=2025-09-03&end_date=2025-10-03")
    resp=resp.json()
    multiplier=resp["data"]["total_seconds"]/10800 
    data["tokens"][f"{x}"]["price"]=data["tokens"][f"{x}"]["price"]*multiplier
ref.set(data)