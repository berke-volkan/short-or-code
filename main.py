import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import json
# Install the Slack app and get xoxb- token in advance
app = App(token="xoxb-2210535565-9627716046115-UCjrnzAOgDyzRJQX9Gw1cOM8")

@app.message("hello")
def hello(message,say):
    resp=requests.get("https://hackatime.hackclub.com/api/v1/users/kzlpndx/stats")
    resp=resp.json()
    user=message["user"]
    say(f"Hey <@{user}>! Please write /join if you want to join to code or short :)")
data = {}
@app.message("-join")
def join(message,say):
   
   with open("users.json", "r", encoding="utf-8") as f:
        try:
           data.append(json.load(f))
           print(data)
        except json.JSONDecodeError:
            data = []
   data.append({"name":message["user"]})
   print(data)
   with open("users.json", "w", encoding="utf-8") as f:
        try:
           json.dump(f,data)
        except json.JSONDecodeError:
            data = {}

     


if __name__ == "__main__":

    handler = SocketModeHandler(app, "xapp-1-A09JCBFBJKG-9627690213283-53cd4ebfe8d390f3b74304d0e0f2b8516f3c937dd4c66cbd1a093c4361a49498")
    handler.start()
