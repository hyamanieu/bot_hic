import discord
from command import Action_Picker, show_help

#env file
import os
from os.path import join, dirname
from dotenv import load_dotenv 

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv('BOT_TOKEN')

client = discord.Client()


action_dic = {'!aide':show_help,
    }

action_picker = Action_Picker(action_dic)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):

    if message.author == client.user:
        return


    await action_picker.choix_action(message)

    

client.run(TOKEN)


