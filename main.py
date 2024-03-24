import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

main_channel = None


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
async def setmainchannel(interactor: discord.Interaction, channel: discord.TextChannel):
    global main_channel
    main_channel = channel
    await interactor.response.send_message("El canal principal ahora es: " + channel.mention)


@bot.tree.command()
async def getfilebycategory(interactor: discord.Interaction,
                            file_extension: str,
                            category: discord.CategoryChannel, order: bool = False, file_name: str = ""):

    if main_channel is not None:
        await interactor.response.send_message("Busqueda iniciada")
        files = await search_by_category(category=category, file_extension=file_extension, order=order)
        if len(files) == 0:
            await interactor.followup.send("No se encontraron archivos en este canal")
            return
        elif len(file_name) > 0:
            files = filter_by_name(files=files, file_name=file_name)

        thread = await create_thread(channel=main_channel, thread_name=(category.name + file_extension))
        await print_files(thread=thread, files=files)
        await interactor.followup.send("Busqueda terminada")
    else:
        await interactor.response.send_message("Aun no se ha designado un canal para mostrar los resultados. Por favor use el comando /setmainchannel channel_name")


@bot.tree.command()
async def getfilebychannel(interactor: discord.Interaction,
                           file_extension: str, channel: discord.TextChannel, order: bool = False, file_name: str = ""):

    if main_channel is not None:
        await interactor.response.send_message("Busqueda iniciada")

        files = await search_by_channel(channel=channel, file_extension=file_extension, order=order)

        if len(files) == 0:
            await interactor.followup.send("No se encontraron archivos en este canal")
            return
        elif len(file_name) > 0:
            files = filter_by_name(files=files, file_name=file_name)

        thread = await create_thread(channel=main_channel, thread_name=(channel.name + file_extension))
        await print_files(thread=thread, files=files)
        await interactor.followup.send("Busqueda terminada")
    else:
        await interactor.response.send_message("Aun no se ha designado un canal para mostrar los resultados. Por favor use el comando /setmainchannel channel_name")


def filter_by_name(files: list[str], file_name: str) -> list[str]:
    filter_files = []
    for file in files:
        if file_name in file:
            filter_files.append(file)

    return filter_files


async def search_by_category(category: discord.CategoryChannel, file_extension: str, order: bool = False) -> list[str]:
    files = []
    channels = category.text_channels
    for channel in channels:
        message_list = await search_by_channel(channel=channel, file_extension=file_extension, order=order)
        for message in message_list:
            files.append(message)

    return files


async def search_by_channel(channel: discord.TextChannel, file_extension: str, order: bool = False) -> list[str]:
    files = []
    async for message in channel.history(limit=None, oldest_first=order):
        if len(message.attachments) > 0 and "Find the File Bot" not in message.author.name:
            for file in message.attachments:
                if file.filename.endswith(file_extension):
                    files.append(file.url)
                print(file.content_type)

    return files


async def print_files(thread: discord.Thread, files: list[str]):
    urls = await get_url_thread(thread=thread)
    for file in files:
        if file not in urls:
            await thread.send(file)


async def get_url_thread(thread: discord.Thread) -> list[str]:
    return [messages.content async for messages in thread.history(limit=None)]


async def create_thread(channel: discord.TextChannel, thread_name: str) -> discord.Thread:
    for thread in channel.threads:
        if thread.name == thread_name:
            return thread

    return await channel.create_thread(name=thread_name)


bot.run(os.getenv('TOKEN'))
