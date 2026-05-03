import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import requests
import json
import os
from server import keep_alive

# Start the web server for 24/7 hosting
keep_alive()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

# ------------------------------
# Secure JSON file for teams
# ------------------------------
TEAMS_FILE = "teams.json"

if os.path.exists(TEAMS_FILE) and os.path.getsize(TEAMS_FILE) > 0:
    try:
        with open(TEAMS_FILE, "r") as f:
            user_teams = json.load(f)
    except json.JSONDecodeError:
        user_teams = {}
else:
    user_teams = {}

def save_teams():
    with open(TEAMS_FILE, "w") as f:
        json.dump(user_teams, f, indent=4)

# ------------------------------
# Helper function to get Pokémon info
# ------------------------------
def get_pokemon_data(pokemon_name):
    try:
        result = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}")
        if result.status_code != 200:
            return None
        return result.json()
    except:
        return None

# ------------------------------
# Type advantage function
# ------------------------------
type_advantage = {
    "fire": ["grass", "bug", "ice"],
    "water": ["fire", "ground", "rock"],
    "grass": ["water", "ground", "rock"],
    "electric": ["water", "flying"],
}

def advantage(poke1_types, poke2_types):
    score = 0
    for t1 in poke1_types:
        for t2 in poke2_types:
            if t2.lower() in type_advantage.get(t1.lower(), []):
                score += 1
            elif t1.lower() in type_advantage.get(t2.lower(), []):
                score -= 1
    return score

# ------------------------------
# Legacy commands
# ------------------------------
@bot.command()
async def test(ctx, *, text: str):
    await ctx.send(text)

@bot.command()
async def poke(ctx, *, pokemon: str):
    data = get_pokemon_data(pokemon)
    if not data:
        await ctx.send("❌ Pokémon not found 😅")
        return

    name = data["name"].title()
    types = ", ".join([t["type"]["name"].title() for t in data["types"]])
    stats_text = "\n".join([f"{s['stat']['name'].title()}: {s['base_stat']}" for s in data["stats"]])
    image_url = data["sprites"]["front_default"]

    msg = f"**{name} 🐾**\nType(s): {types}\nImage: {image_url}\n\nType `yes` to see stats or anything else to skip."
    await ctx.send(msg)

    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for('message', timeout=30.0, check=check)
        if reply.content.lower() == "yes":
            await ctx.send(f"**Stats of {name}:**\n{stats_text}")
        else:
            await ctx.send("⚡ Only image and type shown.")
    except:
        await ctx.send("⏱️ Time expired, stats not shown.")

# ------------------------------
# Slash commands
# ------------------------------
@bot.tree.command(name="poke", description="Shows info about a Pokémon")
@app_commands.describe(pokemon="Pokémon name")
async def slash_poke(interaction: discord.Interaction, pokemon: str):
    data = get_pokemon_data(pokemon)
    if not data:
        await interaction.response.send_message("❌ Pokémon not found 😅")
        return

    name = data["name"].title()
    types = [t["type"]["name"].title() for t in data["types"]]
    stats_text = "\n".join([f"{s['stat']['name'].title()}: {s['base_stat']}" for s in data["stats"]])
    image_url = data["sprites"]["front_default"]

    embed_base = discord.Embed(title=f"{name} 🐾", description=f"Type(s): {', '.join(types)}", color=0xFF0000)
    embed_base.set_thumbnail(url=image_url)

    view = View()
    btn_stats = Button(label="📊 Stats", style=discord.ButtonStyle.green)
    btn_shiny = Button(label="✨ Shiny", style=discord.ButtonStyle.blurple)
    btn_evol = Button(label="🔄 Evolutions", style=discord.ButtonStyle.gray)

    async def stats_callback(inter):
        embed_stats = embed_base.copy()
        embed_stats.add_field(name="Stats", value=stats_text, inline=False)
        await inter.response.edit_message(embed=embed_stats, view=view)

    async def shiny_callback(inter):
        shiny_url = data["sprites"]["front_shiny"]
        embed_shiny = embed_base.copy()
        embed_shiny.set_thumbnail(url=shiny_url)
        embed_shiny.title += " ✨ Shiny"
        await inter.response.edit_message(embed=embed_shiny, view=view)

    async def evol_callback(inter):
        species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon.lower()}"
        species_res = requests.get(species_url)
        
        if species_res.status_code != 200:
            await inter.response.send_message("❌ Species info not found")
            return
            
        species_data = species_res.json()
        evo_chain_url = species_data.get("evolution_chain", {}).get("url")
        if not evo_chain_url:
            await inter.response.send_message("❌ Evolution chain not found")
            return

        evo_data = requests.get(evo_chain_url).json()
        chain = evo_data.get("chain", {})

        def get_evolutions(chain_node):
            evols = [chain_node["species"]["name"].title()]
            for evo in chain_node.get("evolves_to", []):
                evols += get_evolutions(evo)
            return evols

        evolutions = get_evolutions(chain)
        embed_evol = discord.Embed(
            title=f"🔄 Evolutions of {pokemon.title()}",
            description=" → ".join(evolutions),
            color=0xAAAAAA
        )
        await inter.response.edit_message(embed=embed_evol, view=view)

    btn_stats.callback = stats_callback
    btn_shiny.callback = shiny_callback
    btn_evol.callback = evol_callback
    view.add_item(btn_stats)
    view.add_item(btn_shiny)
    view.add_item(btn_evol)

    await interaction.response.send_message(embed=embed_base, view=view)

# ------------------------------
# Team commands
# ------------------------------
@bot.tree.command(name="catch", description="Catch a Pokémon")
@app_commands.describe(pokemon="Pokémon name")
async def catch(interaction: discord.Interaction, pokemon: str):
    data = get_pokemon_data(pokemon)
    if not data:
        await interaction.response.send_message("❌ Pokémon not found")
        return

    user_teams.setdefault(str(interaction.user.id), [])
    user_teams[str(interaction.user.id)].append(pokemon.title())
    save_teams()

    image_url = data["sprites"]["front_default"]
    embed = discord.Embed(title=f"🎉 {pokemon.title()} caught!", color=0x00FF00)
    embed.set_image(url=image_url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="team", description="Show your team with images")
async def team(interaction: discord.Interaction):
    team_list = user_teams.get(str(interaction.user.id), [])
    if not team_list:
        await interaction.response.send_message("⚠️ You don't have any Pokémon yet")
        return

    await interaction.response.send_message("🎮 Your team:")

    for poke_name in team_list:
        data = get_pokemon_data(poke_name)
        if data:
            name = data["name"].title()
            image_url = data["sprites"]["front_default"]

            embed = discord.Embed(title=name, color=0xFFD700)
            embed.set_image(url=image_url)
            await interaction.followup.send(embed=embed)

@bot.tree.command(name="remove", description="Remove a Pokémon from your team")
@app_commands.describe(pokemon="Pokémon to remove")
async def remove(interaction: discord.Interaction, pokemon: str):
    team_list = user_teams.get(str(interaction.user.id), [])
    if pokemon.title() in team_list:
        team_list.remove(pokemon.title())
        save_teams()
        await interaction.response.send_message(f"🗑️ {pokemon.title()} removed from your team")
    else:
        await interaction.response.send_message("❌ Pokémon not found in your team")

@bot.tree.command(name="swap", description="Swap the positions of two Pokémon in your team")
@app_commands.describe(poke1="First Pokémon", poke2="Second Pokémon")
async def swap(interaction: discord.Interaction, poke1: str, poke2: str):
    team_list = user_teams.get(str(interaction.user.id), [])
    if poke1.title() in team_list and poke2.title() in team_list:
        i1 = team_list.index(poke1.title())
        i2 = team_list.index(poke2.title())
        team_list[i1], team_list[i2] = team_list[i2], team_list[i1]
        save_teams()
        await interaction.response.send_message(f"🔄 {poke1.title()} and {poke2.title()} swapped successfully")
    else:
        await interaction.response.send_message("❌ One or both Pokémon not in your team")

# ------------------------------
# VS command
# ------------------------------
@bot.tree.command(name="vs", description="Battle two Pokémon and show the winner")
@app_commands.describe(poke1="First Pokémon", poke2="Second Pokémon")
async def vs(interaction: discord.Interaction, poke1: str, poke2: str):
    data1 = get_pokemon_data(poke1)
    data2 = get_pokemon_data(poke2)
    if not data1 or not data2:
        await interaction.response.send_message("❌ Pokémon not found 😅")
        return

    name1 = data1["name"].title()
    name2 = data2["name"].title()
    types1 = [t["type"]["name"] for t in data1["types"]]
    types2 = [t["type"]["name"] for t in data2["types"]]

    stats1 = sum([s['base_stat'] for s in data1["stats"]])
    stats2 = sum([s['base_stat'] for s in data2["stats"]])

    adv = advantage(types1, types2)
    total1 = stats1 + adv*10
    total2 = stats2 - adv*10

    if total1 > total2:
        winner = f"🏆 {name1} wins!"
    elif total2 > total1:
        winner = f"🏆 {name2} wins!"
    else:
        winner = "🤝 It's a tie!"

    embed = discord.Embed(title=f"{name1} 🆚 {name2}", color=0xFFFF00)
    embed.add_field(name="Result", value=winner, inline=False)
    embed.set_thumbnail(url=data1["sprites"]["front_default"])
    await interaction.response.send_message(embed=embed)

# ------------------------------
# on_ready event
# ------------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced slash commands: {len(synced)}")
    except Exception as e:
        print(f"Sync Error: {e}")

import time

while True:
    try:
        bot.run(TOKEN, reconnect=True)
    except Exception as e:
        print(f"Error: {e}")
        print("Restarting in 5 seconds...")
        time.sleep(5)
