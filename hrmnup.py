"""
Basit Moderasyon Discord Botu
------------------------------
Gereksinim: pip install discord.py
Çalıştırma: python bot.py
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import os
import requests
import json
import time
import random
import asyncio



# ---------------------------------------------------------
# AYARLAR
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# Spotify Developer Dashboard'dan aldığın Client ID ve Client Secret
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
 
# Takip edilecek sanatçılar (istediğin zaman /sanatciekle ile yenilerini ekleyebilirsin)
DEFAULT_ARTISTS = ["Uzi", "Motive", "Lvbel C5"]

# /sarıl komutunda kullanılacak gif linki (istediğin gif linkini buraya yapıştır)
HUG_GIF_URL = "https://media.tenor.com/MFde88T3ZiYAAAAM/peter-parker.gif"

# /eek komutunda gösterilecek fotoğraf linki (kendi fotoğrafının linkini buraya yapıştır)
EEK_IMAGE_URL = "https://cdn.discordapp.com/attachments/1480282779878031613/1524199293941190696/hmr.png?ex=6a577275&is=6a5620f5&hm=8b9d4c45aefac204cac2bd8570a463f3b99460b7142689b0817cdf82b829b629&"
 
 # /ates komutunda gösterilecek fotoğraf linki (kendi fotoğrafının linkini buraya yapıştır)
ATES_IMAGE_URL = "https://cdn.discordapp.com/attachments/1480664155752108285/1526563685257183252/image.png?ex=6a577ab8&is=6a562938&hm=54b57ef3c6ebe1cd7d5917b7b88ad2cc23c57002da3791739cb9e2e9fe016222&"

# Bot açılınca otomatik gireceği ses kanalının ID'si (0 ise otomatik girmez)
AUTO_JOIN_VOICE_CHANNEL_ID = 1526566385520476171

WARNING_ROLES = {
    1: 1485322965334622319,  # 1. Uyarı
    2: 1485324082441359652,  # 2. Uyarı
    3: 1485324272909160603,  # 3. Uyarı
    4: 1494313034657693847,  # 4. Uyarı
    5: 1494313375130189975,  # 5. Uyarı
    6: 1494313472505286866,  # 6. Uyarı
}

COIN_FILE = "coins.json"
INVENTORY_FILE = "inventory.json"
DAILY_FILE = "daily.json"
ROD_FILE = "rods.json"
MISSION_FILE = "missions.json"
WARNINGS_FILE = "warnings.json"

BALIKLAR = [

    # Common
    ("🐟 Hamsi", 3500, 20, 40),
    ("🐠 Sardalya", 2500, 30, 50),
    ("🐟 İstavrit", 1800, 40, 70),
    ("🐡 Mezgit", 1200, 60, 90),

    # Uncommon
    ("🐠 Çipura", 700, 90, 130),
    ("🐟 Lüfer", 500, 120, 180),
    ("🐠 Palamut", 350, 160, 240),

    # Rare
    ("🐡 Levrek", 180, 220, 320),
    ("🦑 Kalamar", 120, 300, 450),
    ("🐙 Ahtapot", 80, 400, 600),

    # Epic
    ("🦀 Yengeç", 45, 600, 900),
    ("🦞 Istakoz", 25, 900, 1300),
    ("🦈 Köpekbalığı", 12, 1400, 1900),

    # Legendary
    ("🐬 Yunus", 6, 2500, 3500),
    ("🐋 Balina", 3, 5000, 7000),

    # Mythic
    ("👑 Altın Balık", 1, 12000, 18000),

    # Divine
    ("💎 Kristal Balık", 0.3, 25000, 35000),
    ("🔥 Lav Balığı", 0.2, 35000, 50000),
    ("👻 Hayalet Balık", 0.1, 50000, 70000),
    ("🌊 Poseidon'un Balığı", 0.03, 90000, 120000),
    ("👑 Leviathan", 0.005, 250000, 400000),
]

RODS = {
    "Tahta Olta": {
        "fiyat": 0,
        "bonus": 0
    },

    "Demir Olta": {
        "fiyat": 5000,
        "bonus": 5
    },

    "Altın Olta": {
        "fiyat": 20000,
        "bonus": 10
    },

    "Elmas Olta": {
        "fiyat": 75000,
        "bonus": 20
    },

    "Efsane Olta": {
        "fiyat": 250000,
        "bonus": 35
    }
}

SLOT_ITEMS = [
    "🍒",
    "🍋",
    "🍇",
    "🍉",
    "⭐",
    "💎"
]



intents = discord.Intents.default()
intents.members = True  # Üye bilgilerine erişim için gerekli (Developer Portal'da da açman lazım)
 
bot = commands.Bot(command_prefix="!", intents=intents)
 
# Basit bir hafızada uyarı sistemi: {user_id: [uyarı1, uyarı2, ...]}
warnings: dict[int, list[str]] = {}
 
 # Aktif sayı tahmin oyunları: {channel_id: {"number": int, "min": int, "max": int, "attempts": int}}
guess_games: dict[int, dict] = {}

MUSIC_DATA_FILE = "music_data.json"
GAMES_DATA_FILE = "games_data.json"

intents = discord.Intents.default()
intents.members = True  # Üye bilgilerine erişim için gerekli (Developer Portal'da da açman lazım)

bot = commands.Bot(command_prefix="!", intents=intents)

# Basit bir hafızada uyarı sistemi: {user_id: [uyarı1, uyarı2, ...]}
warnings: dict[int, list[str]] = {}


# ---------------------------------------------------------
# MÜZİK TAKİP VERİSİNİ DOSYADAN OKUMA / YAZMA
# ---------------------------------------------------------
def load_music_data() -> dict:
    default_data = {
        "music_channel_id": None,
        "artists": {}
    }

    if not os.path.exists(MUSIC_DATA_FILE):
        return default_data

    try:
        with open(MUSIC_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            if "music_channel_id" not in data:
                data["music_channel_id"] = None

            if "artists" not in data:
                data["artists"] = {}

            return data

    except json.JSONDecodeError:
        # Dosya boş veya bozuksa sıfırla
        with open(MUSIC_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)

        return default_data


def save_music_data(data: dict) -> None:
    with open(MUSIC_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


music_data = load_music_data()
 
 # ---------------------------------------------------------
# ÜCRETSİZ OYUN TAKİP VERİSİNİ DOSYADAN OKUMA / YAZMA
# ---------------------------------------------------------
def load_games_data() -> dict:
    if not os.path.exists(GAMES_DATA_FILE):
        return {"games_channel_id": None, "known_ids": []}
    with open(GAMES_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
 
 
def save_games_data(data: dict) -> None:
    with open(GAMES_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
 
 
games_data = load_games_data()

def fetch_free_games():
    """GamerPower API'den ücretsiz oyunları güvenli şekilde çeker."""

    url = "https://www.gamerpower.com/api/giveaways"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            print("API beklenmeyen cevap verdi:", data)
            return []

        games = []

        for game in data:
            if not isinstance(game, dict):
                continue

            platform = str(game.get("platforms", "")).lower()
            title = str(game.get("title", "")).lower()
            description = str(game.get("description", "")).lower()
            giveaway_type = str(game.get("type", "")).lower()
            worth = str(game.get("worth", "")).lower()

            # Sadece Steam ve Epic
            if "steam" not in platform and "epic" not in platform:
                continue

            # Değeri olmayanları alma
            if worth == "n/a":
                continue

            # İstenmeyen giveaway türleri
            blacklist = [
                "key",
                "bundle",
                "dlc",
                "skin",
                "pack",
                "starter pack",
                "beta",
                "playtest",
                "closed beta",
                "open beta",
                "test",
                "demo",
                "currency",
                "coins",
                "loot",
                "weapon",
                "weapons",
                "cosmetic",
                "subscription",
            ]

            text = f"{title} {description} {giveaway_type}"

            if any(word in text for word in blacklist):
                continue

            games.append(game)

        return games

    except Exception as e:
        print("GamerPower hatası:", e)
        return []
 
 
 
# ---------------------------------------------------------
# SPOTIFY API YARDIMCILARI
# ---------------------------------------------------------
_spotify_token = {"access_token": None, "expires_at": 0}
 
 
def get_spotify_token() -> str:
    """Client Credentials akışıyla Spotify erişim token'ı alır (gerekirse yeniler)."""
    if _spotify_token["access_token"] and time.time() < _spotify_token["expires_at"] - 30:
        return _spotify_token["access_token"]
 
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    _spotify_token["access_token"] = payload["access_token"]
    _spotify_token["expires_at"] = time.time() + payload["expires_in"]
    return _spotify_token["access_token"]
 
 
def spotify_search_artist(name: str) -> dict | None:
    """İsme göre Spotify'da sanatçı arar, en iyi eşleşmeyi döndürür."""
    token = get_spotify_token()
    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": name, "type": "artist", "limit": 1},
        timeout=10,
    )
    response.raise_for_status()
    items = response.json()["artists"]["items"]
    return items[0] if items else None
 
 
def spotify_latest_release(artist_id: str) -> dict | None:
    """Bir sanatçının en son çıkardığı albüm/single'ı döndürür."""
    token = get_spotify_token()
    response = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}/albums",
        headers={"Authorization": f"Bearer {token}"},
        params={"include_groups": "album,single", "market": "TR", "limit": 10},
        timeout=10,
    )
    response.raise_for_status()
    items = response.json()["items"]
    if not items:
        return None
    # En yeni çıkışı bulmak için tarihe göre sırala
    items.sort(key=lambda x: x["release_date"], reverse=True)
    return items[0]

# ==============================
# COIN
# ==============================

def load_coins():
    if not os.path.exists(COIN_FILE):
        return {}

    with open(COIN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_coins(data):
    with open(COIN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_coin(user_id):
    data = load_coins()
    return data.get(str(user_id), 0)


def add_coin(user_id, amount):
    data = load_coins()

    uid = str(user_id)

    if uid not in data:
        data[uid] = 0

    data[uid] += amount

    save_coins(data)


def remove_coin(user_id, amount):
    data = load_coins()

    uid = str(user_id)

    if uid not in data:
        data[uid] = 0

    data[uid] -= amount

    if data[uid] < 0:
        data[uid] = 0

    save_coins(data)

    # ==============================
# ENVANTER
# ==============================

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return {}

    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_inventory(data):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def add_item(user_id, item, amount=1):
    data = load_inventory()

    uid = str(user_id)

    if uid not in data:
        data[uid] = {}

    data[uid][item] = data[uid].get(item, 0) + amount

    save_inventory(data)


def get_inventory(user_id):
    data = load_inventory()

    return data.get(str(user_id), {})

def remove_item(user_id, item, amount=1):
    data = load_inventory()

    uid = str(user_id)

    if uid not in data:
        return

    if item not in data[uid]:
        return

    data[uid][item] -= amount

    if data[uid][item] <= 0:
        del data[uid][item]

    save_inventory(data)

# ==============================
# GÜNLÜK
# ==============================

def load_daily():
    if not os.path.exists(DAILY_FILE):
        return {}

    with open(DAILY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_daily(data):
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ==============================
# OLTALAR
# ==============================

def load_rods():
    if not os.path.exists(ROD_FILE):
        return {}

    with open(ROD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_rods(data):
    with open(ROD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_rod(user_id):
    data = load_rods()
    return data.get(str(user_id), "Tahta Olta")


def set_rod(user_id, rod):
    data = load_rods()
    data[str(user_id)] = rod
    save_rods(data)

    # ==============================
# WARNINGS
# ==============================

def load_warnings():
    if not os.path.exists(WARNINGS_FILE):
        return {}

    with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_warnings(data):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# WELCOME
WELCOME_DATA_FILE = "welcome_data.json"
 
 
def load_welcome_data() -> dict:
    if not os.path.exists(WELCOME_DATA_FILE):
        return {"welcome_channel_id": None}
    with open(WELCOME_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
 
 
def save_welcome_data(data: dict) -> None:
    with open(WELCOME_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
 
 
welcome_data = load_welcome_data()
 
# ---------------------------------------------------------
# BOT HAZIR OLDUĞUNDA
# ---------------------------------------------------------
@bot.event
async def on_ready():


    activity = discord.Streaming(
        name="discord.gg/hrmn | /komutlar",
        url="https://www.twitch.tv/discord"  # Geçerli bir Twitch URL'si
    )

    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash komut senkronize edildi.")
    except Exception as e:
        print(f"Senkronizasyon hatası: {e}")
    print(f"Giriş yapıldı: {bot.user} (ID: {bot.user.id})")

    if not check_new_releases.is_running():
       check_new_releases.start()

    if not check_free_games.is_running():
        check_free_games.start()

    if AUTO_JOIN_VOICE_CHANNEL_ID:
        channel = bot.get_channel(AUTO_JOIN_VOICE_CHANNEL_ID)
        if channel is not None:
            try:
                await channel.connect()
                print(f"Otomatik olarak '{channel.name}' ses kanalına girildi.")
            except Exception as e:
                print(f"Ses kanalına otomatik girerken hata oluştu: {e}")
        else:
            print("UYARI: AUTO_JOIN_VOICE_CHANNEL_ID ile eşleşen bir kanal bulunamadı.")

    print("Bot hazır!")
# ---------------------------------------------------------
# YARDIMCI FONKSİYON: Yetki kontrolü
# ---------------------------------------------------------
def has_permission(interaction: discord.Interaction, permission: str) -> bool:
    return getattr(interaction.user.guild_permissions, permission, False)


# ---------------------------------------------------------
# /kick
# ---------------------------------------------------------
@bot.tree.command(name="kick", description="Bir kullanıcıyı sunucudan atar")
@app_commands.describe(member="Atılacak kullanıcı", reason="Atma sebebi")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    if not has_permission(interaction, "kick_members"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("Bu kullanıcıyı atamazsın (rolü senden yüksek veya eşit).", ephemeral=True)
        return

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 **{member}** sunucudan atıldı.\nSebep: {reason}")


# ---------------------------------------------------------
# /ban
# ---------------------------------------------------------
@bot.tree.command(name="ban", description="Bir kullanıcıyı sunucudan yasaklar")
@app_commands.describe(member="Yasaklanacak kullanıcı", reason="Yasaklama sebebi")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep belirtilmedi"):
    if not has_permission(interaction, "ban_members"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("Bu kullanıcıyı yasaklayamazsın (rolü senden yüksek veya eşit).", ephemeral=True)
        return

    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 **{member}** sunucudan yasaklandı.\nSebep: {reason}")


# ---------------------------------------------------------
# /unban
# ---------------------------------------------------------
@bot.tree.command(name="unban", description="Bir kullanıcının yasağını kaldırır (kullanıcı ID'si ile)")
@app_commands.describe(user_id="Yasağı kaldırılacak kullanıcının ID'si")
async def unban(interaction: discord.Interaction, user_id: str):
    if not has_permission(interaction, "ban_members"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ **{user}** kullanıcısının yasağı kaldırıldı.")
    except ValueError:
        await interaction.response.send_message("Geçerli bir kullanıcı ID'si gir.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("Bu kullanıcı yasaklı değil ya da bulunamadı.", ephemeral=True)


# ---------------------------------------------------------
# /mute (timeout)
# ---------------------------------------------------------
@bot.tree.command(name="mute", description="Bir kullanıcıyı belirli süre susturur")
@app_commands.describe(member="Susturulacak kullanıcı", minutes="Kaç dakika susturulacak", reason="Susturma sebebi")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Sebep belirtilmedi"):
    if not has_permission(interaction, "moderate_members"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 **{member}** {minutes} dakika susturuldu.\nSebep: {reason}")


# ---------------------------------------------------------
# /unmute
# ---------------------------------------------------------
@bot.tree.command(name="unmute", description="Bir kullanıcının susturmasını kaldırır")
@app_commands.describe(member="Susturması kaldırılacak kullanıcı")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not has_permission(interaction, "moderate_members"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    await member.timeout(None)
    await interaction.response.send_message(f"🔊 **{member}** kullanıcısının susturması kaldırıldı.")


# ---------------------------------------------------------
# /clear
# ---------------------------------------------------------
@bot.tree.command(name="clear", description="Kanaldaki belirli sayıda mesajı siler")
@app_commands.describe(amount="Silinecek mesaj sayısı (1-100)")
async def clear(interaction: discord.Interaction, amount: int):
    if not has_permission(interaction, "manage_messages"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    if amount < 1 or amount > 100:
        await interaction.response.send_message("1 ile 100 arasında bir sayı gir.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 {len(deleted)} mesaj silindi.", ephemeral=True)


@bot.tree.command(name="warn", description="Bir kullanıcıya uyarı verir")
@app_commands.describe(member="Uyarılacak kullanıcı", reason="Uyarı sebebi")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not has_permission(interaction, "kick_members"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    warnings = load_warnings()

    uid = str(member.id)

    if uid not in warnings:
        warnings[uid] = []

    warnings[uid].append(reason)
    save_warnings(warnings)

    count = len(warnings[uid])

    # Eski uyarı rollerini kaldır
    for role_id in WARNING_ROLES.values():
        role = interaction.guild.get_role(role_id)
        if role and role in member.roles:
            await member.remove_roles(role)

    # Yeni rol
    if count in WARNING_ROLES:
        role = interaction.guild.get_role(WARNING_ROLES[count])
        if role:
            await member.add_roles(role)

    await interaction.response.send_message(
        f"⚠️ {member.mention} uyarıldı.\n"
        f"Toplam uyarı: **{count}**\n"
        f"Sebep: **{reason}**"
    )

@bot.tree.command(name="unwarn", description="Bir kullanıcının uyarısını kaldırır")
@app_commands.describe(member="Uyarısı kaldırılacak kullanıcı", reason="Silinecek uyarı")
async def unwarn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not has_permission(interaction, "kick_members"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return

    warnings = load_warnings()

    uid = str(member.id)

    if uid not in warnings:
        await interaction.response.send_message("Bu kullanıcının hiç uyarısı yok.", ephemeral=True)
        return

    if reason not in warnings[uid]:
        await interaction.response.send_message("Bu sebepte bir uyarı bulunamadı.", ephemeral=True)
        return

    warnings[uid].remove(reason)

    if len(warnings[uid]) == 0:
        del warnings[uid]

    save_warnings(warnings)

    count = len(warnings.get(uid, []))

    # Eski rolleri kaldır
    for role_id in WARNING_ROLES.values():
        role = interaction.guild.get_role(role_id)
        if role and role in member.roles:
            await member.remove_roles(role)

    # Yeni rol
    if count in WARNING_ROLES:
        role = interaction.guild.get_role(WARNING_ROLES[count])
        if role:
            await member.add_roles(role)

    await interaction.response.send_message(
        f"✅ {member.mention} kullanıcısının uyarısı kaldırıldı."
    )

@bot.tree.command(name="warnings", description="Kullanıcının uyarılarını gösterir")
@app_commands.describe(member="Uyarıları görüntülenecek kullanıcı")
async def warnings_cmd(interaction: discord.Interaction, member: discord.Member):

    warnings = load_warnings()

    uid = str(member.id)

    if uid not in warnings:
        await interaction.response.send_message(
            f"{member.mention} kullanıcısının hiç uyarısı yok."
        )
        return

    text = ""

    for i, reason in enumerate(warnings[uid], start=1):
        text += f"**{i}.** {reason}\n"

    embed = discord.Embed(
        title=f"⚠️ {member.display_name} Uyarıları",
        description=text,
        color=discord.Color.orange()
    )

    embed.set_footer(text=f"Toplam {len(warnings[uid])} uyarı")

    await interaction.response.send_message(embed=embed)

# ---------------------------------------------------------
# /setmuzikkanali - bildirimlerin gideceği kanalı ayarlar
# ---------------------------------------------------------

@bot.tree.command(name="setmuzikkanali", description="Yeni şarkı bildirimlerinin gönderileceği kanalı ayarlar")
@app_commands.describe(channel="Bildirimlerin gönderileceği kanal")
async def set_music_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not has_permission(interaction, "manage_guild"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return
 
    music_data["music_channel_id"] = channel.id
    save_music_data(music_data)
    await interaction.response.send_message(f"✅ Müzik bildirimleri artık {channel.mention} kanalına gönderilecek.")
# ---------------------------------------------------------
# /sanatciekle - takip listesine yeni sanatçı ekler
# ---------------------------------------------------------
@bot.tree.command(name="sanatciekle", description="Takip edilecek listeye yeni bir sanatçı ekler")
@app_commands.describe(isim="Spotify'daki sanatçı ismi (örn. Uzi, Motive, Lvbel C5)")
async def add_artist(interaction: discord.Interaction, isim: str):
    if not has_permission(interaction, "manage_guild"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return
 
    await interaction.response.defer()
 
    try:
        artist = spotify_search_artist(isim)
    except requests.exceptions.RequestException as e:
        await interaction.followup.send(f"Spotify'a bağlanırken hata oluştu: {e}")
        return
 
    if not artist:
        await interaction.followup.send(f"'{isim}' isminde bir sanatçı bulunamadı.")
        return
 
    artist_id = artist["id"]
    artist_name = artist["name"]
 
    # Baseline: mevcut en son çıkışı kaydet, böylece eklendiği anda eski şarkı için bildirim atmaz
    latest = spotify_latest_release(artist_id)
    last_release_id = latest["id"] if latest else None
 
    music_data["artists"][artist_id] = {
        "name": artist_name,
        "last_release_id": last_release_id,
    }
    save_music_data(music_data)
 
    await interaction.followup.send(
        f"🎵 **{artist_name}** takip listesine eklendi! Yeni bir şarkı çıkardığında haber vereceğim."
    )
 
 
# ---------------------------------------------------------
# /sanatcilistesi - takip edilen sanatçıları gösterir
# ---------------------------------------------------------
@bot.tree.command(name="sanatcilistesi", description="Takip edilen sanatçıları listeler")
async def list_artists(interaction: discord.Interaction):
    artists = music_data.get("artists", {})
    if not artists:
        await interaction.response.send_message("Henüz takip edilen sanatçı yok. `/sanatciekle` ile ekleyebilirsin.")
        return
 
    names = "\n".join(f"- {info['name']}" for info in artists.values())
    await interaction.response.send_message(f"🎤 Takip edilen sanatçılar:\n{names}")
 
 
# ---------------------------------------------------------
# /sanatcisil - takip listesinden sanatçı çıkarır
# ---------------------------------------------------------
@bot.tree.command(name="sanatcisil", description="Takip listesinden bir sanatçıyı çıkarır")
@app_commands.describe(isim="Silinecek sanatçının ismi")
async def remove_artist(interaction: discord.Interaction, isim: str):
    if not has_permission(interaction, "manage_guild"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return
 
    artists = music_data.get("artists", {})
    match_id = None
    for artist_id, info in artists.items():
        if info["name"].lower() == isim.lower():
            match_id = artist_id
            break
 
    if not match_id:
        await interaction.response.send_message(f"'{isim}' takip listesinde bulunamadı.", ephemeral=True)
        return
 
    removed_name = artists[match_id]["name"]
    del artists[match_id]
    save_music_data(music_data)
    await interaction.response.send_message(f"🗑️ **{removed_name}** takip listesinden çıkarıldı.")

    # ---------------------------------------------------------
# /zar - iki sayı arasında rastgele bir sayı seçer
# ---------------------------------------------------------
@bot.tree.command(name="zar", description="Belirlediğin iki sayı arasında rastgele bir sayı seçer")
@app_commands.describe(min_deger="En küçük sayı", max_deger="En büyük sayı")
async def zar(interaction: discord.Interaction, min_deger: int, max_deger: int):
    if min_deger > max_deger:
        min_deger, max_deger = max_deger, min_deger
 
    sonuc = random.randint(min_deger, max_deger)
    await interaction.response.send_message(f"🎲 **{sonuc}**")
 
 
# ---------------------------------------------------------
# ARKA PLAN GÖREVİ: saatte bir yeni şarkı kontrolü
# ---------------------------------------------------------
@tasks.loop(hours=6)
async def check_new_releases():
    channel_id = music_data.get("music_channel_id")
    if not channel_id:
        return  # Kanal henüz ayarlanmamış
 
    channel = bot.get_channel(channel_id)
    if channel is None:
        return
 
    for artist_id, info in list(music_data.get("artists", {}).items()):
        try:
            latest = spotify_latest_release(artist_id)
        except requests.exceptions.RequestException as e:
            print(f"Spotify kontrol hatası ({info['name']}): {e}")
            continue
 
        if not latest:
            continue
 
        if latest["id"] != info.get("last_release_id"):
            info["last_release_id"] = latest["id"]
            save_music_data(music_data)
 
            cover_url = latest["images"][0]["url"] if latest.get("images") else None
            embed = discord.Embed(
                title=f"🎶 {info['name']} yeni bir şarkı çıkardı!",
                description=f"**{latest['name']}**\nÇıkış tarihi: {latest['release_date']}",
                url=latest["external_urls"]["spotify"],
                color=discord.Color.green(),
            )
            if cover_url:
                embed.set_thumbnail(url=cover_url)
 
            await channel.send(embed=embed)
 
 # ---------------------------------------------------------
# /sarıl - bir kullanıcıya sarılma komutu
# ---------------------------------------------------------
@bot.tree.command(name="sarıl", description="Bir kullanıcıya sarıl!")
@app_commands.describe(kullanici="Sarılmak istediğin kullanıcı")
async def hug(interaction: discord.Interaction, kullanici: discord.Member):
    if HUG_GIF_URL == "HUG_GIF_URL":
        await interaction.response.send_message(
            "Henüz bir gif linki ayarlanmamış. bot.py içindeki HUG_GIF_URL değişkenine bir link yapıştır.",
            ephemeral=True,
        )
        return
 
    embed = discord.Embed(
        description=f"🤗 {interaction.user.mention} ve {kullanici.mention} sarıldı!",
        color=discord.Color.from_rgb(255, 182, 193),
    )
    embed.set_image(url=HUG_GIF_URL)
    await interaction.response.send_message(embed=embed)
 
 # ---------------------------------------------------------
# /eek - belirlenmiş fotoğrafı gösterir
# ---------------------------------------------------------
@bot.tree.command(name="eek", description="Fotoğrafı gösterir")
async def eek(interaction: discord.Interaction):
    if EEK_IMAGE_URL == "BURAYA_FOTOGRAF_LINKINI_YAPISTIR":
        await interaction.response.send_message(
            "Henüz bir fotoğraf linki ayarlanmamış. bot.py içindeki EEK_IMAGE_URL değişkenine bir link yapıştır.",
            ephemeral=True,
        )
        return
 
    embed = discord.Embed(color=discord.Color.blue())
    embed.set_image(url=EEK_IMAGE_URL)
    await interaction.response.send_message(embed=embed)

     # ---------------------------------------------------------
# /ates - belirlenmiş fotoğrafı gösterir
# ---------------------------------------------------------
@bot.tree.command(name="ates", description="Fotoğrafı gösterir")
async def ates(interaction: discord.Interaction):
    if ATES_IMAGE_URL == "BURAYA_FOTOGRAF_LINKINI_YAPISTIR":
        await interaction.response.send_message(
            "Henüz bir fotoğraf linki ayarlanmamış. bot.py içindeki ATES_IMAGE_URL değişkenine bir link yapıştır.",
            ephemeral=True,
        )
        return
 
    embed = discord.Embed(color=discord.Color.blue())
    embed.set_image(url=ATES_IMAGE_URL)
    await interaction.response.send_message(embed=embed)

# KOMUTLAR

@bot.tree.command(name="komutlar", description="Botun tüm komutlarını gösterir.")
async def komutlar(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📖 HRMN Bot Komutları",
        description="Aşağıda kullanılabilir komutlar listelenmiştir.",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Moderasyon",
        value="""
`/warn` → Kullanıcıya uyarı verir.
`/unwarn` → Kullanıcının son uyarısını siler.
`/warnings` → Kullanıcının uyarılarını gösterir.
`/kick` → Kullanıcıyı atar.
`/ban` → Kullanıcıyı yasaklar.
`/unban` → Kullanıcıda ki yasaklamayı kaldırır.
`/mute` → Kullanıcıyı susturur.
`/unmute` → Kullanıcının susturmasını kaldırır.
`/giverole` → Kullanıcıya rol verir.
`/karsilamakanali` → Kullanıcının sunucuya katıldığında mesaj göndereceği kanalı ayarlar.
`/komutlar` → Bu menüyü açar.
""",
        inline=False
    )

    embed.add_field(
        name="Eğlence",
        value="""
`/zar` → Belirlediğin iki sayı arasında rastgele bir sayı seçer.
`/sarıl` → Bir kullanıcıya sarılır.
`/tahminbaslat` → Tahmin oyununu başlatır.
`/tahmin` → Tahmin oyununda sayı tahmini yapar.
`/taskagitmakas` → Taş, Kağıt, Makas oyununu oynar.

""",
        inline=False
    )

    embed.add_field(
        name="Müzik Takip",
        value="""

`/setmuzikkanali` → Yeni şarkı bildirimlerinin gönderileceği kanalı ayarlar.
`/sanatciekle` → Takip edilecek listeye yeni bir sanatçı ekler.
`/sanatcilistesi` → Takip edilen sanatçıları listeler.
`/sanatcisil` → Takip listesinden bir sanatçıyı çıkarır.
""",
        inline=False
    )

    embed.add_field(
        name="Oyun Takip",
        value="""

`/setoyunkanali` → Yeni oyun bildirimlerinin gönderileceği kanalı ayarlar.
`/ucretsizoyunlar` →Steam ve Epic Games Store'daki güncel ücretsiz oyunları gösterir.
""",
        inline=False
    )

    embed.add_field(
        name="Kulecoin",
        value="""

`/kulecoin` → Kulecoin miktarını gösterir.
`/topkulecoin` → Kulecoin sıralamasını gösterir.
`/kulecoinver` → Bir kullanıcıya Kulecoin gönderir.
`/gunluk` → Günlük Kulecoin ödülünü alır.
`/envanter` → Kullanıcının envanterini gösterir.
`/baliktut` → Balık tutma oyununu oynar.
`/baliksat` → Tutulan balığı satar ve Kulecoin kazanır.
`/olta` → Kullanıcının kullandığı oltayı gösterir.
`/oltasatinal` → Kulecoin karşılığında yeni bir olta satın alır.
`/market` → Kulecoin karşılığında satılan oltaları gösterir.
`/bj` → BlackJack oyununu başlatır.
`/slot` → Slot oyununu oynar.
`/gorev` → Kullanıcının görevlerini gösterir.
""",
        inline=False
    )

    embed.set_footer(text="HRMN • Sunucunuza Özel Bot")
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

    # ---------------------------------------------------------
# /ucretsizoyunlar - Steam ve Epic'teki güncel ücretsiz oyunları gösterir
# ---------------------------------------------------------
@bot.tree.command(
    name="ucretsizoyunlar",
    description="Steam ve Epic Games Store'daki güncel ücretsiz oyunları gösterir"
)
async def free_games(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        games = fetch_free_games()
    except Exception as e:
        await interaction.followup.send(f"Veri çekilirken hata oluştu: {e}")
        return

    if not games:
        await interaction.followup.send("Şu anda ücretsiz oyun bulunamadı.")
        return

    embed = discord.Embed(
        title="🎁 Şu An Ücretsiz Oyunlar",
        description="Steam ve Epic Games Store'daki güncel ücretsiz oyunlar",
        color=0x8A2BE2
    )

    for game in games[:10]:
        title = game.get("title", "Bilinmiyor")
        title = title.replace("(Epic Games) Giveaway", "")
        title = title.replace("(Steam) Giveaway", "")
        title = title.replace("Giveaway", "").strip()

        worth = game.get("worth", "Bilinmiyor")
        platform = game.get("platforms", "Bilinmiyor")
        end_date = game.get("end_date", "Bilinmiyor")
        image = game.get("image")
        url = game.get("open_giveaway_url")

        embed.add_field(
            name=f"🎮 {title}",
            value=(
                f"🛒 **Platform:** {platform}\n"
                f"💰 **Normal Fiyat:** {worth}\n"
                f"⏳ **Bitiş:** {end_date}\n"
                f"🔗 {url}"
            ),
            inline=False
        )

        # İlk oyunun görselini göster
        if image and embed.thumbnail.url is None:
            embed.set_thumbnail(url=image)

    embed.set_footer(text="HRMN • GamerPower verileri kullanılmaktadır.")

    await interaction.followup.send(embed=embed)


  
# ---------------------------------------------------------
# /setoyunkanali - ücretsiz oyun bildirimlerinin gideceği kanalı ayarlar
# ---------------------------------------------------------
@bot.tree.command(name="setoyunkanali", description="Yeni ücretsiz oyun bildirimlerinin gönderileceği kanalı ayarlar")
@app_commands.describe(channel="Bildirimlerin gönderileceği kanal")
async def set_games_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not has_permission(interaction, "manage_guild"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return
 
    games_data["games_channel_id"] = channel.id
    save_games_data(games_data)
    await interaction.response.send_message(f"✅ Ücretsiz oyun bildirimleri artık {channel.mention} kanalına gönderilecek.")

# ---------------------------------------------------------
# /giverole - bir kullanıcıya rol verir
# ---------------------------------------------------------
@bot.tree.command(name="giverole", description="Bir kullanıcıya rol verir")
@app_commands.describe(member="Rol verilecek kullanıcı", role="Verilecek rol")
async def giverole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not has_permission(interaction, "manage_roles"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return
 
    if role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("Bu rolü veremezsin (rolün senden yüksek veya eşit).", ephemeral=True)
        return
 
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message("Bu rolü veremem, botun rolü bu rolden daha aşağıda.", ephemeral=True)
        return
 
    if role in member.roles:
        await interaction.response.send_message(f"**{member}** zaten **{role.name}** rolüne sahip.", ephemeral=True)
        return
 
    await member.add_roles(role)
    await interaction.response.send_message(f"✅ **{role.name}** rolü **{member}** kullanıcısına verildi.")

# ---------------------------------------------------------
# /taskagitmakas - taş kağıt makas oyunu
# ---------------------------------------------------------
@bot.tree.command(name="taskagitmakas", description="Bota karşı taş kağıt makas oyna!")
@app_commands.choices(secim=[
    app_commands.Choice(name="Taş", value="tas"),
    app_commands.Choice(name="Kağıt", value="kagit"),
    app_commands.Choice(name="Makas", value="makas"),
])
async def rock_paper_scissors(interaction: discord.Interaction, secim: app_commands.Choice[str]):
    emojiler = {"tas": "🪨", "kagit": "📄", "makas": "✂️"}
    isimler = {"tas": "Taş", "kagit": "Kağıt", "makas": "Makas"}
 
    kullanici_secim = secim.value
    bot_secim = random.choice(["tas", "kagit", "makas"])
 
    kazanan_kombinasyonlar = {
        ("tas", "makas"),
        ("kagit", "tas"),
        ("makas", "kagit"),
    }
 
    if kullanici_secim == bot_secim:
        sonuc = "🤝 Berabere!"
    elif (kullanici_secim, bot_secim) in kazanan_kombinasyonlar:
        sonuc = "🎉 Kazandın!"
    else:
        sonuc = "😢 Kaybettin!"
 
    mesaj = (
        f"Sen: {emojiler[kullanici_secim]} {isimler[kullanici_secim]}\n"
        f"Bot: {emojiler[bot_secim]} {isimler[bot_secim]}\n\n"
        f"**{sonuc}**"
    )
    await interaction.response.send_message(mesaj)

# ---------------------------------------------------------
# ARKA PLAN GÖREVİ: saatte bir yeni ücretsiz oyun kontrolü
# ---------------------------------------------------------
@tasks.loop(hours=1)
async def check_free_games():
 
    channel_id = games_data.get("games_channel_id")
    channel = bot.get_channel(channel_id)
    if channel is None:
        return
 
    try:
        games = fetch_free_games()
    except requests.exceptions.RequestException as e:
        print(f"Ücretsiz oyun kontrol hatası: {e}")
        return
 
    known_ids = games_data.get("known_ids", [])
    new_known_ids = list(known_ids)
 
    for game in games:
        game_id = str(game["id"])
        if game_id in known_ids:
            continue
 
        new_known_ids.append(game_id)
 
        embed = discord.Embed(
            title=f"🎁 Yeni ücretsiz oyun: {game['title']}",
            description=game.get("description", ""),
            url=game["open_giveaway_url"],
            color=discord.Color.gold(),
        )
        embed.add_field(name="Platform", value=game.get("platforms", "Bilinmiyor"))
        if game.get("image"):
            embed.set_thumbnail(url=game["image"])
 
        await channel.send(embed=embed)
 
    if new_known_ids != known_ids:
        games_data["known_ids"] = new_known_ids
        save_games_data(games_data)

#COİM

@bot.tree.command(name="kulecoin", description="Kulecoin miktarını gösterir.")
async def coin(interaction: discord.Interaction):

    miktar = get_coin(interaction.user.id)

    embed = discord.Embed(
        title="💰 Cüzdan",
        description=f"Toplam Kulecoinin: **{miktar:,} 🪙**",
        color=0xFFD700
    )

    await interaction.response.send_message(embed=embed)

#COINVER

@bot.tree.command(name="kulecoinver", description="Bir kullanıcıya Kulecoin gönder.")
async def coinver(
    interaction: discord.Interaction,
    uye: discord.Member,
    miktar: int
):

    if miktar <= 0:
        await interaction.response.send_message("Geçersiz miktar.", ephemeral=True)
        return

    if get_coin(interaction.user.id) < miktar:
        await interaction.response.send_message("Yeterli Kulecoinin yok.", ephemeral=True)
        return

    remove_coin(interaction.user.id, miktar)
    add_coin(uye.id, miktar)

    await interaction.response.send_message(
        f"💸 {uye.mention} kullanıcısına **{miktar}** Kulecoin 🪙 gönderdin."
    )

# GUNLUK

@bot.tree.command(name="gunluk", description="Günlük ödülünü al.")
async def gunluk(interaction: discord.Interaction):

    data = load_daily()

    uid = str(interaction.user.id)

    now = time.time()

    if uid in data:

        kalan = 86400 - (now - data[uid])

        if kalan > 0:

            saat = int(kalan // 3600)
            dakika = int((kalan % 3600) // 60)

            await interaction.response.send_message(
                f"⏳ Tekrar almak için **{saat} saat {dakika} dakika** beklemelisin.",
                ephemeral=True
            )
            return

    odul = random.randint(500, 1000)

    add_coin(interaction.user.id, odul)

    data[uid] = now

    save_daily(data)

    embed = discord.Embed(
        title="🎁 Günlük Ödül",
        description=f"Bugünkü ödülün **{odul} Kulecoin 🪙**",
        color=0x2ECC71
    )

    await interaction.response.send_message(embed=embed)

#ENVANTER

@bot.tree.command(name="envanter", description="Envanterini göster.")
async def envanter(interaction: discord.Interaction):

    inv = get_inventory(interaction.user.id)

    if not inv:

        await interaction.response.send_message("🎒 Envanterin boş.")
        return

    text = ""

    for item, adet in inv.items():
        text += f"• {item} x{adet}\n"

    embed = discord.Embed(
        title=f"🎒 {interaction.user.display_name} Envanteri",
        description=text,
        color=0x3498DB
    )

    await interaction.response.send_message(embed=embed)

# BALIK
@bot.tree.command(
    name="baliktut",
    description="Balık tutarak Kulecoin ve eşya kazan."
)
@app_commands.checks.cooldown(1, 30)
async def baliktut(interaction: discord.Interaction):

    await interaction.response.defer()

    await asyncio.sleep(random.randint(2, 5))

    # Ağırlıklı rastgele balık seç
    toplam_agirlik = sum(balik[1] for balik in BALIKLAR)
    secilen = random.uniform(0, toplam_agirlik)

    anlik = 0

    for isim, agirlik, min_coin, max_coin in BALIKLAR:
        anlik += agirlik

        if secilen <= anlik:
            break

    # Coin ödülü
    coin = random.randint(min_coin, max_coin)

    # Olta bonusu
    rod = get_rod(interaction.user.id)
    bonus = RODS[rod]["bonus"]

    coin = int(coin * (1 + bonus / 100))

    # Ödülleri ver
    add_item(interaction.user.id, isim, 1)
    add_coin(interaction.user.id, coin)
    update_fish(interaction.user.id)

    embed = discord.Embed(
        title="🎣 Balık Avı",
        color=0x3498DB
    )

    embed.add_field(
        name="🐠 Yakaladığın",
        value=isim,
        inline=True
    )

    embed.add_field(
        name="🪙 Kazandığın Kulecoin",
        value=f"{coin:,}",
        inline=True
    )

    embed.add_field(
        name="🎣 Kullanılan Olta",
        value=f"{rod} (+%{bonus})",
        inline=True
    )

    embed.set_footer(
        text=f"{interaction.user.display_name} tarafından tutuldu."
    )

    await interaction.followup.send(embed=embed)
# OLTA

@bot.tree.command(name="olta", description="Kullandığın oltayı gösterir.")
async def olta(interaction: discord.Interaction):

    rod = get_rod(interaction.user.id)

    embed = discord.Embed(
        title="🎣 Oltan",
        description=f"Şu anda kullandığın olta:\n\n**{rod}**",
        color=0x2ECC71
    )

    await interaction.response.send_message(embed=embed)

# MARKET

@bot.tree.command(name="market", description="Olta marketini açar.")
async def market(interaction: discord.Interaction):

    mevcut_olta = get_rod(interaction.user.id)

    embed = discord.Embed(
        title="🛒 Olta Marketi",
        description="Yeni oltalar satın alarak daha fazla Kulecoin kazanabilirsin.",
        color=0xF1C40F
    )

    for isim, bilgi in RODS.items():

        fiyat = bilgi["fiyat"]
        bonus = bilgi["bonus"]

        if isim == mevcut_olta:
            durum = "✅ Kullanılıyor"
        else:
            durum = f"`/oltasatin al:{isim}`"

        embed.add_field(
            name=f"🎣 {isim}",
            value=(
                f"💰 Fiyat: **{fiyat:,} 🪙**\n"
                f"⭐ Bonus: **+%{bonus}**\n"
                f"{durum}"
            ),
            inline=False
        )

    await interaction.response.send_message(embed=embed)

# OLTA SATIN AL
@bot.tree.command(name="oltasatinal", description="Yeni bir olta satın al.")
@app_commands.describe(olta="Satın almak istediğin olta")
@app_commands.choices(
    olta=[
        app_commands.Choice(name="Demir Olta", value="Demir Olta"),
        app_commands.Choice(name="Altın Olta", value="Altın Olta"),
        app_commands.Choice(name="Elmas Olta", value="Elmas Olta"),
        app_commands.Choice(name="Efsane Olta", value="Efsane Olta"),
    ]
)
async def oltasatin(
    interaction: discord.Interaction,
    olta: app_commands.Choice[str]
):

    secilen = olta.value
    mevcut = get_rod(interaction.user.id)

    siralama = list(RODS.keys())

    if siralama.index(secilen) <= siralama.index(mevcut):
        await interaction.response.send_message(
            "❌ Bu oltayı satın alamazsın.",
            ephemeral=True
        )
        return

    fiyat = RODS[secilen]["fiyat"]

    if get_coin(interaction.user.id) < fiyat:
        await interaction.response.send_message(
            f"❌ Bunun için **{fiyat:,} Kulecoin 🪙** gerekiyor.",
            ephemeral=True
        )
        return

    remove_coin(interaction.user.id, fiyat)
    set_rod(interaction.user.id, secilen)

    embed = discord.Embed(
        title="🎣 Olta Satın Alındı",
        description=f"Yeni oltan **{secilen}** oldu!",
        color=0x2ECC71
    )

    embed.add_field(
        name="💰 Harcanan Kulecoin",
        value=f"{fiyat:,} 🪙"
    )

    await interaction.response.send_message(embed=embed)

# BALIK SAT

@bot.tree.command(name="baliksat", description="Envanterindeki tüm balıkları satar.")
async def baliksat(interaction: discord.Interaction):

    inv = get_inventory(interaction.user.id)

    toplam = 0
    satilan = ""

    for isim, oran, min_coin, max_coin in BALIKLAR:

        adet = inv.get(isim, 0)

        if adet <= 0:
            continue

        fiyat = random.randint(min_coin, max_coin)
        kazanc = fiyat * adet

        toplam += kazanc

        satilan += f"{isim} x{adet} → **{kazanc:,} 🪙**\n"

        remove_item(interaction.user.id, isim, adet)

    if toplam == 0:
        await interaction.response.send_message(
            "🎣 Satacak balığın yok.",
            ephemeral=True
        )
        return

    add_coin(interaction.user.id, toplam)

    embed = discord.Embed(
        title="💰 Balıklar Satıldı",
        description=satilan,
        color=0x2ECC71
    )

    embed.add_field(
        name="🪙 Toplam Kazanç",
        value=f"**{toplam:,} Kulecoin**",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# SLOT

@bot.tree.command(
    name="slot",
    description="Kulecoin ile slot oyna."
)
@app_commands.describe(miktar="Bahis miktarı")
async def slot(interaction: discord.Interaction, miktar: int):

    if miktar <= 0:
        await interaction.response.send_message(
            "❌ Geçerli bir miktar gir.",
            ephemeral=True
        )
        return

    if get_coin(interaction.user.id) < miktar:
        await interaction.response.send_message(
            "❌ Yeterli Kulecoinin yok.",
            ephemeral=True
        )
        return

    remove_coin(interaction.user.id, miktar)

    semboller = [
        "🍒",
        "🍋",
        "🍇",
        "💎",
        "7️⃣",
        "⭐"
    ]

    sonuc = [random.choice(semboller) for _ in range(3)]

    kazanc = 0
    sonuc_mesaj = ""

    # 3 aynı
    if sonuc[0] == sonuc[1] == sonuc[2]:

        if sonuc[0] == "7️⃣":
            kazanc = miktar * 10

        elif sonuc[0] == "💎":
            kazanc = miktar * 7

        elif sonuc[0] == "⭐":
            kazanc = miktar * 5

        else:
            kazanc = miktar * 3

        sonuc_mesaj = "🎉 JACKPOT!"

    # 2 aynı
    elif (
        sonuc[0] == sonuc[1]
        or sonuc[1] == sonuc[2]
        or sonuc[0] == sonuc[2]
    ):
        kazanc = int(miktar * 1.5)
        sonuc_mesaj = "✨ İki aynı geldi!"

    else:
        sonuc_mesaj = "💀 Kaybettin."

    if kazanc > 0:
        add_coin(interaction.user.id, kazanc)

    embed = discord.Embed(
        title="🎰 Slot Makinesi",
        description=" | ".join(sonuc),
        color=0xF1C40F
    )

    embed.add_field(
        name="💰 Bahis",
        value=f"{miktar:,} 🪙",
        inline=True
    )

    embed.add_field(
        name="🏆 Sonuç",
        value=sonuc_mesaj,
        inline=True
    )

    embed.add_field(
        name="💸 Kazanç",
        value=f"{kazanc:,} 🪙",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ==========================================
# BLACKJACK
# ==========================================

KARTLAR = [
    ("A", 11),
    ("2", 2),
    ("3", 3),
    ("4", 4),
    ("5", 5),
    ("6", 6),
    ("7", 7),
    ("8", 8),
    ("9", 9),
    ("10", 10),
    ("J", 10),
    ("Q", 10),
    ("K", 10)
]

def kart_cek():
    return random.choice(KARTLAR)

def el_degeri(el):
    toplam = sum(k[1] for k in el)
    as_sayisi = sum(1 for k in el if k[0] == "A")

    while toplam > 21 and as_sayisi > 0:
        toplam -= 10
        as_sayisi -= 1

    return toplam


@bot.tree.command(name="bj", description="Blackjack oyna.")
@app_commands.describe(bahis="Bahis miktarı")
async def blackjack(interaction: discord.Interaction, bahis: int):

    if bahis <= 0:
        await interaction.response.send_message(
            "Geçerli bahis gir.",
            ephemeral=True
        )
        return

    if get_coin(interaction.user.id) < bahis:
        await interaction.response.send_message(
            "Yeterli Kulecoin yok.",
            ephemeral=True
        )
        return

    remove_coin(interaction.user.id, bahis)

    oyuncu = [kart_cek(), kart_cek()]
    krupiye = [kart_cek(), kart_cek()]

    oyuncu_puan = el_degeri(oyuncu)

    while el_degeri(krupiye) < 17:
        krupiye.append(kart_cek())

    krupiye_puan = el_degeri(krupiye)

    sonuc = ""
    renk = 0x2ECC71

    if oyuncu_puan > 21:
        sonuc = f"Kaybettin!\n-{bahis:,} 🪙"
        renk = 0xE74C3C

    elif krupiye_puan > 21:
        kazanc = bahis * 2
        add_coin(interaction.user.id, kazanc)
        sonuc = f"Krupiye patladı!\n+{kazanc:,} 🪙"

    elif oyuncu_puan > krupiye_puan:
        kazanc = bahis * 2
        add_coin(interaction.user.id, kazanc)
        sonuc = f"Kazandın!\n+{kazanc:,} 🪙"

    elif oyuncu_puan == krupiye_puan:
        add_coin(interaction.user.id, bahis)
        sonuc = "Berabere.\nBahsin iade edildi."

    else:
        sonuc = f"Kaybettin!\n-{bahis:,} 🪙"
        renk = 0xE74C3C

    embed = discord.Embed(
        title="🃏 Blackjack",
        color=renk
    )

    embed.add_field(
        name=f"Sen ({oyuncu_puan})",
        value=" ".join(k[0] for k in oyuncu),
        inline=False
    )

    embed.add_field(
        name=f"Krupiye ({krupiye_puan})",
        value=" ".join(k[0] for k in krupiye),
        inline=False
    )

    embed.add_field(
        name="Sonuç",
        value=sonuc,
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# TOPKULECOİN

@bot.tree.command(
    name="topkulecoin",
    description="Sunucudaki en zengin kullanıcıları gösterir."
)
async def topcoin(interaction: discord.Interaction):

    coins = load_coins()

    if not coins:
        await interaction.response.send_message("Henüz hiç Kulecoin bulunmuyor.")
        return

    siralama = sorted(
        coins.items(),
        key=lambda x: x[1],
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 Kulecoin Liderlik Tablosu",
        color=0xFFD700
    )

    text = ""

    for i, (user_id, coin) in enumerate(siralama[:10], start=1):

        try:
            uye = await bot.fetch_user(int(user_id))
            isim = uye.name
        except:
            isim = "Bilinmeyen Kullanıcı"

        if i == 1:
            emoji = "🥇"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = f"**{i}.**"

        text += f"{emoji} **{isim}** — `{coin:,}` 🪙\n"

    embed.description = text

    await interaction.response.send_message(embed=embed)

    # ==============================
# GÖREVLER
# ==============================

def load_missions():
    if not os.path.exists(MISSION_FILE):
        return {}

    with open(MISSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_missions(data):
    with open(MISSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_mission(user_id):
    data = load_missions()

    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "fish": 0,
            "reward": False
        }
        save_missions(data)

    return data[uid]


def update_fish(user_id):
    data = load_missions()

    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "fish": 0,
            "reward": False
        }

    data[uid]["fish"] += 1

    save_missions(data)

# GÖREV

@bot.tree.command(name="gorev", description="Günlük görevini görüntüler.")
async def gorev(interaction: discord.Interaction):

    mission = get_mission(interaction.user.id)

    hedef = 10
    odul = 5000

    if mission["fish"] >= hedef and not mission["reward"]:

        add_coin(interaction.user.id, odul)

        data = load_missions()
        data[str(interaction.user.id)]["reward"] = True
        save_missions(data)

        embed = discord.Embed(
            title="🎉 Günlük Görev Tamamlandı!",
            description=f"🎣 {hedef} balık tuttun!\n\n💰 **{odul:,} Kulecoin** kazandın.",
            color=0x2ECC71
        )

        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(
        title="📋 Günlük Görev",
        color=0x3498DB
    )

    embed.add_field(
        name="🎣 Görev",
        value=f"Balık Tut ({mission['fish']}/{hedef})",
        inline=False
    )

    embed.add_field(
        name="💰 Ödül",
        value=f"{odul:,} Kulecoin 🪙",
        inline=False
    )

    if mission["reward"]:
        embed.set_footer(text="✅ Ödül alındı.")
    else:
        embed.set_footer(text="Devam et!")

    await interaction.response.send_message(embed=embed)

# ---------------------------------------------------------
# /tahminbaslat
# ---------------------------------------------------------
@bot.tree.command(name="tahminbaslat", description="Bu kanalda sayı tahmin oyunu başlatır")
@app_commands.describe(min_deger="En küçük sayı", max_deger="En büyük sayı")
async def start_guess_game(interaction: discord.Interaction, min_deger: int, max_deger: int):
    if min_deger >= max_deger:
        await interaction.response.send_message("En küçük sayı, en büyük sayıdan küçük olmalı.", ephemeral=True)
        return
 
    channel_id = interaction.channel_id
    secret_number = random.randint(min_deger, max_deger)
    guess_games[channel_id] = {"number": secret_number, "min": min_deger, "max": max_deger, "attempts": 0}
 
    await interaction.response.send_message(
        f"🎯 Aklımdan **{min_deger}** ile **{max_deger}** arasında bir sayı tuttum!\n"
        f"Tahmin etmek için `/tahmin sayi:` komutunu kullan."
    )
 
 
# ---------------------------------------------------------
# /tahmin
# ---------------------------------------------------------
@bot.tree.command(name="tahmin", description="Aktif sayı tahmin oyununda bir tahmin yapar")
@app_commands.describe(sayi="Tahmin ettiğin sayı")
async def guess_number(interaction: discord.Interaction, sayi: int):
    channel_id = interaction.channel_id
    game = guess_games.get(channel_id)
 
    if game is None:
        await interaction.response.send_message(
            "Bu kanalda aktif bir oyun yok. Önce `/tahminbaslat` ile bir oyun başlat.", ephemeral=True
        )
        return
 
    game["attempts"] += 1
 
    if sayi < game["min"] or sayi > game["max"]:
        await interaction.response.send_message(
            f"Lütfen {game['min']} ile {game['max']} arasında bir sayı gir.", ephemeral=True
        )
        return
 
    if sayi == game["number"]:
        attempts = game["attempts"]
        del guess_games[channel_id]
        await interaction.response.send_message(
            f"🎉 **{interaction.user.mention}** doğru bildi! Sayı **{sayi}**'ymiş. ({attempts} denemede buldu)"
        )
    elif sayi < game["number"]:
        await interaction.response.send_message(f"📈 Daha büyük bir sayı dene! ({game['attempts']}. deneme)")
    else:
        await interaction.response.send_message(f"📉 Daha küçük bir sayı dene! ({game['attempts']}. deneme)")
 
 # ---------------------------------------------------------
# /karsilamakanali - hoşgeldin/güle güle mesajlarının gideceği kanalı ayarlar
# ---------------------------------------------------------
@bot.tree.command(name="karsilamakanali", description="Hoşgeldin ve güle güle mesajlarının gönderileceği kanalı ayarlar")
@app_commands.describe(channel="Mesajların gönderileceği kanal")
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not has_permission(interaction, "manage_guild"):
        await interaction.response.send_message("Bu komutu kullanma yetkin yok.", ephemeral=True)
        return
    welcome_data["welcome_channel_id"] = channel.id
    save_welcome_data(welcome_data)
    await interaction.response.send_message(f"✅ Hoşgeldin/güle güle mesajları artık {channel.mention} kanalına gönderilecek.")
 
 
# ---------------------------------------------------------
# ÜYE KATILDIĞINDA
# ---------------------------------------------------------
@bot.event
async def on_member_join(member: discord.Member):
    channel_id = welcome_data.get("welcome_channel_id")
    if not channel_id:
        return
 
    channel = bot.get_channel(channel_id)
    if channel is None:
        return
 
    embed = discord.Embed(
        title="👋 Yeni bir üye katıldı!",
        description=f"{member.mention}, **{member.guild.name}** sunucusuna hoş geldin!",
        color=discord.Color.green(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Şu an sunucuda {member.guild.member_count} üye var.")
 
    await channel.send(embed=embed)
 
 
# ---------------------------------------------------------
# ÜYE AYRILDIĞINDA
# ---------------------------------------------------------
@bot.event
async def on_member_remove(member: discord.Member):
    channel_id = welcome_data.get("welcome_channel_id")
    if not channel_id:
        return
 
    channel = bot.get_channel(channel_id)
    if channel is None:
        return
 
    embed = discord.Embed(
        title="😢 Bir üye ayrıldı",
        description=f"**{member}** sunucudan ayrıldı.",
        color=discord.Color.red(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Şu an sunucuda {member.guild.member_count} üye var.")
 
    await channel.send(embed=embed)

# ---------------------------------------------------------
# /hotfix
# ---------------------------------------------------------
HOTFIX_MESSAGES = [
    "🛠️ Katlanmam hotfix attı.",
    "🔥 Sunucu yine çöktü, hotfix geliyor...",
    "⚙️ Bug'ları görmezden gelip hotfix attık.",
    "🚨 Acil durum! Hotfix devrede.",
]

@bot.tree.command(name="hotfix", description="Hotfix attık!")
async def hotfix(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(HOTFIX_MESSAGES))
 
    

# ---------------------------------------------------------
# HATA YÖNETİMİ (genel)
# ---------------------------------------------------------
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Bu işlem için yetkin yok.", ephemeral=True)
    else:
        print(f"Hata: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("Bir hata oluştu, konsolu kontrol et.", ephemeral=True)

@bot.tree.error
async def on_app_command_error(interaction, error):

    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ Tekrar kullanmak için {int(error.retry_after)} saniye beklemelisin.",
            ephemeral=True
        )
        return

    if isinstance(error, app_commands.MissingPermissions):
        ...


# ---------------------------------------------------------
# BOTU ÇALIŞTIR
# ---------------------------------------------------------
if __name__ == "__main__":
    if TOKEN == "MTQ1MzQwNzg5ODkyNjQ1Mjc3Ng.GP0ZpA.Mivhafgsth3MF6z2WDH7Y-aWwBu3msSRZRtWxc":
        print("UYARI: Lütfen bot.py içine ya da DISCORD_BOT_TOKEN ortam değişkenine token'ını gir!")
    bot.run(TOKEN)

