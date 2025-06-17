import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import time
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    if not hasattr(bot, 'synced'):
        await bot.tree.sync()
        bot.synced = True
    print(f'Logged in as {bot.user.name} - {bot.user.id}')


@app_commands.command(name="ping", description="Bot gecikmesi kontrolü")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong! 🏓')
    start_time = time.time()
    latency = round(bot.latency * 1000)
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000)
    await interaction.followup.send(f'Gecikme: {latency} ms, İşlem süresi: {elapsed_time} ms 🏓')

@app_commands.command(name='zar', description='Zar atar')
async def zar(interaction: discord.Interaction):
    await interaction.response.send_message('Zar atılıyor 🎲!')
    await asyncio.sleep(1)
    result = random.randint(1, 6)
    await interaction.followup.send(f'Zar sonucu: {result} 🎲')

@app_commands.command(name='rastgele', description='Rastgele bir sayı üretir')
@app_commands.describe(min='Minimum değeriniz', max='Maksimum değeri giriniz')
async def rastgele(interaction: discord.Interaction, min: int, max: int):
    if min > max:
        await interaction.response.send_message("Geçersiz aralık.", ephemeral=True)
        return
    result = random.randint(min, max)
    await interaction.response.send_message(f'Rastgele sayı: {result}')

@app_commands.command(name="hesap_ekle", description="Hesapları satır satır gir (**txt olmasın aman dikkat*‼️*)")
@app_commands.describe(
    accounts="Her satıra bir hesap yaz",
    platform="Hesapların platformu",
    type="Hesap türü"
)
async def hesap_ekle(interaction: discord.Interaction, accounts: str, platform: str, type: str):
    # Yalnızca admin izni olanlar kullanabilir
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

@app_commands.command(name="stoklar", description="Hesapları listeler")
async def stoklar(interaction: discord.Interaction):
    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = f.readlines()

        if not accounts:
            await interaction.response.send_message("Stokta hesap bulunmuyor.", ephemeral=True)
            return

        await interaction.response.send_message(f"Stokta {len(accounts)} adet hesap var.", ephemeral=True)
    except FileNotFoundError:
        await interaction.response.send_message("Stok dosyası bulunamadı.", ephemeral=True)

@app_commands.command(name="help", description="Yardım menüsünü gösterir")
async def help_command(interaction: discord.Interaction):
    help_text = """
    **Yardım Menüsü**
    /ping - Bot gecikmesini kontrol eder.
    /zar - Zar atar.
    /rastgele - Rastgele bir sayı üretir.
    /hesap_ekle - Hesapları ekler.
    /stoklar - Hesapları listeler.
    /gen - İstediğiniz platform ve türde hesapları listeler.(premium sadece özel üyelik içindir.)
    /help - Yardım menüsünü gösterir.
    **Not:** Bu bot sadece yöneticiler tarafından kullanılabilir.
    **Kullanım:** Komutları kullanmak için `/` işaretini kullanın.
    """
    await interaction.response.send_message(help_text)
@app_commands.command(name="gen", description="İstediğiniz platform ve türde hesapları listeler.")
@app_commands.describe( platform="Hesapların platformu")
async def freegen(interaction: discord.Interaction, platform: str, type: str = 'free'):
    # Platformdan sadece 1 hesap ver.
    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = f.readlines()

        filtered_accounts = [acc for acc in accounts if acc.strip().split(',')[1] == platform and acc.strip().split(',')[2] == type]
        
        if not filtered_accounts:
            await interaction.response.send_message(f"{platform} platformunda {type} türünde hesap bulunamadı.", ephemeral=True)
            return

        # Sadece 1 hesap ver
        account = random.choice(filtered_accounts).strip()
        await interaction.response.send_message(f"Platform: {platform}, Tür: {type}\nHesap: {account}", ephemeral=True)
    except FileNotFoundError:
        await interaction.response.send_message("Stok dosyası bulunamadı,Lütfen yönetici ile iletişime geçin‼️‼️",ephemeral=True)
@app_commands.command(name="pregen", description="Premium hesap üretir (sadece premium üyeler için)")
async def pregen(interaction: discord.Interaction):
    allowed_roles = ['Premium', 'Booster']
    if not any(role.name in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("Bu komutu kullanmak için yeterli izniniz yok.", ephemeral=True)
        return

    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = f.readlines()

        if not accounts:
            await interaction.response.send_message("Stokta hesap bulunmuyor.", ephemeral=True)
            return

        filtered_accounts = [acc for acc in accounts if acc.strip().split(',')[2] == 'premium']
        if not filtered_accounts:
            await interaction.response.send_message("Stokta premium hesap bulunmuyor. Yönetici ile iletişime geçiniz‼️", ephemeral=True)
            return

        account = random.choice(filtered_accounts).strip()
        await interaction.response.send_message(f"Premium hesap:\n{account}", ephemeral=True)

        # Hesabı dosyadan kaldır (güvenli filtreleme yöntemi)
        accounts = [acc for acc in accounts if acc.strip() != account]

        with open("accounts.txt", "w", encoding="utf-8") as f:
            f.writelines(accounts)

    except FileNotFoundError:
        await interaction.response.send_message("Stok dosyası bulunamadı, lütfen yönetici ile iletişime geçin‼️", ephemeral=True)



# Slash komutlarını ekle
bot.tree.add_command(ping)
bot.tree.add_command(zar)
bot.tree.add_command(rastgele)
bot.tree.add_command(hesap_ekle)
bot.tree.add_command(stoklar)
bot.tree.add_command(freegen)
bot.tree.add_command(pregen)
bot.tree.add_command(help_command)
# TOKEN yerine render.com için ortam değişkeni kullan
bot.run(os.getenv("TOKEN"))
