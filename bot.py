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

REACTIONS_YESNO = ['✅', '❌']
REACTIONS_MULTI = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))



@bot.command()
async def aide(ctx):
    """utilisez plutôt `!help`"""
    embed = discord.Embed()
    
    msg = ""
    msg += "==== Hacking Industry Camp - AIDE ====\n"
    msg += "- `!help` : pour obtenir l'aide des commandes\n"
    msg += "- `@bénévoles` : pour appeler un bénévole\n"
    msg += "- `@coach` : pour être coaché\n"
    msg += "- `@admins` : si quelqu'un doit passer au conseil disciplinaire\n"
    msg += "\n"
    msg += "Votez en cliquant sous les emojis. Y a un nombre max de vote!\n"
    
    
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
    message = ctx.message
    author = ctx.author
    role_names = [r.name for  r in author.roles]
    print(role_names)
    if 'admins' not in role_names:
        await message.add_reaction('\U0001F44E')
        await ctx.send("seuls les admins peuvent faire cette action!")
        return
    
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
    if isinstance(error, commands.BadArgument) or (isinstance(error, commands.MissingRequiredArgument)):
        await message.add_reaction('\U0001F44E')
        await ctx.send("Erreur! La commande est du type `!teamup nom_de_lequipe chef_de_projet membre1 membre2 membre3`")
    
############## debut poll


@bot.command()
async def new_poll(ctx, question: str,maxvotes: int=1, *options: str):
    "Faire un nouveau vote."
    message = ctx.message
    author = ctx.author
    role_names = [r.name for  r in author.roles]
    print(role_names)
    if 'admins' not in role_names:
        await message.add_reaction('\U0001F44E')
        await ctx.send("seuls les admins peuvent faire cette action!")
        return
    if len(options) <= 1:
        await ctx.send('Il vous faut au minimum une option')
        return
    if len(options) > 10:
        await ctx.send("Trop d'options")
        return
    
    if maxvotes <1:
        await ctx.send('Il vous faut au minimum une option')
        return
        

    if len(options) == 2 and options[0] == 'oui' and options[1] == 'non':
        reactions = REACTIONS_YESNO
    else:
        reactions = REACTIONS_MULTI
    
    if maxvotes == 1:
        description = [f"**{maxvotes} vote max**"]
    else:
        description = [f"**{maxvotes} votes max**"]
    for x, option in enumerate(options):
        description += '\n {} {}'.format(reactions[x], option)
    embed = discord.Embed(title=question, description=''.join(description))
    react_message = await ctx.send(embed=embed)
    for reaction in reactions[:len(options)]:
        await react_message.add_reaction(reaction)
    print(str(react_message.id))
    embed.set_footer(text=f'Poll {maxvotes} : ' + str(react_message.id))
    await react_message.edit(embed=embed)
    
    
@new_poll.error
async def new_poll_error(ctx, error):
    message = ctx.message
    print(error)
    if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
        await message.add_reaction('\U0001F44E')
        await ctx.send("Erreur! La commande est du type `!new_poll \"question\" nombre_max_de_vote \"opt1\" \"opt2\"...`")
    


@bot.command()
async def reset_poll(ctx, id: int):
    """Reset un poll identifié par `id`. l'`id` d'un vote se trouve sous
    chaque vote"""
    message = ctx.message
    author = ctx.author
    role_names = [r.name for  r in author.roles]
    print(role_names)
    if 'admins' not in role_names:
        await message.add_reaction('\U0001F44E')
        await ctx.send("seuls les admins peuvent faire cette action!")
        return
    
    
    called_msg = await ctx.fetch_message(id)


    if called_msg.author != bot.user:
        #chek whether bot actually posted the reacted message, otherwise ignores
        return
    

    msg_react = called_msg.reactions
    
    for r in msg_react:
        await called_msg.clear_reaction(r.emoji)
        await called_msg.add_reaction(r.emoji)

# supprime un sondage
@bot.command()
async def destroy_poll(ctx, id: int):
    message = ctx.message
    author = ctx.author
    role_names = [r.name for  r in author.roles]
    print(role_names)
    if 'admins' not in role_names:
        await message.add_reaction('\U0001F44E')
        await ctx.send("seuls les admins peuvent faire cette action!")
        return
    message = await ctx.fetch_message(id)
    await message.delete()


@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    channel = message.channel
    emoji = reaction.emoji
    number_of_votes = 0
    
    
    if message.author != bot.user:
        #chek whether bot actually posted the reacted message, otherwise ignores
        return
    
    if user == bot.user:
        #ignores if it is the bot voting
        return
    
    if (emoji not in REACTIONS_YESNO) and (emoji not in REACTIONS_MULTI):
        #only vote reactions are accepted
        return
    
    
    
    for e in message.embeds:
        #check if it's a reaction to a vote
        if ('Poll' in e.footer.text):
            title = e.title
            try:
                maxvotes = int(e.footer.text.split()[1])
            except:
                return
            break
    else:
        return
    
    for r in message.reactions:
        users = await r.users().flatten()
        if user in users:
            number_of_votes+=1
            if number_of_votes>maxvotes:
                await reaction.remove(user)
                await channel.send(f'<@!{user.id}> ne peut plus voter à "{title}", c\'est son vote n°{number_of_votes}/{maxvotes}')
                return
    await channel.send(f'{user.name} a voté {reaction.emoji} à "{title}", c\'est son vote n°{number_of_votes}/{maxvotes}')

if __name__ == "__main__":
    bot.run(TOKEN)


