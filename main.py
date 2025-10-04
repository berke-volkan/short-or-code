import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import json
import datetime
# Install the Slack app and get xoxb- token in advance

app = App(token=OBB)

@app.message("hello")
def hello(message,say):
    user=message["user"]
    say(f"Hey <@{user}>! Please write -join if you want to join to code or short :)")


def write_2_json(data,f):
   with open(f, "w", encoding="utf-8") as f:
        try:
           json.dump(data,f)
        except json.JSONDecodeError:
            data = {}

@app.message("-join")
def join(message,say):

   with open("users.json", "r", encoding="utf-8") as f:
        try:
           data = json.load(f)
           timestamp= datetime.datetime.now().timestamp()
           print(timestamp)
           say("ı registered you")
           data["users"].append({"slack_id":message["user"],"reg_stamp":timestamp,"holdings":[],"price":1})
           write_2_json(data,f="users.json")

        except json.JSONDecodeError:
            data = []
   with open("tokens.json","r") as f:
       data = json.load(f)
       data["tokens"].append({"token":message["user"],"holders":[],"24h":0,"price":1})
       write_2_json(data,f="tokens.json")

@app.message("-token")
def explore(message,say):
    say("buying token")
    with open("tokens.json","r") as f:
       data = json.load(f)
       entry=data["tokens"][0]["price"]
       data["tokens"][0]["holders"].append({"U07SU9F50MT":{"bal":100,"entry":entry}})
       write_2_json(data,f="tokens.json")



@app.message("-recalc")
def explore(message,say):
    say("recalcing token price")
    resp=requests.get("https://hackatime.hackclub.com/api/v1/users/kzlpndx/stats?start_date=2025-09-03&end_date=2025-10-03")
    resp=resp.json()
    multiplier=resp["data"]["total_seconds"]/10800 #this equals to 3h.Maybe ı can change later but id
    with open("tokens.json","r") as f:
       data = json.load(f)
       entry=data["tokens"][0]["holders"][0]["U07SU9F50MT"]["entry"]
       data["tokens"][0]["price"]=multiplier*data["tokens"][0]["price"]
       write_2_json(data,f="tokens.json")
       price=data["tokens"][0]["price"]
       pos=data["tokens"][0]["holders"][0]["U07SU9F50MT"]["bal"]
       change=(price-entry)*pos
       say(f"UPDATE: New token Price: {price} \n Change On your Balance {change}")

     


if __name__ == "__main__":
    handler = SocketModeHandler(app, APP)
    handler.start()
