#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 14:57:28 2021

@author: hyamanieu
"""
import bs4
import urllib.request
import discord

import requests
from pdfminer.high_level import extract_text
from io import BytesIO


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
    server = message.guild
    content = message.content
    
    role_names = [r.name for  r in author.roles]
    if '@admin' in role_names:
        await message.add_reaction('\U0001F9BE')
        return f"T'es {role_names}!"
    else:
        await message.add_reaction('\U0001F44E')
        return f"T'es {role_names}!"
        
        
        
    