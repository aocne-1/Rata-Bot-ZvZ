import discord
import os
import time
import aiohttp
from discord.ext import tasks, commands
from collections import defaultdict

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = 1512160099358085161
map_activity = defaultdict(list)
already_posted_events = set()

@bot.event
async def on_ready():
    print(f'RADAR ULTRA-RATA DE ZvZ ENCENDIDO')
    detect_zvz.start()

@tasks.loop(seconds=20)
async def detect_zvz():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    url = "https://gameinfo.albiononline.com/api/gameinfo/events?limit=50"
    current_time = time.time()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    events = await response.json()
                    for event in events:
                        event_id = event.get("EventId")
                        if event_id in already_posted_events:
                            continue
                        
                        location = event.get("Location")
                        if not location:
                            continue

                        map_activity[location].append(current_time)
                        already_posted_events.add(event_id)

                    for map_name, timestamps in list(map_activity.items()):
                        recent_kills = [t for t in timestamps if current_time - t < 300]
                        map_activity[map_name] = recent_kills

                        if len(recent_kills) >= 15:
                            for event in events:
                                if event.get("Location") == map_name:
                                    killer = event.get("Killer", {})
                                    victim = event.get("Victim", {})
                                    k_guild = killer.get("GuildName", "Sin Gremio")
                                    v_guild = victim.get("GuildName", "Sin Gremio")
                                    k_alliance = killer.get("AllianceName", "")
                                    v_alliance = victim.get("AllianceName", "")
                                    k_info = f"[{k_alliance}] {k_guild}" if k_alliance else f"{k_guild}"
                                    v_info = f"[{v_alliance}] {v_guild}" if v_alliance else f"{v_guild}"

                                    embed = discord.Embed(
                                        title="🚨 ALERTA DE GUERRA TOTAL (15+ KILLS) 🚨",
                                        description="¡Se están despedazando! El suelo está tapado en bolsas.",
                                        color=discord.Color.dark_red()
                                    )
                                    embed.add_field(name="📍 Zona de Choque", value=f"**{map_name}**", inline=False)
                                    embed.add_field(name="⚔️ Choque de Blobs", value=f"🔴 **{k_info}** vs 🔵 **{v_info}**", inline=False)
                                    embed.add_field(name="💀 Reporte de Bajas", value=f"**{len(recent_kills)} muertos** detectados.", inline=True)
                                    embed.add_field(name="🔥 Estrategia", value="Montura de carga, set invisible y a ratear!", inline=False)
                                    
                                    await channel.send(embed=embed)
                                    map_activity[map_name] = []
                                    break
        except Exception:
            pass

bot.run(os.environ['DISCORD_TOKEN'])