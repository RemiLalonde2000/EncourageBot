import os
import discord
import requests
import json
import random
from replit import db
from keepAlive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

sadWords = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]

starterEncouragements = [
  "Cheer up!", "Hang in there.", "You are a great person!"
]

if "responding" not in db.keys():
  db["responding"] = True


def getQuote():
  response = requests.get("https://zenquotes.io/api/random")
  jsonData = json.loads(response.text)
  quote = jsonData[0]['q'] + " -" + jsonData[0]['a']
  return quote


def updateEncouragements(encouragingMessage):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouragingMessage)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouragingMessage]


def deleteEncouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
  db["encouragements"] = encouragements


@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):

  msg = message.content
  if message.author == client.user:
    return

  if msg.startswith("$inspire"):
    quote = getQuote()
    await message.channel.send(quote)

  if db["responding"]:
    options = starterEncouragements

    if "encouragements" in db.keys():
      options = options.extend(db["encouragements"])

    if any(word in msg for word in sadWords):
      await message.channel.send(random.choice(db["encouragements"]))

  if msg.startswith("$new"):
    encouragingMessage = msg.split("$new ", 1)[1]
    updateEncouragements(encouragingMessage)
    await message.channel.send("New encouraging message added.")

  if msg.startswith("$del"):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(msg.split("$del", 1)[1])
      deleteEncouragement(index)
      encouragements = db["encouragements"]
    await message.channel.send("Encouraging message deleted.")

  if msg.startswith("$list"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  if msg.startswith("$responding"):
    value = msg.split("$responding ", 1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off.")


my_secret = os.environ['TOKEN']
keep_alive()
client.run(my_secret)
