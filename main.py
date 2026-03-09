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

  if msg.startswith("$vote"):
    pollBody = msg.split("$vote", 1)[1].strip()

    if not pollBody:
      await message.channel.send(
        "Use: $vote Question | Option 1 | Option 2 (or just $vote Question for 👍/👎)"
      )
      return

    parts = [part.strip() for part in pollBody.split("|") if part.strip()]

    if len(parts) >= 3:
      question = parts[0]
      choices = parts[1:10]
      numberEmojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
      pollLines = [f"📊 **{question}**"]

      for index, choice in enumerate(choices):
        pollLines.append(f"{numberEmojis[index]} {choice}")

      sentPoll = await message.channel.send("\n".join(pollLines))

      for emoji in numberEmojis[:len(choices)]:
        await sentPoll.add_reaction(emoji)
    else:
      question = pollBody
      sentPoll = await message.channel.send(f"📊 **{question}**\n👍 = Yes\n👎 = No")
      await sentPoll.add_reaction("👍")
      await sentPoll.add_reaction("👎")

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


my_secret = os.environ['TOKEN']
keep_alive()
client.run(my_secret)
