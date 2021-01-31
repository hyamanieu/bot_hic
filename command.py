#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import discord
import shlex

#This class is useless now!
class Action_Picker():
    """
    A class supporting different kind of responses for different commands.
    commands always start with "!" followed by a single word
    
    Holds two types of actions :
        embeds: simply reacts to a message content by returning an Embed object.
        processors: make more complex actions (check user privileges!)
    """
    
    
    _list_embedactions = dict()#simply parsing
    _list_processors = dict()
    
    @classmethod
    def _assert_actions(cls, actions):
        assert type(actions) is dict, "must enter a dict"
        for k, v in actions.items():
            assert callable(v), "dict must contain functions"
            assert (type(k) is str) and (k.startswith('!')), "dict keys must be strings starting with '!'"
        
    
    def __init__(self, embeds= None, processors= None):
        if embeds:
            self.add_embed(embeds)
        if processors:
            self.add_processor(processors)
        
    def add_embed(self, embeds):
        self._assert_actions(embeds)
        self._list_embedactions.update(embeds)
        
    def add_processor(self, processors):
        self._assert_actions(processors)
        self._list_processors.update(processors)
    
    async def choix_action(self,message):
    
        #si on est dans un salon publique et si on ne commence pas par "!", alors on fait rien
        if str(message.channel.type) == "text":
            if not message.content.startswith("!"):
                return;
    
        
    
            
    
        #début de l'interprétation des commandes
        args = shlex.split(message.content)
    
        action_name = args[0]
        if action_name in self._list_embedactions: #check if it's in the list of Embeds
            action_emb = self._list_embedactions[action_name]
            embed = action_emb(*args)
            
            await message.channel.send(embed=embed)
    
        elif action_name in self._list_processors:
            proc = self._list_processors[action_name]
            response = await proc(message)
            
            await message.channel.send(response)
    
        else:       
            print("Instruction error")
            embed = discord.Embed()
            embed.title = "Erreur"
            embed.description = "Instruction non valable - Entrez `!aide` pour obtenir l'aide"
            await message.channel.send(embed=embed)



