import discord
import asyncio
import threading
import os
import traceback
from flask import Flask

TOKEN = os.environ.get("TOKEN", "")
CHANNEL_ID_STR = os.environ.get("CHANNEL_ID", "0")

print(f"🔧 TOKEN uzunluğu: {len(TOKEN)} karakter")
print(f"🔧 CHANNEL_ID degeri: {CHANNEL_ID_STR}")

try:
    CHANNEL_ID = int(CHANNEL_ID_STR)
except ValueError:
    print(f"❌ CHANNEL_ID gecersiz: '{CHANNEL_ID_STR}'")
    CHANNEL_ID = 0

if not TOKEN:
    print("❌ TOKEN bos! Environment variable eksik.")

# --- Keep-alive web sunucusu ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot calisiyor!"

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
    try:
        channel = client.get_channel(CHANNEL_ID)
        if channel is None or not isinstance(channel, discord.VoiceChannel):
            print(f"❌ Ses kanali bulunamadi! CHANNEL_ID={CHANNEL_ID}")
            return
        if voice_client and voice_client.is_connected():
            return
        voice_client = await channel.connect(self_deaf=True, self_mute=True)
        print(f"✅ Baglandi → {channel.name}")
    except Exception as e:
        print(f"⚠️ Baglanti hatasi: {e}")
        traceback.print_exc()


async def keep_alive_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(30)
        if voice_client is None or not voice_client.is_connected():
            print("🔄 Yeniden baglanıyor...")
            await join_and_stay()


@client.event
async def on_ready():
    print(f"🤖 {client.user} aktif!")
    await join_and_stay()


@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user:
        if before.channel is not None and after.channel is None:
            print("⚡ Kanaldan cıkarıldı, geri giriyor...")
            await asyncio.sleep(3)
            await join_and_stay()


async def main():
    try:
        async with client:
            asyncio.create_task(keep_alive_loop())
            await client.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Token gecersiz! Discord'a giris yapilamadi.")
    except Exception as e:
        print(f"❌ Ana dongu hatasi: {e}")
        traceback.print_exc()


keep_alive()
asyncio.run(main())
