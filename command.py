import discord
import shlex

async def choix_action(message):

    #si on est dans un salon publique et si on ne commence pas par "!", alors on fait rien
    if str(message.channel.type) == "text":
        if not message.content.startswith("!"):
            return;

    

    embed = discord.Embed()
        

    #début de l'interprétation des commandes
    args = shlex.split(message.content)

    ok = False

    if args[0] == "!aide": #aide
        embed.add_field(name="Aide",value=show_help())
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