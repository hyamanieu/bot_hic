import discord
import shlex



class Action_Picker():
    _list_actions = dict()
    
    @classmethod
    def _assert_actions(cls, actions):
        assert type(actions) is dict, "must enter a dict"
        for k, v in actions.items():
            assert callable(v), "dict must contain functions"
            assert (type(k) is str) and (k.startswith('!')), "dict keys must be strings starting with '!'"
        
    
    def __init__(self, actions):
        self._assert_actions(actions)
        self._list_actions.update(actions)
        
    def add_actions(self, actions):
        self._assert_actions(actions)
        self._list_actions.update(actions)
        
    
    async def choix_action(self,message):
    
        #si on est dans un salon publique et si on ne commence pas par "!", alors on fait rien
        if str(message.channel.type) == "text":
            if not message.content.startswith("!"):
                return;
    
        
    
        embed = discord.Embed()
            
    
        #début de l'interprétation des commandes
        args = shlex.split(message.content)
    
        ok = False
        action_name = args[0]
        if action_name in self._list_actions: #aide
            action_func = self._list_actions[action_name]
            field_name = action_name[1:].capitalize()
            embed.add_field(name=field_name,value=action_func())
            await message.channel.send(embed=embed)
            ok = True
    
    
    
        if not ok:       
            print("Instruction error")
            embed.title = "Erreur"
            embed.description = "Instruction non valable - Entrez `!aide` pour obtenir l'aide"
            await message.channel.send(embed=embed)





def show_help():
    msg = ""
    msg += "==== Hacking Industry Camp - AIDE ====\n"
    msg += "- `!aide` : obtenir l'aide\n"

    return msg