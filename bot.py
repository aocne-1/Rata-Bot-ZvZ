import os
import discord
from discord.ext import commands, tasks
import aiohttp
import time
from collections import defaultdict

# --- CONFIGURACIÓN ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID = 1552160899350885161
map_activity = defaultdict(list)
already_posted_events = set()

# --- LÓGICA DEL BOT ---
@bot.event
async def on_ready():
    print(f'Bot iniciado como {bot.user}')
    if not detect_zvz.is_running():
        detect_zvz.start()

@tasks.loop(seconds=20)
async def detect_zvz():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    url = "https://gameinfo.albiononline.com/api/gameinfo/events?limit=50"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return
                events = await response.json()
    except Exception:
        return

    for event in reversed(events):
        event_id = event.get('EventId')
        if event_id in already_posted_events:
            continue
        
        # Filtro de lógica (ej. kills >= 15)
        # Aquí iría tu lógica de procesamiento...
        
        already_posted_events.add(event_id)
        # ... lógica para crear el embed y enviar el mensaje ...
        # await channel.send(embed=embed)

# --- EJECUCIÓN ---
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("No se ha configurado el DISCORD_TOKEN en las variables de entorno.")

bot.run(token)
