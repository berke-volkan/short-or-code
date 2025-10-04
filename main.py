import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import json
import datetime
import math
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
    say(message[0])
    with open("tokens.json","r") as f:
       data = json.load(f)
       entry=data["tokens"][0]["price"]
       data["tokens"][0]["holders"].append({"U07SU9F50MT":{"bal":100,"entry":entry}})
       write_2_json(data,f="tokens.json")



@app.message("-recalc")
def recalc(message,say):
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
       change_percent=round((multiplier-1),2)*100
       say(f"UPDATE: New token Price: {price} \n Change On your Balance {change} \n Change(%): %{change_percent}")
@app.message("explore") 
def explore(message,say):
    best_roi={"24h":0}
    with open("tokens.json","r") as f:
        tokens=json.load(f)
        for token in tokens["tokens"]:
            if token["24h"]>best_roi["24h"]:
                best_roi=token
    name=best_roi["token"]
    change=best_roi["24h"]
    price=best_roi["price"]
    say(f"Best token in 24h is: {name} \n24H Change: {change} \nTrade Price: {price} \n\n Created by: /- I need to add a created_by thingy after changing from message event to command -/")

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    with open("users.json","r") as f:
            data = json.load(f)
            for i in data["users"]:
                if (i["slack_id"]==event["user"]):
                    user=i
    token=user["holdings"]
    markdown=""
    for x in token:
        name=x["token"]
        bal=x["bal"]
        price=x["price"]
        a=f"{name}    | {bal}      | H${price} \n"    
        markdown+=a           
    try:
        # Call views.publish with the built-in client
        client.views_publish(
            # Use the user ID associated with the event
            user_id=event["user"],
            # Home tabs must be enabled in your app configuration
            view={
    "type":"home",
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Hey! Welcome to code or short :)*"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text":                    "```"
                    "Coin   | Amount   | Value (H$)\n"
                    f"{markdown}"
                    "```"
			}
		},
	]
})
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, APP)
    handler.start()
