#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 14:57:28 2021

@author: hyamanieu
"""
import bs4
import urllib.request
import discord
import shlex

import requests
from pdfminer.high_level import extract_text
from io import BytesIO
import argparse


def show_planning(*args):
    embed = discord.Embed()
    print(args)
    
    
    
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
        
    if len(args) == 1:
        for i in range(len(idxs)):
            field_name = pdf[idxs[i]:idx_ends[i]]
            msg_end = -1 if i+1>=len(idxs) else idxs[i+1]
            msg = pdf[idx_ends[i]:msg_end]
            embed.add_field(name=field_name,value=msg)
    elif args[1].lower() in opt_list:
        opt = args[1].lower()
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
        
        
        
    return embed


async def check_role(message):
    author = message.author
    
    role_names = [r.name for  r in author.roles]
    if '@admin' in role_names:
        await message.add_reaction('\U0001F9BE')
    else:
        await message.add_reaction('\U0001F44E')
        
        
        
class NonexitParser(argparse.ArgumentParser):

    def error(self, message):
        raise ValueError('Mal fait!')



async def make_group(message):
    """
    respond to the following request (considering caller is !teamup)
    
    !teamup -n nom_de_lequipe -chef chef_de_projet -membres membre1 membre2 membre3
    
    
    Parameters
    ----------
    message : discord Message
    Returns
    -------
    str
        simple stirng to return as message

    """
    author = message.author
    server = message.guild
    content = message.content
    mentions = message.mentions
    
    
    role_names = [r.name for  r in author.roles]
    if '@admin' not in role_names:
        await message.add_reaction('\U0001F44E')
        return "seuls les admins peuvent faire cette action!"
    
    args = shlex.split(content)
    
    parser = NonexitParser(description='arguments to teamup.')
    parser.add_argument('-n', dest='rolename', required=True)
    parser.add_argument('-chef', dest='teamleader', required=True)
    parser.add_argument('-membres', nargs='+', dest='members', required=True)
    
    
    
    try:
        ns = parser.parse_args(args=args[1:])
    except ValueError:
        await message.add_reaction('\U0001F44E')
        return "Erreur! La commande est du type `!teamup -n nom_de_lequipe -chef chef_de_projet -membres membre1 membre2 membre3`"
    
    
    serv_roles = await server.fetch_roles()
    if ns.rolename not in [r.name for r in serv_roles]:
        teamrole = await server.create_role(name=ns.rolename,
                                           mentionable=True,
                                           reason="admin through bot")
    else:
        await message.add_reaction('\U0001F44E')
        return f"L'équipe {ns.rolename} existe déjà."
        
    
    print("mentions: ",mentions)
    print('members: ', ns.teamleader, ns.members)
    for member in mentions:
        if str(member.id) in ns.teamleader:
            if 'chefdeproj' not in [r.name for r in serv_roles]:
                cdp_role = await server.create_role(name='chefdeproj',
                                           mentionable=True,
                                           reason="admin through bot")
            else:
                for r in serv_roles:
                    if r.name == 'chefdeproj':
                        cdp_role = r
                        break
            await member.add_roles(teamrole, cdp_role)
        else:
            await member.add_roles(teamrole)
    
    await message.add_reaction('\U0001F9BE')
    
    return "Tout le monde est rajouté, manque plus qu'un salon!"
    
    
        
    