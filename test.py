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


ref = db.reference("users")
data=ref.get()
for key, value in data.items():
    print(key,value)