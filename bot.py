import discord
import random
from discord.ext import commands
from discord.utils import get
import json

users = {}
assignments = {}
participants = []
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


description = '''A lil santa thing :D'''

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')


@bot.command()
async def AssignRecipients(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You don't have perms to do this")
        return
    guild = ctx.message.author.guild
    participantRole = get(guild.roles, id=1179527861569335306)
    participants = []
    for member in guild.members:
        if participantRole in member.roles:
            participants.append(member)
    random.shuffle(participants)
    for i in range(len(participants)):
        try:
            assignments[participants[i].id] = participants[i + 1].id
        except:
            assignments[participants[i].id] = participants[0].id

    with open("data.json", "r") as read_file:
        data = json.load(read_file)
    for userID in assignments:
        try:
            data[str(userID)]["assignment"] = assignments[userID]
        except:
            data[userID] = {}
            data[userID]["assignment"] = assignments[userID]
        member = discord.utils.get(participants, id=userID)
        assignment = discord.utils.get(participants, id=assignments[userID])
        await member.send(f"Congrats! The person you're doing art for is... *insert drumroll here*\n\n\n{assignment.mention}!")
    with open("data.json", "w") as write_file:
        json.dump(data, write_file)
        
@bot.command()
async def TestAssignments(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You don't have perms to do this")
        return
    print("\n")
    guild = ctx.message.author.guild
    participantRole = get(guild.roles, id=1179527861569335306)
    participants = []
    for member in guild.members:
        if participantRole in member.roles:
            await member.send("You're all set for secret santa!")
    await ctx.send("@everyone if you did not get a dm from this bot and you want to participate, contact the host, because you won't get an assignment either!")


@bot.command()
async def SignUp(ctx):
    member = ctx.message.author
    guild = member.guild
    role = get(guild.roles, id=1179527861569335306)
    if role in member.roles:
        await ctx.send("You're already signed up! If you no longer wish to participate use !withdraw")
    else:
        await member.add_roles(role)
        await ctx.send("You're now a particpant!")

        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        privateChannels = discord.utils.get(guild.categories,id=1179539391262236692)
        channel = await guild.create_text_channel(member.name, overwrites=overwrites, category=privateChannels)


@bot.command()
async def Withdraw(ctx):
    member = ctx.message.author
    guild = member.guild
    role = get(guild.roles, id=1179527861569335306)
    if role in member.roles:
        privateChannel = discord.utils.get(guild.channels, name=member.name)
        await privateChannel.delete(reason="{member.display_name} is no longer a participant.")
        await member.remove_roles(role)
        await ctx.send("You're no longer a particpant")
    else:
        await ctx.send("You've already withdrawn")
        
@bot.command()
async def Request(ctx, *requests:str):
    requestString = ""
    for request in requests:
        requestString += request + " "
    member = ctx.message.author
    with open("data.json", "r") as read_file:
        data = json.load(read_file)

    try:
            data[str(member.id)]["requests"] = requestString
    except:
            data[member.id] = {}
            data[member.id]["requests"] = requestString

    with open("data.json", "w") as write_file:
        json.dump(data, write_file)

@bot.command()
async def SeeRequests(ctx):
    with open("data.json", "r") as read_file:
        data = json.load(read_file)
    guild = ctx.guild
    member = ctx.message.author
    assignment = data.get(str(member.id), {}).get('assignment')
    if assignment:
        assignedUser = await bot.fetch_user(assignment)
        request = data.get(str(assignment), {}).get('requests')
        if request:
            await member.send(f"{assignedUser.mention} requested:\n{request}")
        else:
            await member.send(f"{assignedUser.mention} didn't request anything! Go wild!")
    else:
        await member.send("You haven't gotten an assignment yet!")
    print(assignment, member.id)
    
@bot.command()
async def SetStatus(ctx, status:str):
    percentString = ""
    for character in status:
        if character <= '9' and character >= '0' or character == '.':
            percentString += character
    status = float(percentString)
    if status >= 0 and status <= 100:
        with open("data.json", "r") as read_file:
            data = json.load(read_file)

        try:
                data[str(ctx.author.id)]["artStatus"] = status
        except:
                data[ctx.author.id] = {}
                data[ctx.author.id]["artStatus"] = status

        with open("data.json", "w") as write_file:
            json.dump(data, write_file)
    else:
        await ctx.send("Not a valid percent")
            
@bot.command()
async def CheckCompletion(ctx):
    author = ctx.author
    with open("data.json", "r") as read_file:
            data = json.load(read_file)
    for userID in data:
        if data[userID]["assignment"] == author.id:
            artist = userID
            break
    completionPercent = data.get(str(artist), {}).get("artStatus")
    if not completionPercent:
        completionPercent = 0
    await ctx.send(f"Your secret santa claims they are {completionPercent:0.2f}% done with your art!\n(Keep in mind, they may not have updated it!)")

TOKEN = 1


bot.run(TOKEN)