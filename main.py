#bot.py

import discord
import os
import requests
import json
import random
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get
import urllib.parse, urllib.request, re
import youtube_dl
import re

api_key = "INSERT OWN API KEY FOR WEATHERMAP HERE"
base_url = "http://api.openweathermap.org/data/2.5/weather?"

#init bot with prefix '$', can be changed. Useful for understanding commands @client
client = commands.Bot(command_prefix = '!')

#game variables for tictactoe
player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]
#Weather Feature. Takes prefix $weather + the city name (as string),
#returns data about the city using OpenWeatherMap API. Else return city not found.
@client.command()
async def weather(ctx, *, city: str):
    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    channel = ctx.message.channel
    if x["cod"] != "404":
        async with channel.typing():
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsiuis = str(round(current_temperature - 273.15))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Weather in {city_name}",
                              color=ctx.guild.me.top_role.color,
                              timestamp=ctx.message.created_at,)
            embed.add_field(name="Descripition", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Temperature(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
            embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await channel.send(embed=embed)
    else:
        await channel.send("City not found.")

#join feaature for the bot's music capabilites
#join voice channel based on the voice channel of callee.
#If not in a channel, return.
@client.command(pass_context = True)
async def join (ctx):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
#Simple leave command. Disconnect the bot. Only necessary to work if in Voice Channel.
@client.command()
async def leave(ctx): #force argument, in case bad state?
    server = ctx.message.guild.voice_client
    await server.disconnect()

#Command to play Youtube audio based off URL.
#Uses local file with FFmpeg to store mp3 file and play it back through the bot.
#Only works on Youtube links so far
@client.command()
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the stop command")

    # voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = 'DUCT_CLEANING')
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }
    txt = url
    temp = re.search("https://www.youtube.com/", txt)
    if not (temp == None):    
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")
        voice.play(discord.FFmpegPCMAudio("song.mp3"))
    else:
        await ctx.send("That is not a youtube link.")
#Pauses music of the bot only if playing music. Else return.
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No audio is playing, thereforee cant be paused ok")
#Resumes music of the bot only if music is paused. Else return.
@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused, try to play something")
#Stops the bot from playing music.
@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    voice.stop()

#Interactive TicTacToe game between two discord users in the same chat
@client.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

#Pkaces the piece according to user input for TicTacToe game
@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver == True:
                    await ctx.send(mark + " wins!")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")

                # switch turns
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the !tictactoe command.")


#checks for winner of the game
def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

#Can be invoked to finish the game early. Doesn't determine winner.
@client.command()
async def finish(ctx):
    global gameOver
    gameOver = True

#Error handling
@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players (ie. <@688534433879556134>).")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('!h for help'))

#Returns interactive quote using zenquotes API.
@client.command() 
async def inspire(ctx):
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    await ctx.send(quote)

@client.command()
async def warzone(ctx):
    await ctx.send("@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n@everyone warzone or riot NOW\n")

#Help Commands for the user
@client.command()
async def h(ctx):
    embedded = discord.Embed(title = "Help for Tree Bot", description = "Here are some of Tree Bot's commands (responds to the ! operator):")
    embedded.add_field(name="!warzone", value="Pings everyone in the server to play Warzone.")
    embedded.add_field(name="!inspire", value = "Sends an inspirational quote from some random website, I think?")
    embedded.add_field(name="!tictactoe", value = "Starts a tictactoe game beetween you and a user! To use: <!tictactoe @user1 @user2>.")
    embedded.add_field(name="!weather", value = "Invoke to check weather in a city. To use: <!weather CityNameHere>.")
    embedded.add_field(name ="!play", value = "Plays audio from any youtube video. Must be in a voice channel. To use: <!play InsertURLHere>.")
    await ctx.send(content=None, embed = embedded)

client.run('YOUR DISCORD CLIENT TOKEN HERE')