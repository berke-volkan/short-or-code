import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import json
import datetime
# Install the Slack app and get xoxb- token in advance
app = App(token="token")

@app.message("hello")
def hello(message,say):
    resp=requests.get("https://hackatime.hackclub.com/api/v1/users/kzlpndx/stats")
    resp=resp.json()
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
       data["tokens"].append({"token":message["user"],"holders":[],"24h":0})
       write_2_json(data,f="tokens.json")

@app.message("-explore")
def explore(message,say):
    pass

     


if __name__ == "__main__":
    handler = SocketModeHandler(app, "token")
    handler.start()
