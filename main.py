import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from enum import Enum
from typing import Literal
from multipledispatch import dispatch

# todo busca por Python Typing Literals y multiple choices


class SearchType(Enum):
    specific_search = 0
    full_search = 2


FileExtensions = Literal["pdf", "doc", "docx"]
discord.app_commands.choices()
load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

main_channel = None

extensions = [
    discord.app_commands.Choice(name="pdf", value="pdf"),
    discord.app_commands.Choice(name="doc", value="doc"),
    discord.app_commands.Choice(name="docx", value="docx")
]

categos = Literal["Ninguna"]


def gocats(res, asset):
    fis = Literal[res, asset]
    return fis


def get_categories(interactor: discord.Interaction):
    cats = interactor.guild.categories
    res = Literal["Ninguna"]
    for cat in cats:
        res = gocats(res, cat.name)

    return res


@bot.event
async def on_ready():
    print('we have logged in as {0.user}'.format(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        print(synced)
    except Exception as e:
        print(e)


# todo cada que se agrege un archivo por cualquiera de estos metodos, este tambien debe agregarse
#  a su hilo de extension, asi se facilita la busqueda en el largo plazo, ademas de agrega el full
#  search y el log search, tambien el search al hilo.

# todo agregar usos de attachment.content_type, preferiblemenbe con un enumerador o lista de extensiones para evitar
#  el la entrada de texto indiscriminado


@bot.tree.command()
async def test(interactor: discord.Interaction):
    # noinspection PyUnresolvedReferences
    go = get_categories(interactor)
    global categos
    categos = go
    sy = await bot.tree.sync()
    print(len(sy))


@bot.tree.command()
async def setmainchannel(interactor: discord.Interaction, channel: discord.TextChannel):
    global main_channel
    main_channel = channel
    global categos
    categos = get_categories(interactor)
    # noinspection PyUnresolvedReferences
    await interactor.response.send_message("El canal principal ahora es: " + channel.mention)


@bot.tree.command()
async def getmainchannel(interactor: discord.Interaction):
    # noinspection PyUnresolvedReferences
    await interactor.response.send_message(main_channel.mention if main_channel is not None else
                                           "No hay canal asignado, asigne uso usando /setmainchannel")

# todo fix this xd
@bot.tree.command()
async def getfileinguild(interactor: discord.Interaction, file_extension: FileExtensions,
                         exceptions: discord.CategoryChannel, order: bool = False, file_name: str = ""):
    if len(exceptions) > 0:
        await search_generalization(interactor, SearchType.specific_search, file_extension,
                                    interactor.guild, file_name, order, list(exceptions))
    else:
        await search_generalization(interactor, SearchType.full_search, file_extension,
                                    interactor.guild, file_name, order)


@bot.tree.command()
async def getfilebycategory(interactor: discord.Interaction, file_extension: FileExtensions,
                            category: discord.CategoryChannel, order: bool = False, file_name: str = ""):

    await search_generalization(interactor, SearchType.specific_search, file_extension, category,
                                file_name, order)


@bot.tree.command()
async def getfilebychannel(interactor: discord.Interaction, file_extension: FileExtensions,
                           channel: discord.TextChannel, order: bool = False, file_name: str = ""):

    await search_generalization(interactor, SearchType.specific_search, file_extension, channel, file_name, order)


async def search_generalization(interactor: discord.Interaction, search_type: SearchType, file_extension: str,
                                discord_entity, file_name: str = "", order: bool = False, exceptions: list[str] = None):
    if main_channel is None:
        # noinspection PyUnresolvedReferences
        await interactor.response.send_message("Aun no se ha designado un canal para mostrar los resultados. " +
                                               "Por favor use el comando /setmainchannel channel_name")
        return
    # noinspection PyUnresolvedReferences
    await interactor.response.send_message("Busqueda iniciada")
    files = []

    if search_type == SearchType.specific_search:
        files = get_file(discord_entity, file_extension, order)

    if search_type == SearchType.full_search:
        files = get_file(discord_entity, file_extension, order, exceptions)

    if len(files) < 1:
        await interactor.followup.send("No se encontraron estos archivos en", discord_entity.name)
        return

    if len(file_name) > 0:
        filter_by_name(files, file_name)

    thread = await create_thread(main_channel, discord_entity.name + file_extension)
    await print_files(thread, files)
    await interactor.followup.send("Busqueda terminada")


@dispatch(discord.Guild, str, bool, list)
async def get_file(guild: discord.Guild, file_extension: str, order: bool = False,
                   exceptions: list[str] = None) -> list[str]:
    files = []
    categories = guild.categories
    for category in categories:
        if category.name not in exceptions:
            message_list = await get_file(category, file_extension, order)
            for message in message_list:
                files.append(message)

    return files


@dispatch(discord.CategoryChannel, str, bool)
async def get_file(category: discord.CategoryChannel, file_extension: str, order: bool = False) -> list[str]:
    files = []
    channels = category.text_channels
    for channel in channels:
        message_list = await get_file(channel, file_extension, order)
        for message in message_list:
            files.append(message)

    return files


@dispatch(discord.TextChannel, str, bool)
async def get_file(channel: discord.TextChannel, file_extension: str, order: bool = False) -> list[str]:
    files = []
    async for message in channel.history(limit=None, oldest_first=order):
        if len(message.attachments) > 0 and "Find the File Bot" not in message.author.name:
            for file in message.attachments:
                if file.content_type.endswith(file_extension):
                    files.append(file.url)
                print(file.content_type)

    return files


async def print_files(thread: discord.Thread, files: list[str]):
    urls = await get_url_thread(thread)
    for file in files:
        if file not in urls:
            print("in:", file not in urls)
            await thread.send(file)
        print("out:", file not in urls)


async def get_url_thread(thread: discord.Thread) -> list[str]:
    return [messages.content async for messages in thread.history(limit=None)]


async def create_thread(channel: discord.TextChannel, thread_name: str) -> discord.Thread:
    for thread in channel.threads:
        if thread.name == thread_name:
            return thread

    return await channel.create_thread(name=thread_name)


def filter_by_name(files: list[str], file_name: str) -> list[str]:
    filter_files = []
    for file in files:
        if file_name in file:
            filter_files.append(file)

    return filter_files


bot.run(os.getenv('TOKEN'))
