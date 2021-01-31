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

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix='!',  case_insensitive=True)



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
        await ctx.message.add_reaction('\U0001F9BE')
        

@bot.command()
async def teamup(ctx, nom_de_lequipe: str, chef_de_projet: discord.Member, members: commands.Greedy[discord.Member]):
    """
    `!teamup nom_de_lequipe chef_de_projet membre1 membre2 membre3`: rajouter une equipe
    avec son salon.
    """
    message = ctx.message
    author = ctx.author
    server = ctx.guild
    
    
    role_names = [r.name for  r in author.roles]
    print(role_names)
    if 'admins' not in role_names:
        await message.add_reaction('\U0001F44E')
        await ctx.send("seuls les admins peuvent faire cette action!")
        return
    
    
    
    
    
    serv_roles = await server.fetch_roles()
    if nom_de_lequipe not in [r.name for r in serv_roles]:
        teamrole = await server.create_role(name=nom_de_lequipe,
                                           mentionable=True,
                                           reason="admin through bot")
    else:
        await message.add_reaction('\U0001F44E')
        await ctx.send(f"L'équipe {nom_de_lequipe} existe déjà. Utilisez `!teamadd` pour rajouter des membres.")
        return
        
    
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
    
    
    msg = (f"Tout le monde a été rajouté dans l'équipe {teamrole.name}, et "
           f"{chef_de_projet.name} "
           f"a été rajouté aux {cdp_role.name}.\n"
            " il ne manque plus qu'un salon!")
    
    await ctx.send(msg)
    
    overwrites = {
        server.default_role: discord.PermissionOverwrite(read_messages=False),
        teamrole: discord.PermissionOverwrite(read_messages=True),
    }
    
    for r in serv_roles:
        if r.name.lower() in ['admins','benevoles','bénévoles','coach']:
            overwrites[r]=discord.PermissionOverwrite(read_messages=True)
    
    team_cat = await server.create_category(f'salons de {nom_de_lequipe}',
                                             overwrites=overwrites,
                                             reason='Nouvelle équipe')
    
    text = await team_cat.create_text_channel('Chat')
    voice = await team_cat.create_voice_channel('Vocal')
    msg = (f"C'est bon! <@&{teamrole.id}> vous pouvez vous rendre sur"
           f"<#{text.id}> et <#{voice.id}>.")
    await ctx.send(msg)
    
        
@teamup.error
async def teamup_error(ctx, error):
    message = ctx.message
    print(error)
    if isinstance(error, commands.BadArgument):
        await message.add_reaction('\U0001F44E')
        await ctx.send("Erreur! La commande est du type `!teamup nom_de_lequipe chef_de_projet membre1 membre2 membre3`")
    

if __name__ == "__main__":
    bot.run(TOKEN)


