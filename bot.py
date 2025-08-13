"""
Discord Bot Implementation με 24/7 Keep-Alive
Περιέχει όλες τις εντολές και event handlers του bot
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import yt_dlp
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Opus loading για audio support
if not discord.opus.is_loaded():
    try:
        discord.opus.load_opus('opus')
    except OSError:
        try:
            discord.opus.load_opus('libopus.so.0')
        except OSError:
            try:
                discord.opus.load_opus('libopus.so')
            except OSError:
                logger.warning("Warning: Could not load Opus library - μουσική ίσως να μην δουλέψει")

# Bot configuration
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Configuration από τον αρχικό κώδικα
STAFF_ROLE_IDS = {
    1250890557279178864,
    1293607647223746661,
    1292372795631603847
}
OWNER_ID = 839148474314129419

active_mutes = {}
dm2_sent_count = 0  # Μετρητής για τα DM του /dm2

# YTDL & FFMPEG setup
ytdl_format_options = {
    'format': 'bestaudio[acodec=opus]/bestaudio/best',
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.webpage_url = data.get('webpage_url')

    @classmethod  
    async def from_url(cls, url, *, loop=None, stream=True):  
        loop = loop or asyncio.get_event_loop()  
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))  
        if 'entries' in data:  
            data = data['entries'][0]  
        filename = data['url'] if stream else ytdl.prepare_filename(data)  
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    await tree.sync()
    logger.info(f"✅ Bot online ως {bot.user}")
    logger.info(f'Bot ID: {bot.user.id if bot.user else "Unknown"}')
    logger.info(f'Guilds: {len(bot.guilds)}')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="24/7 στο Replit!"
        )
    )

def is_staff_or_owner(member: discord.Member) -> bool:
    """Έλεγχος αν ο χρήστης είναι staff ή owner"""
    return member.id == OWNER_ID or any(role.id in STAFF_ROLE_IDS for role in member.roles)

# Slash Commands από τον αρχικό κώδικα

@tree.command(name="dm", description="Στείλε μήνυμα σε κάποιον χρήστη (ιδιωτικό).")
@app_commands.describe(user="User to send message", message="The message to send")
async def dm(interaction: discord.Interaction, user: discord.User, message: str):
    if not is_staff_or_owner(interaction.user):
        await interaction.response.send_message("❌ Δεν έχεις δικαιώματα.", ephemeral=True)
        return
    try:
        await user.send(message)
        await interaction.response.send_message(f"✅ Μήνυμα σταλθηκε σε {user}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Σφάλμα: {e}", ephemeral=True)

@tree.command(name="dm2", description="Μαζικό DM σε μέλη ενός ρόλου.")
@app_commands.describe(role="Ο ρόλος στον οποίο ανήκουν οι χρήστες", message="Μήνυμα για αποστολή")
async def dm2(interaction: discord.Interaction, role: discord.Role, message: str):
    global dm2_sent_count
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Μόνο ο owner μπορεί να το χρησιμοποιήσει.", ephemeral=True)
        return

    members = [m for m in role.members if not m.bot]  
    dm2_sent_count = 0  
    await interaction.response.send_message(f"📤 Στέλνω μηνύματα σε μέλη με ρόλο {role.name}...")  

    for member in members:  
        try:  
            await member.send(message)  
            dm2_sent_count += 1  
            await asyncio.sleep(12)  # delay 12 δευτερολέπτων μεταξύ κάθε DM  
        except:  
            pass

@tree.command(name="dm2_status", description="Πόσα μηνύματα έχουν σταλθεί με το /dm2")
async def dm2_status(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Δεν έχεις δικαιώματα.", ephemeral=True)
        return
    await interaction.response.send_message(f"✉️ Έχουν σταλεί μηνύματα σε {dm2_sent_count} μέλη μέχρι τώρα.", ephemeral=True)

@tree.command(name="mute", description="Mute έναν χρήστη (για admins).")
@app_commands.describe(user="User to mute", duration="Duration σε λεπτά (προαιρετικό)")
async def mute(interaction: discord.Interaction, user: discord.Member, duration: int = None):
    if not is_staff_or_owner(interaction.user):
        await interaction.response.send_message("❌ Δεν έχεις δικαιώματα.", ephemeral=True)
        return

    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")  
    if not mute_role:  
        mute_role = await interaction.guild.create_role(name="Muted")  
        for ch in interaction.guild.channels:  
            await ch.set_permissions(mute_role, speak=False, send_messages=False, read_message_history=True, read_messages=False)  

    await user.add_roles(mute_role)  
    active_mutes[user.id] = True  
    await interaction.response.send_message(f"🔇 Ο {user} muteάρισε.", ephemeral=True)  

    if duration:  
        await asyncio.sleep(duration * 60)  
        if active_mutes.get(user.id):  
            await user.remove_roles(mute_role)  
            active_mutes.pop(user.id, None)

@tree.command(name="announce", description="Ανακοίνωση σε συγκεκριμένο κανάλι.")
@app_commands.describe(channel="Κανάλι για την ανακοίνωση", message="Το μήνυμα ανακοίνωσης")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not is_staff_or_owner(interaction.user):
        await interaction.response.send_message("❌ Δεν έχεις δικαιώματα.", ephemeral=True)
        return
    await channel.send(message)
    await interaction.response.send_message(f"✅ Ανακοίνωση στάλθηκε στο {channel.mention}.", ephemeral=True)

@tree.command(name="permissions", description="Δες τα δικαιώματά σου.")
async def permissions(interaction: discord.Interaction):
    perms = interaction.channel.permissions_for(interaction.user)
    perms_list = [perm for perm, value in perms if value]
    await interaction.response.send_message(f"✅ Δικαιώματά σου:\n- " + "\n- ".join(perms_list), ephemeral=True)

@tree.command(name="play", description="Παίξε μουσική από URL ή όνομα.")
@app_commands.describe(url="URL ή όνομα τραγουδιού")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Πρέπει να είσαι σε φωνητικό κανάλι για να παίξεις μουσική.", ephemeral=True)
        return

    channel = interaction.user.voice.channel  
    voice_client = interaction.guild.voice_client  

    if not voice_client:  
        voice_client = await channel.connect()  
    elif voice_client.channel != channel:  
        await voice_client.move_to(channel)  

    try:
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)  
        if voice_client.is_playing():  
            voice_client.stop()  
        voice_client.play(player)  
        await interaction.response.send_message(f"▶️ Παίζει: {player.title}", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Σφάλμα στη μουσική: {e}", ephemeral=True)

@tree.command(name="disconnect", description="Αποσυνδέσου από το φωνητικό κανάλι.")
async def disconnect(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("⏹️ Αποσυνδέθηκε.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Δεν είμαι συνδεδεμένος σε φωνητικό κανάλι.", ephemeral=True)

# Επιπλέον εντολές για debugging και status

@bot.command(name='ping')
async def ping(ctx):
    """Ping command to check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Καθυστέρηση: {latency}ms",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    """Bot information command"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📊 Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Users", value=len(bot.users), inline=True)
    embed.add_field(name="⚡ Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🏠 Hosting", value="Replit 24/7", inline=True)
    embed.add_field(name="🐍 Python", value="discord.py", inline=True)
    if bot.user:
        embed.add_field(name="📅 Created", value=bot.user.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text="Powered by Replit")
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status(ctx):
    """Check bot status"""
    if bot.user:
        uptime_seconds = (datetime.utcnow() - bot.user.created_at).total_seconds()
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
    else:
        hours = minutes = 0
    
    embed = discord.Embed(
        title="📊 Bot Status",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🟢 Status", value="Online & Running", inline=True)
    embed.add_field(name="⏱️ Session Time", value=f"{hours}h {minutes}m", inline=True)
    embed.add_field(name="🔗 Keep-Alive", value="Active", inline=True)
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Άγνωστη εντολή! Χρησιμοποιήστε `!help` για λίστα εντολών.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Λείπει παράμετρος! Χρησιμοποιήστε `!help {ctx.command}` για περισσότερες πληροφορίες.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Περιμένετε {error.retry_after:.1f} δευτερόλεπτα πριν χρησιμοποιήσετε ξανά αυτή την εντολή.")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send("❌ Προέκυψε σφάλμα κατά την εκτέλεση της εντολής.")

@bot.event
async def on_guild_join(guild):
    """Event when bot joins a new guild"""
    logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
    
    # Try to send a welcome message
    if guild.system_channel:
        embed = discord.Embed(
            title="👋 Γεια σας!",
            description="Ευχαριστώ που με προσθέσατε στον server σας!\nΧρησιμοποιήστε `/help` για slash commands ή `!help` για text commands.",
            color=discord.Color.green()
        )
        try:
            await guild.system_channel.send(embed=embed)
        except:
            logger.warning(f"Could not send welcome message to {guild.name}")

def run_bot():
    """Main function to run the bot"""
    # Get Discord token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("❌ DISCORD_TOKEN not found in environment variables!")
        logger.error("Please add your Discord bot token to the Secrets tab in Replit")
        return
    
    try:
        logger.info("Starting Discord bot...")
        bot.run(token, log_handler=None)  # We handle logging ourselves
    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token! Please check your DISCORD_TOKEN in Secrets.")
    except discord.HTTPException as e:
        logger.error(f"❌ HTTP error occurred: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        # Auto-restart mechanism
        logger.info("Attempting to restart bot in 30 seconds...")
        import time
        time.sleep(30)
        run_bot()
