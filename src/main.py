from discord.ext import commands
import discord
import random
import asyncio
import openai
import os
from urllib.request import urlopen

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = 224929939776995329  # Change to your discord id

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

@bot.command()
async def name(ctx):
    await ctx.send(ctx.author.name)

@bot.command()
async def d6(ctx):
    await ctx.send(random.randint(1,6))

@bot.command()
async def admin(ctx, member: discord.Member, *, reason=None):
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    if admin_role is None:
        admin_role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())

    await member.add_roles(admin_role)

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reasons = ["Parce que j'en ai envie", "Parce que je suis un tyran", "Parce que je suis un bot"]
        reason = random.choice(reasons)
    await member.ban(reason=reason)

    await ctx.send(f"{member} a été banni pour la raison suivante: {reason}")

messageCountMap = {}
flood_active = False
max_message = 5
timeout = 10

async def reset_message_count():
    global messageCountMap
    messageCountMap = {}
    await asyncio.sleep(timeout)

    if flood_active:
        await reset_message_count()

@bot.command()
async def flood(ctx):
    global flood_active
    flood_active = not flood_active
    if flood_active:
        await ctx.send("Flood moderation activé")

        await reset_message_count()
    else:
        await ctx.send("Flood moderation désactivé")

@bot.command()
async def xkcd(ctx):
    req = urlopen("https://c.xkcd.com/random/comic/")
    html = str(req.read())
    image_url = html.split('og:image" content="')[1].split('"')[0]
    await ctx.send(image_url)

@bot.command()
async def poll(ctx, question, timeout=None):
    await ctx.message.delete()
    message = await ctx.send(f"**{ctx.author} asks:** {question}")

    await message.add_reaction("👍")
    await message.add_reaction("👎")

    if timeout != None:
        timeout = int(timeout)
        await asyncio.sleep(timeout)
        await message.delete()

@bot.command()
async def prompt(ctx, *, prompt):
    await ctx.send("Je réfléchis...")

    openai.api_key = os.getenv("OPENAI_API_KEY")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    await ctx.send(completion.choices[0].message["content"])

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == 'Salut tout le monde':
        await message.channel.send('{0.author.mention} Salut tout seul'.format(message))

    global flood_active
    global messageCountMap
    if flood_active:
        if message.author in messageCountMap:
            messageCountMap[message.author] += 1
        else:
            messageCountMap[message.author] = 1

        if messageCountMap[message.author] > max_message:
            await message.channel.send('{0.author.mention} Attention au flood chacal'.format(message))
            await message.delete()

    await bot.process_commands(message)


token = os.getenv("BOT_TOKEN")
bot.run(token)  # Starts the bot