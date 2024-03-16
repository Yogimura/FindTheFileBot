import json
import os
import random

import discord
import requests
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

sad_words = [
    "sad",
    "depressed",
    "unhappy",
    "angry",
    "miserable",
    "depressing"]

starter_encouragements = [
    "Cheer up!",
    "Hang in there.",
    "You are a great person / bot!"
]


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


@client.event
async def on_ready():
    print('we have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    if msg.startswith("$inspire"):
        quote = get_quote()
        await message.channel.send(quote)

        options = starter_encouragements
        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    if msg.startswith("$list"):
        encouragements = starter_encouragements
        await message.channel.send(list(encouragements))

    await message.channel.send(msg)


client.run(os.getenv('TOKEN'))

