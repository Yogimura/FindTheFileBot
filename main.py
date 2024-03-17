import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
last_research = {}


@bot.event
async def on_ready():
    print('we have logged in as {0.user}'.format(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        print(synced)
    except Exception as e:
        print(e)


@bot.tree.command()
@app_commands.describe(extension="File extension")
@app_commands.describe(limit="Number of files")
@app_commands.describe(categoryid="Category to be scan")
async def getbycategoryft(interactor: discord.Interaction, extension: str, limit: int, categoryid: str):
    await interactor.response.send_message("iniciando proceso")

    await exist_thread(interactor, extension)
    thread = load_thread(interactor, extension)

    messages = await search_by_category(interactor, extension, limit, categoryid)

    for file in messages:
        await thread.send(file)

    await interactor.followup.send("Todos los archivos han sido enviados")


@bot.tree.command()
@app_commands.describe(extension="File extension")
@app_commands.describe(limit="Number of files")
@app_commands.describe(limit_comprobator="Number of comparison to avoid redundancies on threads")
@app_commands.describe(categoryid="Category to be scan")
async def getbycategory(interactor: discord.Interaction, extension: str, limit: int, limit_comprobator: int, categoryid: str):

    await interactor.response.send_message("iniciando proceso")

    await exist_thread(interactor, extension)
    thread = load_thread(interactor, extension)

    messages = await search_by_category(interactor, extension, limit, categoryid)
    thread_messages = await search_by_thread(thread, limit_comprobator)

    valid_messages = []

    for x in messages:
        if x not in thread_messages:
            valid_messages.append(x)

    for file in valid_messages:
        await thread.send(file)

    await interactor.followup.send("Todos los archivos han sido enviados")


@bot.tree.command()
@app_commands.describe(extension="File extension")
@app_commands.describe(limit="Number of files")
@app_commands.describe(limit_comprobator="Number of comparison to avoid redundancies on threads")
async def getbyguildft(interactor: discord.Interaction, extension: str, limit: int, limit_comprobator: int):

    await interactor.response.send_message("iniciando proceso")

    await exist_thread(interactor, extension)
    thread = load_thread(interactor, extension)

    messages = await search_by_guild(interactor, extension, limit)
    thread_messages = await search_by_thread(thread, limit_comprobator)

    valid_messages = []

    for x in messages:
        if x not in thread_messages:
            valid_messages.append(x)

    for file in valid_messages:
        await thread.send(file)

    await interactor.followup.send("Todos los archivos han sido enviados")


@bot.tree.command()
@app_commands.describe(extension="File extension")
@app_commands.describe(limit="Number of files")
async def getbyguild(interactor: discord.Interaction, extension: str, limit: int):

    await interactor.response.send_message("iniciando proceso")

    await exist_thread(interactor, extension)
    thread = load_thread(interactor, extension)

    messages = await search_by_guild(interactor, extension, limit)

    for file in messages:
        await thread.send(file)

    await interactor.followup.send("Todos los archivos han sido enviados")


async def search_by_category(interactor, extension, limit, categoryID):
    categories = interactor.guild.categories
    category = ""
    for catego in categories:
        if catego.id == int(categoryID):
            category = catego.text_channels

    messages = []
    for channel in category:
        async for message in channel.history(limit=limit):
            if "Find the File Bot" not in message.author.name and len(message.attachments) > 0:
                attachs = message.attachments
                for file in attachs:
                    if file.filename.endswith(extension):
                        messages.append(file.url)

    return messages


async def search_by_guild(interactor, extension, limit) -> list[str]:
    channelslist = interactor.guild.text_channels
    messages = []
    for channel in channelslist:
        async for message in channel.history(limit=limit):
            if "Find the File Bot" not in message.author.name and len(message.attachments) > 0:
                attachs = message.attachments
                for file in attachs:
                    if file.filename.endswith(extension):
                        messages.append(file.url)

    return messages


async def search_by_thread(thread, limit) -> list[str]:
    messages = []
    async for message in thread.history(limit=limit):
        messages.append(message.content)

    return messages


async def exist_thread(interactor, extension):
    threads = interactor.channel.threads
    threadsnames = []
    for th in threads:
        threadsnames.append(th.name)

    if extension not in threadsnames:
        await interactor.channel.create_thread(name=extension)


def load_thread(interactor, extension):
    threads = interactor.channel.threads
    thread = 0
    for th in threads:
        if th.name in extension:
            thread = th

    return thread


bot.run(os.getenv('TOKEN'))
