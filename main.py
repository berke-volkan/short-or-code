import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import json
import datetime
import math
import firebase_admin
from firebase_admin import db
from datetime import datetime,timedelta
# Install the Slack app and get xoxb- token in advance

cred_obj = firebase_admin.credentials.Certificate('firebase.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':"https://volkan-f6d36-default-rtdb.firebaseio.com"
    })

ref = db.reference("/tokens")


app = App(token=OBB)

@app.message("hello")
def hello(message,say):
    user=message["user"]
    say(f"Hey <@{user}>! Please write /join-code if you want to join to code or short :)")
@app.command("/buy")
def buy(ack, respond, command):
    ack()
    user_input = command.get('text', '')
    args = user_input.split()

    with open("users.json","r") as f:
        data=json.load(f)
        for x in data["users"]:
            if (x["slack_id"]==command["user_id"]):
                budget=x["budget"]
    if (int(args[1])<=budget):
        with open("tokens.json","r") as f:
            data = json.load(f)
            for i in data["tokens"]:
             if(i["token"]==args[0]):
               entry=i["price"]
               amount=int(args[1])/entry
               i["holders"].append({"U07SU9F50MT":{"bal":amount,"entry":entry}})
               write_2_json(data,f="tokens.json")
               respond(f"Bought: {args[0]} \n Amount: {amount} \n From:H${entry} per stock")
               #well well ı need to write this data to users.json too :heavysob:
    else:
        respond("⚠️ Fraud Detected \n Just kidding.Did you think that ı would approve a transaction over your budget?")
@app.event("app_uninstalled")
def uninstalled(client, event, logger):
    requests.post("https://ntfy.sh/slack-gambling-status",data="Someone uninstalled me from Hack Club Slack 😭 Plz add me back".encode(encoding='utf-8'))


def write_2_json(data,f):
   with open(f, "w", encoding="utf-8") as f:
        try:
           json.dump(data,f)
        except json.JSONDecodeError:
            data = {}

@app.command("/join-code")
def join(command,ack,respond):
   ack()
   with open("users.json", "r", encoding="utf-8") as f:
        try:
           data = json.load(f)
           timestamp= datetime.now().timestamp()
           print(timestamp)
           respond("Hey! I registered u & created your token")
           username=command["user_name"]
           uid=command["user_id"]
           requests.post("https://ntfy.sh/gambling-user-log",data=f"Hey ya! It looks like someone joined to Code Or Short \nUser:{username}({uid}) \nTimestamp: {timestamp}".encode(encoding='utf-8'))
           data["users"].append({"slack_id":command["user_id"],"reg_stamp":timestamp,"holdings":[],"budget":100,"marketcap":100})
           write_2_json(data,f="users.json")

        except json.JSONDecodeError:
            data = []
   with open("tokens.json","r") as f:
       data = json.load(f)
       data["tokens"].append({"token":command["user_id"],"holders":[],"24h":0,"price":1})
       write_2_json(data,f="tokens.json")

@app.command("/deprecated-buy")
def token(command,ack,respond):
    ack()
    with open("tokens.json","r") as f:
       data = json.load(f)
       entry=data["tokens"][0]["price"]
       data["tokens"][0]["holders"].append({"U07SU9F50MT":{"bal":100,"entry":entry}})
       write_2_json(data,f="tokens.json")

@app.command("/recalc")
def recalc(command,ack,respond):
    ack()
    respond("[THIS COMMAND IS ONLY FOR TESTING PURPOSES.PLEASE DONT ABUSE]\nHey ya! I am recalculating value of this token :)")
    user_input = command.get('text', '')
    args = user_input.split()
    userid=""
    if (args[0]!=[]):
        userid=args[0]
    else:
        userid=command["user_id"]
    resp=requests.get(f"https://hackatime.hackclub.com/api/v1/users/{userid}/stats?start_date=2025-09-03&end_date=2025-10-03")
    resp=resp.json()
    multiplier=resp["data"]["total_seconds"]/10800 #this equals to 3h.Maybe ı can change later but id
    with open("tokens.json","r") as f:
       data = json.load(f)
       for x in data["tokens"]:
           if (x["created_by"]==userid):
               x["price"]=x["price"]*multiplier
               write_2_json(data,f="tokens.json")
               price=x["price"]
               change=(round(multiplier-1,2))*100
               respond(f"Hey! New price of stock: {round(price,2)}  \n Change(%): %{change}")

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

@app.command("/market-cap")
def cap(ack,respond,command):
    ack()
    user_input = command.get('text', '')
    args = user_input.split()
    uid=""
    with open("tokens.json","r") as f:
            data = json.load(f)  
            cap=0
            for i in data["tokens"]:
                
                if args[0]==[]:
                    uid=command["user_id"]
                else:
                    uid=args[0]
                if i["created_by"]==uid:
                    for x in i["holders"]:
                        for user in x:
                            cap+=x[user]['bal']
    if uid==command["user_id"]:
        respond(f"Hey you yes you.You worth H${cap} 💎")
    else:
        ping=f"<@{uid}>"
        respond(f"Stalking others? Oh cool! Creator of this coins is:{ping} & Market Cap is: H${cap} 💎")

def get_total_stars(username):
   url = f"https://api.github.com/users/{username}/repos"
   total_stars = 0
   page = 1
   while True:
       response = requests.get(url, params={"page": page, "per_page": 100})
       if response.status_code != 200:
           print(f"Error: {response.status_code}")
           break
       repos = response.json()
       if not repos:
           break
       total_stars += sum(repo['stargazers_count'] for repo in repos)
       page += 1
   return total_stars

@app.command("/connect")
def github(ack,respond,command):
    ack()
    user_input = command.get('text', '')
    args = user_input.split()
    with open("users.json","r") as f:
            data = json.load(f)
            for x in data["users"]:
                if(x["slack_id"]==command["user_id"]):
                    if (x["github"]=="undefined"):
                        if (args[0]==[]):
                            respond("Please provide a gh username")
                        else:
                            x["github"]=args[0]
                            write_2_json(data,"users.json")
                            respond(f"I set your gh account to: {args[0]}")
                            name=x["slack_id"]
                            gh=x["github"]
                            requests.post("https://ntfy.sh/gambling-connection",data=f"{name} just connected their github account yaay! \n Github Account: {gh}".encode(encoding='utf-8'))
                    else:
                        respond("You already connected github")
@app.command("/connect-scrapbook")
def github(ack,respond,command):
    ack()
    user_input = command.get('text', '')
    args = user_input.split()
    with open("users.json","r") as f:
            data = json.load(f)
            for x in data["users"]:
                if(x["slack_id"]==command["user_id"]):
                    if (x["scrapbook"]=="undefined"):
                        if (args[0]==[]):
                            respond("Please provide a gh username")
                        else:
                            x["scrapbook"]=args[0]
                            write_2_json(data,"users.json")
                            respond(f"I set your scrapbook account to: {args[0]}")
                            name=x["slack_id"]
                            sc=x["scrapbook"]
                            requests.post("https://ntfy.sh/gambling-connection",data=f"{name} just connected their scrapbook account yaay! \n Scrapbook Account: {sc}".encode(encoding='utf-8'))
                    else:
                        respond("You already connected scrapbook")

@app.command("/hacker-score")
def scoring(ack,respond,command):
    ack()
    with open("users.json","r") as f:
        data = json.load(f)
        for x in data["users"]:
            if(x["slack_id"]==command["user_id"]):
                if(x["github"]=="undefined"):
                    respond("Plase setup your gh name using /connect command")
                else:
                    stars=get_total_stars(x["github"])
                    u=command["user_id"]
                    hour=requests.get(f"https://hackatime.hackclub.com/api/v1/users/{u}/stats")
                    hour=hour.json()["data"]["human_readable_total"]
                    now=datetime.utcnow()
                    seven_days_ago = now - timedelta(days=7)
                    start_date = seven_days_ago.strftime("%Y-%m-%d")
                    end_date = now.strftime("%Y-%m-%d")
                    sevenday=requests.get(f"https://hackatime.hackclub.com/api/v1/users/{u}/stats?start_date={start_date}&end_date={end_date}")
                    seven_hour=sevenday.json()["data"]["human_readable_daily_average"]
                    thirty_days_ago = now - timedelta(days=30)
                    start_date = thirty_days_ago.strftime("%Y-%m-%d")
                    end_date = now.strftime("%Y-%m-%d")
                    thirtyday=requests.get(f"https://hackatime.hackclub.com/api/v1/users/{u}/stats?start_date={start_date}&end_date={end_date}")
                    thirtyday=thirtyday.json()["data"]["human_readable_daily_average"]
                    print(sevenday.json())
                    if x["scrapbook"]=="undefined":
                        respond("Hey! Please connect your scrapbook using /connect-scrapbook")
                    else:
                        scrap=x["scrapbook"]
                        scrapbook=requests.get(f"https://scrapbook.hackclub.com/api/users/{scrap}").json()["profile"]
                        streak=scrapbook["streakCount"]
                        maxStreak=scrapbook["maxStreaks"]
                        respond(f"Here is your Hacker Score \nGH Stars: {stars} \n-------------------Hackatime-------------------\nScrapbbok Streak: {streak} (Max: {maxStreak}) \nTotal hours logged: {hour}\n 7D Daily: {seven_hour}  \n 1 Month Daily: {thirtyday}")


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
        entry=x["entry"]
        profit=(price-entry)*bal
        a=f"{name}    | {bal}      | H${price}        | H${price*bal}       | H${profit} (%{round(price-entry,2)*100}) \n"    
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
                    "Coin   | Amount   | Price (H$) | Value (H$)  | Profit (H$)\n"
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


