import discord
import asyncio
import threading
import os
from flask import Flask

# ============================================================
#  AYARLAR — Render'da Environment Variables'tan okunur
# ============================================================
TOKEN = os.environ.get("TOKEN", "BOT_TOKEN_BURAYA")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))
# ============================================================

# --- Keep-alive web sunucusu (Render için şart) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot çalışıyor!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

# --- Discord Bot ---
intents = discord.Intents.default()
intents.voice_states = True

client = discord.Client(intents=intents)
voice_client = None


async def join_and_stay():
    global voice_client
    channel = client.get_channel(CHANNEL_ID)

    if channel is None or not isinstance(channel, discord.VoiceChannel):
        print("❌ Ses kanalı bulunamadı! CHANNEL_ID'yi kontrol et.")
        return

    try:
        if voice_client and voice_client.is_connected():
            return
        voice_client = await channel.connect(self_deaf=True, self_mute=True)
        print(f"✅ Bağlandı → {channel.name}")
    except Exception as e:
        print(f"⚠️ Bağlantı hatası: {e}")


async def keep_alive_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(30)
        if voice_client is None or not voice_client.is_connected():
            print("🔄 Yeniden bağlanıyor...")
            await join_and_stay()


@client.event
async def on_ready():
    print(f"🤖 {client.user} aktif!")
    await join_and_stay()


@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user:
        if before.channel is not None and after.channel is None:
            print("⚡ Kanaldan çıkarıldı, geri giriyor...")
            await asyncio.sleep(3)
            await join_and_stay()


async def main():
    async with client:
        asyncio.get_event_loop().create_task(keep_alive_loop())
        await client.start(TOKEN)


keep_alive()
asyncio.run(main())
