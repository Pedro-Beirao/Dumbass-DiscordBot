import discord
from discord.opus import is_loaded
import discord_slash
import requests
import json
from discord.ext import commands
from discord.ext import tasks
import random
from discord.utils import get
import re
import yt_dlp
import os
from asyncio import sleep
import asyncio
import requests
from kahoot import client
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

intents = discord.Intents.default()
intents.members = True 

bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents)
bot.remove_command('help')
slash = discord_slash.SlashCommand(bot, sync_commands=True, override_type=True)


currentDir = os.path.realpath(__file__)[:-6]
print(currentDir)

lasttime=0
a=0
buly = " "
userino1 = " "
userino2 = " "
userino3 = " "
server = []
delayttv = "5"
queue = {}

gids =[]


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name='| /help for help'))

def hook(response):
    if response["status"] == "downloading":
        print(response['elapsed'])
        if(response['elapsed']>5):
            print("on no")

@slash.slash(name="help", description="Show help menu")
async def help(ctx):
            emb = discord.Embed(title="Dumbass", description="I am not a bot, I am a vietnamese boy forced to work as a fake discord bot. \n SEND HELP ", color=0x3498db)
            emb.add_field(name="Commands:", value="/kill <name> --- to see your enemies take their last breath. \n /insult <name> --- to make someone cry. \n /bully <name> --- to bully someone. ||Say 'i am a big crying baby' to stop|| \n /muck | /nomuck --- to muck \n /yomomma --- for a yo momma joke \n /ttv <streamer name> --- to check if a streamer is live \n /kahoot --- to flood a kahoot game" , inline=False)
            emb.add_field(name="Music Commands", value="/play <name of music> --- Play music\n/skip --- Skip song\n/queue --- Show music queue\n/clear --- Clear music queue", inline=False)
            emb.add_field(name="Mod only commands:", value="Type 'mod i am dumb'", inline=False)
            await ctx.send(embed = emb)

async def playMusicSource(ctx, file, down, musicName):
                    user=ctx.author
                    voice_channel=user.voice.channel
                    voice_client = ctx.guild.voice_client
                    try: 
                        if queue[ctx.guild.name][0] != "placeholder lol":
                            pass
                    except:
                        queue[ctx.guild.name] = []
                    queue[ctx.guild.name].append(musicName)
                    print(queue)
                    while queue[ctx.guild.name][0] != musicName:
                        await sleep(1)

                    try:
                        while voice_client.is_playing():
                            await sleep(1)
                    except: pass

                    await sleep(1)

                    try:
                        vc= await voice_channel.connect()
                    except:
                        vc = voice_client

                    await down.delete()
                    emb = discord.Embed(title="Now Playing", color=0x3498db)
                    emb.add_field(name=file['title'], value="lol", inline=False)
                    await ctx.channel.send(embed = emb)
                    source = discord.FFmpegOpusAudio(file['url'], **FFMPEG_OPTIONS)
                    vc.play(source)
                    #vc.play(discord.FFmpegOpusAudio(executable='ffmpeg', source=currentDir+"music/"+path))

                    while vc.is_playing():
                        await sleep(1)
                    queue[ctx.guild.name].pop(0)

@slash.slash(name="play", description="Play music", options=[
    create_option(
        name="music",
        description="Music name or link",
        option_type=3,
        required=True),
])
async def playMusic(ctx, music: str):
            try:
                os.mkdir(currentDir+"music")
            except: pass
            message = music
            ydl_opts = {
                'format': 'worstaudio/worst',
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'logtostderr': False,
                'writethumbnail': True,
                'default_search': 'auto',
                'source_address': '0.0.0.0' ,
                'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192',
                }],
                'progress_hooks':[hook],
                'socket_timeout':'5',
            }

            user=ctx.author
            voice_channel=user.voice.channel
            voice_client = ctx.guild.voice_client
            if voice_channel!= None:
                musicName = message
                down = await ctx.send("Downloading: " + musicName)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    loop = asyncio.get_event_loop()
                    file = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{musicName}", download=False))
                    await down.edit(content="Downloaded: " + file['title'])
                    for i in file["entries"]:
                        print(i)
                        await playMusicSource(ctx, i, down, musicName)
                    await sleep(300)
                    try:
                        if not ctx.guild.voice_client.is_playing():
                            await ctx.guild.voice_client.disconnect()
                    except: pass

                    
                
        

@slash.slash(name="skip", description="Skip current song")
async def skip(ctx):
    try:
        a = await ctx.send("Skipped")
        voice_client = ctx.guild.voice_client
        if voice_client.is_connected():
            voice_client.pause()
            await sleep(5)
            await a.delete()
    except:
        queue[ctx.guild.name].pop(0)


@slash.slash(name="clear", description="Clear music queue")
async def clear(ctx):
    queue[ctx.guild.name] = []
    ctx.send("[]")


@slash.slash(name="queue", description="Show music queue")
async def queueList(ctx):
    try:
        print(queue[ctx.guild.name])
        await ctx.send(str(queue[ctx.guild.name]))
    except:
        await ctx.send("[]")
    

@slash.slash(name="ttv", description="Check if streamer is online", options=[
    create_option(
        name="name",
        description="Streamer name",
        option_type=3,
        required=True),
])
async def ttv(ctx, name: str):
    usereno = name
    print(usereno)
    usereno.replace(" ",".")
    try:
        IS_LIVE = isLive(usereno)
    except:
        IS_LIVE=False
    if IS_LIVE:
        emb = discord.Embed(title=usereno+ " is live", description="https://www.twitch.tv/"+usereno, color=0x2ecc71)
        await ctx.send(embed = emb)
    else:
        emb = discord.Embed(title=usereno+ " is not live", description="https://www.twitch.tv/"+usereno, color=0xe74c3c)
        await ctx.send(embed = emb)


@slash.slash(name="bin", description="Binary converter", options=[
    create_option(
        name="args",
        description="Arguments",
        option_type=3,
        required=False),
])
async def binary(ctx, args: str = ""):
    try:
        args = args.split(" ")
        if args[0]=="bd":
            b=0
            d=0
            a = args[1][::-1]
            for c in range(0,len(args[1])):
                if a[c] == "1" and c == len(a)-1:
                    b-= int(a[c]) * 2**(c)
                else:
                    b+=int(a[c]) * 2**(c)
            for c in range(0,len(args[1])):
                    d+=int(a[c]) * 2**(c)
            emb = discord.Embed(title="Binary to Decimal", description=args[1]+"\n\nUnsigned:   `"+str(d)+"`\nSigned "+str(len(args[1]))+"-bit:   `"+str(b)+"`", color=0x3498db)
            await ctx.send(embed = emb)
        elif  args[0]=="db":
            faked= len(bin(int(args[1])).replace("0b", ""))
            if faked < 8:
                f=0b11111111
            elif faked < 16:
                f=0b1111111111111111
            elif faked < 32:
                f=0b11111111111111111111111111111111
            d = bin(int(args[1]) & f).replace("0b", "")


                
            emb = discord.Embed(title="Decimal to Binary", description=args[1]+"\n\n`"+str(d)+"`", color=0x3498db)
            await ctx.send(embed = emb)
        elif  args[0]=="bh":
            d = int(args[1], 2)
            h = hex(d)
            emb = discord.Embed(title="Binary to Hexadecimal", description=args[1]+"\n\n0x   `"+str(h)[2:]+"`", color=0x3498db)
            await ctx.send(embed = emb)
        elif  args[0]=="dh":
            d = bin(int(args[1])).replace("0b", "")
            if d[0]=="-":
                d = d[1:].zfill(8)
                d = d.replace("1","2")
                d = d.replace("0","1")
                d = d.replace("2","0")
                d = bin(int(d,2) + 1).replace("0b", "").zfill(8)
            else:
                d = d.zfill(8)
            print(d)
            h = hex(int(d,2))
            emb = discord.Embed(title="Decimal to Hexadecimal", description=args[1]+"\n\n0x   `"+str(h)[2:]+"`", color=0x3498db)
            await ctx.send(embed = emb)
        elif  args[0]=="hb":
            b=bin(int(args[1], 16))[2:].replace("0b", "")
            emb = discord.Embed(title="Hexadecimal to Binary", description=args[1]+"\n\n`"+str(b)+"`", color=0x3498db)
            await ctx.send(embed = emb)
        elif  args[0]=="hd":
            b=0
            d=bin(int(args[1], 16))[2:].replace("0b", "")
            a = d[::-1]
            for c in range(0,len(d)):
                if a[c] == "1" and c == len(a)-1:
                    b-= int(a[c]) * 2**(c)
                else:
                    b+=int(a[c]) * 2**(c)
            emb = discord.Embed(title="Hexadecimal to Decimal", description=args[1]+"\n\n`"+str(b)+"`", color=0x3498db)
            await ctx.send(embed = emb)
        else:
            emb = discord.Embed(title="Binary converter", description="/bin bd <input> --- binary to decimal\n/bin db <input> --- decimal to binary\n/bin bh <input> --- binary to hex\n/bin dh <input> --- decimal to hex\n/bin hb <input> --- hex to binary\n/bin hd <input> --- hex to decimal", color=0x3498db)
            await ctx.send(embed = emb)
    except:
        emb = discord.Embed(title="Binary converter", description="/bin bd <input> --- binary to decimal\n/bin db <input> --- decimal to binary\n/bin bh <input> --- binary to hex\n/bin dh <input> --- decimal to hex\n/bin hb <input> --- hex to binary\n/bin hd <input> --- hex to decimal", color=0x3498db)
        await ctx.send(embed = emb)

isMucking = False

@slash.slash(name="muck", description="Say 'Muck' every 5 seconds")
async def muck(ctx):
    global isMucking 
    isMucking= True
    while isMucking:
        await ctx.send("Muck")
        await sleep(5)

@slash.slash(name="nomuck", description="Stop the mucking")
async def nomuck(ctx):
    global isMucking
    isMucking = False

@slash.slash(name="kick", description="Kick some asshole", options=[
    create_option(
        name="user",
        description="User about to get kicked",
        option_type=6,
        required=True),
    create_option(
        name="reason",
        description="Reason",
        option_type=3,
        required=False),
])
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason: str = None):
  if not reason:
    await user.kick()
    await ctx.send(user.display_name+" was such a piece of shit, that got kicked")
  else:
    await user.kick(reason=reason)
    await ctx.send(user.display_name+" was such a piece of shit, that got kicked\n\nReason: "+reason)


@slash.slash(name="ban", description="Ban some asshole", options=[
    create_option(
        name="user",
        description="User about to get banned",
        option_type=6,
        required=True),
    create_option(
        name="reason",
        description="Reason",
        option_type=3,
        required=False),
])
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *, reason: str = None):
  if not reason:
    await user.ban()
    await ctx.send(user+" was such a piece of shit, that got banned")
  else:
    await user.ban(reason=reason)
    await ctx.send(user+" was such a piece of shit, that got banned\n\nReason: "+reason)




@slash.slash(name="kill", description="Kill someone", options=[
    create_option(
        name="user",
        description="User",
        option_type=6,
        required=True),
])
async def kill(ctx, user: discord.Member):
            if user.display_name != "Dumbass":
                obituaties = [
                str(user.display_name+" was ran over by a chicken"),
                str(user.display_name+" killed himself, after realizing how dumb "+user.display_name+" is"),
                str(user.display_name+" was walking down the street with the 2 dollars his mommy gave him to buy an icecream, when suddently... OH NO ...a wild Mister Mugger appeared! "+ user.display_name+" tried to run, but his skinny legs and fat belly made it very easy for Mister Mugger to catch him. "+user.display_name+" refused to give up the precious 2 dollars that separated him from the legally overweight, so Mister Mugger stabbed the poor bastard. Even then, "+user.display_name+" didn't give up the money. Moments later he died. And that's how I met your mother *Intro Starts*"),
                str(" "+user.display_name+": *Is alive* \n "+user.display_name+": You're terminated, fucker! \n "+ user.display_name+": *Is dead*"),
                str(user.display_name+" was killed by his own stupidity"),
                str(user.display_name+" was killed by flatulence"),
                str(user.display_name+" was killed by flying sphagetti"),
                str(user.display_name+" was killed by obesity"),
                str(user.display_name+" was killed by a one legged midget"),
                str(user.display_name+" fragged "+user.display_name),
                ]
            await ctx.send(random.choice(obituaties))



@slash.slash(name="insult", description="Insult someone", options=[
    create_option(
        name="user",
        description="User",
        option_type=6,
        required=True),
])
async def insult(ctx, user: discord.Member):
            if not user.display_name=="Dumbass":
                insulted = user.display_name
                response = requests.get("https://insult.mattbas.org/api/insult.txt?who="+insulted, verify=False)
                await ctx.send(response.text)


@slash.slash(name="bully", description="Bully someone", options=[
    create_option(
        name="user",
        description="User",
        option_type=6,
        required=True),
])
async def bully(ctx, user: discord.Member):
            buly = user.display_name
            if not user.display_name=="Dumbass":
                with open(currentDir+"/Config.json", "r") as load_file:
                    data = json.load(load_file)
                    with open(currentDir+"/Config.json", "w") as read_file:
                        new_data = {
                            "bullied":buly
                            }
                        data[ctx.guild.name]=new_data
                        json.dump(data, read_file)
                    await ctx.send("You got it, I'm gonna buly "+ user.display_name+ " like there is no tomorrow.")


@slash.slash(name="yomomma", description="Yo momma joke")
async def yomomma(ctx):
            response = requests.get("https://api.yomomma.info", verify=False)
            response=response.text
            response=response[9:]
            response=response[:-2]
            await ctx.send(response)

@slash.slash(name="kahoot", description="Flood a kahoot", options=[
    create_option(
        name="args",
        description="Arguments",
        option_type=3,
        required=False),
])
async def kahoot(ctx, args: str = ""):
    try:
            if len(args)<3:
                emb = discord.Embed(title="Kahoot", description="/kahoot rickroll <game id> --- to rickroll and entire class\n/kahoot up <amount of bots> <game id> --- flood a kahoot with student like names\n/kahoot name=<some name> <amount of bots> <game id> --- flood a kahoot with a specific user name", color=0x3498db)
                await ctx.send(embed = emb)
                return
            args = args.split(" ")
            if(args[0]=="rickroll"):
                gameid = args[1]
                emb = discord.Embed(title="Kahoot", description="Rickrolling game "+gameid, color=0x3498db)
                await ctx.send(embed = emb)
                rickroll = ["We’re no strangers to love","You know the rules and so do I","A full commitment’s what I’m thinking of","You wouldn’t get this from any other guy","I just wanna tell you", "how I’m feeling","Gotta make you understand", "Never gonna give you up", "Never gonna let you down", "Never gonna run around and desert you", "Never gonna make you cry", "Never gonna say goodbye", "Never gonna tell a lie and hurt you", "We’ve known each other for so long", "Your heart’s been aching, but", "You’re too shy to say it", "Inside, we both know what’s been going on", "We know the game and we’re gonna play it", "And if you ask me how I’m feeling", "Don’t tell me you’re too blind to see", "Never gonna give you up ", "Never gonna let you down ", "Never gonna run around and desert you ", "Never gonna make you cry ", "Never gonna say goodbye ", "Never gonna tell a lie and hurt you ", "Never gonna give you up  ", "Never gonna let you down  ", "Never gonna run around and desert you  ", "Never gonna make you cry  ", "Never gonna say goodbye  ", "Never gonna tell a lie and hurt you  ", "Never gonna give you up   ", "Never gonna let you down   ", "Never gonna run around and desert you   ", "Never gonna make you cry   ", "Never gonna say goodbye   ", "Never gonna tell a lie and hurt you   ", "Never gonna give you up    ", "Never gonna let you down"    ]
                amount = len(rickroll)
                for i in range(0, amount):
                    bot = client()
                    bot.join((gameid), rickroll[i])
            elif(args[0]=="up"):
                gameid = args[2]
                amount = args[1]
                emb = discord.Embed(title="Kahoot", description="Flooding kahoot game as a fake FEUP student", color=0x3498db)
                await ctx.send(embed = emb)
                for i in range(0, int(amount)):
                    bot = client()
                    username = ("up2021" +str(random.randint(1000, 9999)))
                    bot.join((gameid), username)
            elif(args[0].startswith("name=")):
                gameid = args[2]
                amount = args[1]
                emb = discord.Embed(title="Kahoot", description="With a specific name", color=0x3498db)
                await ctx.send(embed = emb)
                for i in range(0, int(amount)):
                    bot = client()
                    username = (args[0][args[0].find("=")+1:] +" "+str(random.randint(1000, 9999)))
                    bot.join((gameid), username)
    except:
            emb = discord.Embed(title="Kahoot", description="/kahoot rickroll <game id> --- to rickroll and entire class\n/kahoot up <amount of bots> <game id> --- flood a kahoot with student like names\n/kahoot name=<some name> <amount of bots> <game id> --- flood a kahoot with a specific user name", color=0x3498db)
            await ctx.send(embed = emb)

@slash.slash(name="button", description="button")
async def button(ctx):
    buttons = [
        create_button(style=ButtonStyle.green, label="A green button"),
        create_button(style=ButtonStyle.blue, label="A blue button")
    ]
    action_row = create_actionrow(*buttons)

    await ctx.send(components=[action_row])

@bot.event
async def on_message(message):
        global delayttv
        global a
        global aboutToKick



        with open(currentDir+"/Config.json", "r") as read_file:
            data = json.load(read_file)
            try:
                guildjson=data[message.guild.name]
                buly=guildjson["bullied"]
            except:
                buly=" "

        
        if message.content.lower().startswith('i am a big crying baby'):
            buly = " "
            with open(currentDir+"/Config.json", "w") as load_file:
                    new_data = {
                        "bullied":buly
                        }
                    data[message.guild.name] =new_data
                    json.dump(data, load_file)

        if message.author.display_name == buly:
            insulted = message.author.display_name
            response = requests.get("https://insult.mattbas.org/api/insult.txt?who="+insulted, verify=False)
            await message.channel.send(response.text)
            return

        #help menu
        if message.content.lower().startswith('i am dumb'):
            await help(message.channel)
            
            
            #mod help menu
        if message.content.lower().startswith('mod i am dumb'):
                emb = discord.Embed(title="Dumbass - Mod only", description="I am not a bot, I am a vietnamese boy forced to work as a fake discord bot. \n SEND HELP ", color=0x3498db)
                emb.add_field(name="Mod only commands:", value="'/kick' + name --- to kick someone without a reason. \n '/kick' + reason + name --- to kick someone with a reason. \n '/ban' + name --- to ban someone without a reason. \n '/ban' + reason + name --- to ban someone with a reason.", inline=False)
                await message.channel.send(embed = emb)

        #to other commands
        try:
            if message.mentions[0].name=="Dumbass":
                await message.channel.send("How dumb do you think I am?")
        except:
            pass
    
        await bot.process_commands(message)



#check if live
HEADERS = { 'client-id' : 'kimne78kx3ncx6brgo4mv6wki5h1ko' }
GQL_QUERY = """
query($login: String) {
    user(login: $login) {
        stream {
            id
        }
    }
}
"""
def isLive(username):
    QUERY = {
        'query': GQL_QUERY,
        'variables': {
            'login': username
        }
    }

    response = requests.post('https://gql.twitch.tv/gql',
                             json=QUERY, headers=HEADERS)
    dict_response = response.json()
    print(dict_response)
    return True if dict_response['data']['user']['stream'] else False
    










bot.run('Your Token Here')