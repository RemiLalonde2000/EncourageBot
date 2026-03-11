import os
import discord
import requests
import json
import random
from replit import db
from keepAlive import keep_alive


class MemoryDB(dict):
  def keys(self):
    return super().keys()


if db is None:
  print("Warning: Replit DB not configured. Falling back to in-memory storage.")
  db = MemoryDB()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

sadWords = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]

starterEncouragements = [
  "Cheer up!", "Hang in there.", "You are a great person!"
]

originalOpeners = [
  "Today is a fresh start",
  "Your effort matters",
  "You are stronger than you feel",
  "Small steps still count"
]

originalClosers = [
  "keep moving forward 🌟",
  "your future self will thank you 💪",
  "you've got this 🔥",
  "one breath at a time 🌈"
]

if "responding" not in db.keys():
  db["responding"] = True


def getQuote():
  response = requests.get("https://zenquotes.io/api/random")
  jsonData = json.loads(response.text)
  quote = jsonData[0]['q'] + " -" + jsonData[0]['a']
  return quote


def getEarthPhoto():
  try:
    photo_id = random.randint(1, 1084)
    info = requests.get(f"https://picsum.photos/id/{photo_id}/info", timeout=10).json()
    image_url = f"https://picsum.photos/id/{photo_id}/1200/800"
    author = info.get("author", "Unknown")
    return image_url, author
  except Exception as e:
    return None, None


def getF1DriverStandings():
  try:
    response = requests.get(
      "https://api.jolpi.ca/ergast/f1/current/driverStandings.json", timeout=10
    )
    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
      return "No standings data available yet for this season."
    entries = standings[0]["DriverStandings"][:10]
    season = standings[0]["season"]
    lines = [f"**F1 Driver Standings — {season} Season**\n"]
    for entry in entries:
      pos = entry["position"]
      driver = entry["Driver"]
      name = f"{driver['givenName']} {driver['familyName']}"
      points = entry["points"]
      constructor = entry["Constructors"][0]["name"]
      lines.append(f"`{pos}.` **{name}** ({constructor}) — {points} pts")
    return "\n".join(lines)
  except Exception as e:
    return f"Could not fetch F1 standings: {e}"


def getF1ConstructorStandings():
  try:
    response = requests.get(
      "https://api.jolpi.ca/ergast/f1/current/constructorStandings.json",
      timeout=10
    )
    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
      return "No constructor standings data available yet for this season."
    entries = standings[0]["ConstructorStandings"]
    season = standings[0]["season"]
    lines = [f"**F1 Constructor Standings — {season} Season**\n"]
    for entry in entries:
      pos = entry["position"]
      constructor = entry["Constructor"]["name"]
      points = entry["points"]
      wins = entry["wins"]
      lines.append(f"`{pos}.` **{constructor}** — {points} pts ({wins} wins)")
    return "\n".join(lines)
  except Exception as e:
    return f"Could not fetch F1 constructor standings: {e}"


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

  if msg.startswith("$original"):
    originalMessage = (
      f"{random.choice(originalOpeners)} — {random.choice(originalClosers)}"
    )
    await message.channel.send(originalMessage)

  if db["responding"]:
    options = list(starterEncouragements)

    if "encouragements" in db.keys():
      options.extend(db["encouragements"])

    if any(word in msg.lower() for word in sadWords):
      await message.channel.send(random.choice(options))

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

  if msg.startswith("$earth"):
    image_url, author = getEarthPhoto()
    if image_url:
      embed = discord.Embed(title="🌍 A Beautiful Part of the World", color=0x1a73e8)
      embed.set_image(url=image_url)
      embed.set_footer(text=f"Photo by {author}")
      await message.channel.send(embed=embed)
    else:
      await message.channel.send("Could not fetch an Earth photo right now.")

  if msg.startswith("$f1constructors"):
    standings = getF1ConstructorStandings()
    await message.channel.send(standings)
  elif msg.startswith("$f1"):
    standings = getF1DriverStandings()
    await message.channel.send(standings)


my_secret = os.environ['TOKEN']
keep_alive()
client.run(my_secret)
