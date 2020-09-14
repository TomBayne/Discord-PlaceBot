import asyncio
import discord
from datetime import datetime, timedelta
import time
from PIL import Image
from PIL import ImageColor
from multiprocessing import Process
from shutil import copyfile

now = datetime.now()  # get current datetime
nowNice = dt_string = now.strftime("[%d/%m/%Y %H:%M:%S]")  # make it look nice for prepending
nowFile = dt_string = now.strftime("%d%m%Y-%H%M")
nowEmbed = dt_string = now.strftime("%d/%m/%Y %H:%M")  # nice datetime for embed
tomorrow = now + timedelta(hours=24)
tomorrowEmbed = dt_string = tomorrow.strftime("%d/%m/%Y %H:%M")


def backup():
    while True:
        dst = 'resources/' + nowFile + '.png'
        copyfile('resources/place.png', dst)
        print(nowNice + 'Created png backup')
        time.sleep(86400)


client = discord.Client()  # init connection to discord


possibleColors = ["lightgreen", "orange", "brown", "yellow", "white", "grey", "lightgrey", "pink", "red",
                  "purple", "brightpink", "darkblue", "blue", "lightblue", "green", "black"]
rgbCodes = ["#93e330", "#e89800", "#a26a3d", "#e7dc00", "#ffffff", "#89888a", "#e5e5e5", "#ffa8d2", "#e90000",
            "#830082", "#e33cff", "#0100ef", "#0083cb", "#00e6f2", "#00c100", "#000000"]

global cooldownList
cooldownList = []

colorString = ', '.join(possibleColors)


@client.event
async def on_ready():  # when bot loads
    print(nowNice, 'Bot has started as {0.user}'.format(client))  # print bot username
    connectedUsers = len(client.users)
    connectedServers = len(client.guilds)
    print('Bot Online! We are serving ', connectedUsers, ' users across ', connectedServers, ' different servers!')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="!showplace"))
    while True:
        b = open('resources/place.png', 'rb')
        await client.user.edit(avatar=b.read())
        b.close()
        print(nowNice + 'Updated Profile Picture')
        await asyncio.sleep(3600)


@client.event
async def on_message(message):
    global cooldownList
    if message.content.startswith('!showplace'):  # if a user types !showplace

        colorsString = ""
        colorsString.join(possibleColors)

        file = discord.File("resources/place.png", filename="place.png")
        embed = discord.Embed(title="Place!", description="Place is a game where each user on discord can place a "
                                                          "single pixel into a 1000x1000 canvas every 10 minutes. "
                                                          "Work together to create (or destroy) one pixel at a time.")
        embed.set_image(url="attachment://place.png")
        embed.add_field(name="Total Players", value=str(len(client.users)), inline=True)
        embed.add_field(name="Servers", value=str(len(client.guilds)), inline=True)
        embed.add_field(name="How to Play", value="Use the command \n **'!place [X Coord] [Y Coord] [color]'** \n to "
                                                  "place a pixel.", inline=False)
        embed.add_field(name="Available Colors", value=colorString)
        embed.add_field(name="Add to your server.", value="https://bit.ly/3k1mgaj", inline=False)

        await message.channel.send(file=file, embed=embed, delete_after=300)

        print(nowNice, message.author, ' requested place image on ', message.guild.name)  # log to console
        return
    if message.content.startswith('!place'):
        if message.author.id not in cooldownList:
            sentMsg = str(message.content)
            params = sentMsg.split(' ')
            try:
                xCoord = int(params[1])
                yCoord = int(params[2])
            except:
                xCoord = 9999999 # force the next if statement to fail
                yCoord = 9999999
            try:
                color = str(params[3]).lower()
            except:
                color = None
            if 0 <= xCoord <= 1000 and 0 <= yCoord <= 1000:
                pass
            else:
                embed = discord.Embed(title="Place!", description="Invalid Coordinate Selection. Coordinates must be "
                                                                  "between 0 and 1000")
                await message.channel.send(embed=embed, delete_after=300)
                return
            if color not in possibleColors or color is None:
                embed = discord.Embed(title="Place!", description="Invalid Color Selection.")
                embed.add_field(name="Available Colors", value=colorString, inline=True)
                await message.channel.send(embed=embed, delete_after=300)
                return
            else:
                print(nowNice + message.author.name + '#' + message.author.discriminator + ' added ' + color +
                      ' pixel at (' + str(xCoord) + ', ' + str(yCoord) + ')')
                finalCoord = [xCoord, yCoord]
                rgbColor = rgbCodes[possibleColors.index(color)]
                im = Image.open('resources/place.png')
                im.putpixel(finalCoord, ImageColor.getcolor(rgbColor, "RGB"))
                im.save("resources/place.png", "PNG")  # TODO: Dont immediatly apply, ask confirm selection w/ reaction
                cooldownList += [message.author.id]
                file = discord.File("resources/place.png", filename="place.png")
                embed = discord.Embed(title="Place!", description="Your pixel was added!")
                embed.set_image(url="attachment://place.png")
                embed.add_field(name="Pixel Info", value='Added ' + color + ' pixel at (' + str(xCoord) + ', ' + str(yCoord) + ')', inline=True)
                embed.add_field(name="Add to your server.", value="https://bit.ly/2FlkqSj", inline=False)
                await message.channel.send(file=file, embed=embed, delete_after=300)
                await asyncio.sleep(600)
                cooldownList.remove(message.author.id)
        else:
            embed = discord.Embed(title="Place!", description="You can only place pixels every 10 minutes. Try again "
                                                              "later!")
            await message.channel.send(embed=embed, delete_after=30)

# TODO: Anyway to simplify the process of selecting a pixel?
# TODO: Could we create a database to keep track of who last modified each pixel? It's only 1000x1000 (1m entries)
# TODO: Allow users to query this database? !pixelauthor 1854 340
# TODO: What if multiple users attempt to modify at exactly the same time? can we create a queue system maybe?


def runbot():
    client.run('xxxxxxxxxxxxxxxxx') #run bot with this login token


if __name__ == '__main__':
    Process(target=backup).start()
    Process(target=runbot).start()
