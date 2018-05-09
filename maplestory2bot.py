import discord
import os

def index(request):
    return tokenAddres(token)

client = discord.Client()
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
client.run(os.environ.get(tokenAddress))
#NDQzNTY5NzU3ODA3OTY4MjU2.DdPycQ.wzKxgVcytX3sbvslj5zZg32sLmU
