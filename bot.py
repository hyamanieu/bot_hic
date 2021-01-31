import discord
from discord.ext import commands
# from command import Action_Picker, show_help
# from extra_commands import show_planning, check_role, make_group
#env file
import os
from os.path import join, dirname
from dotenv import load_dotenv 
import requests
from pdfminer.high_level import extract_text
from io import BytesIO
import typing
from vote_list import *

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix='!',  case_insensitive=True)

#Pour les votes




@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))



@bot.command()
async def aide(ctx):
    """utilisez plutôt `!help`"""
    embed = discord.Embed()
    
    msg = ""
    msg += "==== Hacking Industry Camp - AIDE ====\n"
    msg += "- `!help` : pour obtenir l'aide complète\n"
    
    
    field_name = "Aide"
    embed.add_field(name=field_name,value=msg)

    await ctx.send(embed=embed)



@bot.command()
async def planning(ctx, period: typing.Optional[str] = None):
    """`!planning [opt: vendredi|samedi|dimanche|semaine]` te donne le planning et le lien vers le PDF."""
    embed = discord.Embed()
    
    
    
    url = 'https://www.hackingindustry.camp/Planning-HIC-2021.pdf'
    r = requests.get(url, allow_redirects=True)
    embed.add_field(name="lien",value=url)
    embed.set_thumbnail(url='https://www.hackingindustry.camp/images/logos/Logo_HIC_White.png')
    bio = BytesIO(r.content)
    pdf = extract_text(bio)   
    
    
    fields = ['planning',
            'vendredi 5 février 2021',
            'samedi 6 février 2021',
            'dimanche 7 février 2021',
            'du lundi 8 février au vendredi 12 février 2021']
    
    
    idxs = []
    idx_ends = []
    
    
    opt_list = {'vendredi':1,'samedi':2,'dimanche':3,'semaine':4}
    
    for f in fields:
        try:
            idx = pdf.lower().index(f)
            idx_end = idx + len(f)
            idxs.append(idx)
            idx_ends.append(idx_end)
        except ValueError:
            pass
        
    if period is None:
        for i in range(len(idxs)):
            field_name = pdf[idxs[i]:idx_ends[i]]
            msg_end = -1 if i+1>=len(idxs) else idxs[i+1]
            msg = pdf[idx_ends[i]:msg_end]
            embed.add_field(name=field_name,value=msg)
    elif period.lower() in opt_list:
        opt = period.lower()
        period = opt_list[opt]
        #
        field_name = pdf[idxs[period]:idx_ends[period]]
        msg_end = -1 if period+1>=len(idxs) else idxs[period+1]
        msg = pdf[idx_ends[period]:msg_end]
        embed.add_field(name=field_name,value=msg)
        
    else:
        field_name = 'error'
        msg = "options possibles sont:\n"
        msg += "- `!planning` pour le planning entier\n"
        for k in opt_list.keys():
            msg += f"- `!planning {k}`\n"
        
        embed.add_field(name=field_name,value=msg)
        
        
        
    await ctx.send(embed=embed)

@bot.command()
async def admin(ctx):
    """`!admin` réagit en te faisant comprendre si t'es admin"""
    author = ctx.message.author
    
    role_names = [r.name for  r in author.roles]
    if '@admin' in role_names:
        await ctx.message.add_reaction('\U0001F9BE')
    else:
        await ctx.message.add_reaction('\U0001F44E')
        
        
        


@bot.command()
async def teamadd(ctx, nom_de_lequipe: discord.Role, members: commands.Greedy[discord.Member]):
    """"`!teamadd membre1 membre2`: rajouter des participants à une équipe."""
    for member in members:
        await member.add_roles(nom_de_lequipe)

@bot.command()
async def teamup(ctx, nom_de_lequipe: str, chef_de_projet: discord.Member, members: commands.Greedy[discord.Member]):
    """
    `!teamup nom_de_lequipe chef_de_projet membre1 membre2 membre3`: rajouter une equipe
    avec son salon.
    """
    message = ctx.message
    author = ctx.author
    server = ctx.guild
    mentions = message.mentions
    
    
    role_names = [r.name for  r in author.roles]
    if '@admin' not in role_names:
        await message.add_reaction('\U0001F44E')
        await ctx.send("seuls les admins peuvent faire cette action!")
    
    
    
    
    
    serv_roles = await server.fetch_roles()
    if nom_de_lequipe not in [r.name for r in serv_roles]:
        teamrole = await server.create_role(name=nom_de_lequipe,
                                           mentionable=True,
                                           reason="admin through bot")
    else:
        await message.add_reaction('\U0001F44E')
        await ctx.send(f"L'équipe {nom_de_lequipe} existe déjà. Utilisez `!teamadd` pour rajouter des membres.")
        
    
    print("mentions: ",mentions)
    print('members: ', chef_de_projet, members)
    
    #check if chefdeproj role already exists. If not, creates it.
    if 'chefdeproj' not in [r.name for r in serv_roles]:
        cdp_role = await server.create_role(name='chefdeproj',
                                       mentionable=True,
                                       reason="admin through bot")
    else:
        for r in serv_roles:
            if r.name == 'chefdeproj':
                cdp_role = r
                break
    #add the teamleader to both chefdeproj and his team's role.
    await chef_de_projet.add_roles(teamrole, cdp_role)
    
    #then each member
    for member in members:
        await member.add_roles(teamrole)
    
    await message.add_reaction('\U0001F9BE')
    
    await ctx.send("Tout le monde est rajouté, manque plus qu'un salon!")
    
    
        
@teamup.error
async def teamup_error(ctx, error):
    message = ctx.message
    if isinstance(error, commands.BadArgument):
        await message.add_reaction('\U0001F44E')
        await ctx.send("Erreur! La commande est du type `!teamup nom_de_lequipe chef_de_projet membre1 membre2 membre3`")
    

############## debut poll


@bot.command()
async def new_poll(ctx, question: str, *options: str):
    if len(options) <= 1:
        await ctx.send('Il vous faut au minimum une option')
        return
    if len(options) > 10:
        await ctx.send("Trop d'options")
        return
    
    if len(options) == 2 and options[0] == 'oui' and options[1] == 'non':
        reactions = ['✅', '❌']
    else:
        reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

    description = []
    for x, option in enumerate(options):
        description += '\n {} {}'.format(reactions[x], option)
    embed = discord.Embed(title=question, description=''.join(description))
    react_message = await ctx.send(embed=embed)
    for reaction in reactions[:len(options)]:
        await react_message.add_reaction(reaction)
    print(str(react_message.id))
    embed.set_footer(text='Poll ID: ' + str(react_message.id))
    await react_message.edit(embed=embed)

#marche pas encore - doit remettre les compteurs à 0 (ou 1 du coup sinon ils disparaissent)
@bot.command()
async def reset_poll(ctx, id: int):
    message = await ctx.fetch_message(id)
    
    msg_react = message.reactions
    print(msg_react)

# supprime un sondage
@bot.command()
async def destroy_poll(ctx, id: int):
    message = await ctx.fetch_message(id)
    await message.delete()


#marche pas
@bot.event
async def on_reaction_add(reaction, user):
    #channel = reaction.message.channel
    chan = discord.utils.get(bot.get_all_channels(), id=805421069887995925)
    await chan.send('{} has added {} to the message: {}'.format(user.name, reaction.emoji, reaction.message.content))
    

bot.run(TOKEN)


