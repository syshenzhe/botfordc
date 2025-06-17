import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import time
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
@app_commands.command(name="hesap_sil", description="Belirtilen platform ve türdeki hesapları siler (Yönetici sadece).")
@app_commands.describe(platform="Silinecek hesapların platformu", type="Hesap türü (free/premium)")
async def hesap_sil(interaction: discord.Interaction, platform: str, type: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Bu komutu sadece yöneticiler kullanabilir.", ephemeral=True)
        return

    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = f.readlines()

        kalan_hesaplar = [acc for acc in accounts if not (acc.strip().split(',')[1] == platform and acc.strip().split(',')[2] == type)]

        silinen_sayisi = len(accounts) - len(kalan_hesaplar)

        if silinen_sayisi == 0:
            await interaction.response.send_message(f"{platform} platformunda {type} türünde hesap bulunamadı.", ephemeral=True)
            return

        with open("accounts.txt", "w", encoding="utf-8") as f:
            f.writelines(kalan_hesaplar)

        await interaction.response.send_message(f"{silinen_sayisi} adet hesap silindi.", ephemeral=True)

    except FileNotFoundError:
        await interaction.response.send_message("Stok dosyası bulunamadı.", ephemeral=True)

# 🌐 Keep-alive servisi (render.com için)
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot calisiyor')

def run_keep_alive():
    server = HTTPServer(('0.0.0.0', 8080), KeepAliveHandler)
    server.serve_forever()

threading.Thread(target=run_keep_alive).start()

# 🔧 Bot tanımı
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    if not hasattr(bot, 'synced'):
        await bot.tree.sync()
        bot.synced = True
    print(f'✅ Giriş yapıldı: {bot.user.name} - {bot.user.id}')

# 🎯 /ping komutu
@app_commands.command(name="ping", description="Bot gecikmesi kontrolü")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong! 🏓')
    start_time = time.time()
    latency = round(bot.latency * 1000)
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000)
    await interaction.followup.send(f'Gecikme: {latency} ms, İşlem süresi: {elapsed_time} ms 🏓')

# 🎲 /zar komutu
@app_commands.command(name='zar', description='Zar atar')
async def zar(interaction: discord.Interaction):
    await interaction.response.send_message('Zar atılıyor 🎲!')
    await asyncio.sleep(1)
    result = random.randint(1, 6)
    await interaction.followup.send(f'Zar sonucu: {result} 🎲')

# 🔢 /rastgele komutu
@app_commands.command(name='rastgele', description='Rastgele bir sayı üretir')
@app_commands.describe(min='Minimum değeriniz', max='Maksimum değeri giriniz')
async def rastgele(interaction: discord.Interaction, min: int, max: int):
    if min > max:
        await interaction.response.send_message("Geçersiz aralık.", ephemeral=True)
        return
    result = random.randint(min, max)
    await interaction.response.send_message(f'Rastgele sayı: {result}')

# ➕ /hesap_ekle komutu
@app_commands.command(name="hesap_ekle", description="Hesapları satır satır gir (**txt olmasın aman dikkat*‼️*)")
@app_commands.describe(
    accounts="Her satıra bir hesap yaz",
    platform="Hesapların platformu",
    type="Hesap türü"
)
async def hesap_ekle(interaction: discord.Interaction, accounts: str, platform: str, type: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Bu komutu sadece yöneticiler kullanabilir.", ephemeral=True)
        return

    account_list = accounts.strip().splitlines()
    if not account_list:
        await interaction.response.send_message("Lütfen en az bir hesap girin.", ephemeral=True)
        return

    with open("accounts.txt", "a", encoding="utf-8") as f:
        for account in account_list:
            f.write(f"{account},{platform},{type}\n")
    await interaction.response.send_message(f"{len(account_list)} adet hesap eklendi.", ephemeral=True)

# 📦 /stoklar komutu
@app_commands.command(name="stoklar", description="Hesapları listeler")
async def stoklar(interaction: discord.Interaction):
    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = f.readlines()

        if not accounts:
            await interaction.response.send_message("Stokta hesap bulunmuyor.", ephemeral=True)
            return

        platform_count = {}
        for acc in accounts:
            try:
                _, platform, typ = acc.strip().split(',')
                key = f"{platform} ({typ})"
                platform_count[key] = platform_count.get(key, 0) + 1
            except ValueError:
                continue

        msg = "**📦 Stok Durumu:**\n"
        for k, v in platform_count.items():
            msg += f"- {k}: {v} adet\n"

        await interaction.response.send_message(msg, ephemeral=True)

    except FileNotFoundError:
        await interaction.response.send_message("Stok dosyası bulunamadı.", ephemeral=True)

# 📜 /help komutu
@app_commands.command(name="help", description="Yardım menüsünü gösterir")
async def help_command(interaction: discord.Interaction):
    help_text = """
**Yardım Menüsü**
/ping - Bot gecikmesini kontrol eder.
/zar - Zar atar.
/rastgele - Rastgele bir sayı üretir.
/hesap_ekle - Hesapları ekler (sadece admin).
/stoklar - Hesapları listeler.
/gen - Belirli türde hesap verir.
/pregen - Premium hesap verir (sadece premium roller).
/help - Yardım menüsünü gösterir.
**Not:** Bazı komutlar sadece yöneticiler içindir.
"""
    await interaction.response.send_message(help_text)

# 🔍 /gen komutu
@app_commands.command(name="gen", description="İstediğiniz platform ve türde hesapları listeler.")
@app_commands.describe(platform="Hesapların platformu", type="Hesap türü (free/premium)")
async def freegen(interaction: discord.Interaction, platform: str, type: str = 'free'):
    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = f.readlines()

        filtered_accounts = [acc.strip() for acc in accounts if acc.strip().split(',')[1] == platform and acc.strip().split(',')[2] == type]

        if not filtered_accounts:
            await interaction.response.send_message(f"{platform} platformunda {type} türünde hesap bulunamadı.", ephemeral=True)
            return

        account = random.choice(filtered_accounts)
        await interaction.response.send_message(f"Platform: {platform}, Tür: {type}\nHesap: {account}", ephemeral=True)

    except FileNotFoundError:
        await interaction.response.send_message("Stok dosyası bulunamadı, lütfen yönetici ile iletişime geçin‼️‼️", ephemeral=True)

# 👑 /pregen komutu
@app_commands.command(name="pregen", description="Premium hesap üretir (sadece premium üyeler için)")
async def pregen(interaction: discord.Interaction):
    allowed_roles = ['Premium', 'Booster']
    member = interaction.user

    if not isinstance(member, discord.Member):
        await interaction.response.send_message("Bu komutu sadece sunucularda kullanabilirsin.", ephemeral=True)
        return

    if not any(role.name in allowed_roles for role in member.roles):
        await interaction.response.send_message("Bu komutu kullanmak için yeterli izniniz yok.", ephemeral=True)
        return

    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = f.readlines()

        filtered_accounts = [acc.strip() for acc in accounts if acc.strip().split(',')[2] == 'premium']

        if not filtered_accounts:
            await interaction.response.send_message("Stokta premium hesap bulunmuyor. Yönetici ile iletişime geçiniz‼️", ephemeral=True)
            return

        account = random.choice(filtered_accounts)
        await interaction.response.send_message(f"🎁 Premium Hesap:\n{account}", ephemeral=True)

        accounts = [acc for acc in accounts if acc.strip() != account.strip()]

        with open("accounts.txt", "w", encoding="utf-8") as f:
            f.writelines(accounts)

    except FileNotFoundError:
        await interaction.response.send_message("Stok dosyası bulunamadı, lütfen yönetici ile iletişime geçin‼️", ephemeral=True)

# 🔓 Botu başlat (TOKEN ortam değişkeninden)
bot.run(os.getenv("TOKEN"))
