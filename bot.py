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

# YTDL & FFMPEG setup με την καλύτερη ποιότητα ήχου Discord
ytdl_format_options = {
    'format': 'bestaudio[ext=webm][acodec=opus]/bestaudio[ext=m4a][acodec=aac]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extractaudio': True,
    'audioformat': 'opus',
    'audioquality': '0',  # Καλύτερη ποιότητα (0 = best)
    'prefer_ffmpeg': True,
}

# Ultra Premium FFMPEG ρυθμίσεις για τον καλύτερο Discord ήχο
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn -ar 48000 -ac 2 -ab 512k -acodec libopus -compression_level 10 -frame_duration 20 -application audio -cutoff 20000 -f opus -threads 4'
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
    try:
        synced = await tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")
    
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

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    logger.error(f"Command error: {error}")
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Σφάλμα: {error}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handle slash command errors"""
    logger.error(f"Slash command error: {error}")
    if interaction.response.is_done():
        await interaction.followup.send(f"❌ Σφάλμα: {error}", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Σφάλμα: {error}", ephemeral=True)

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

# Προστασία από staff abuse για role permissions
@bot.event
async def on_member_update(before, after):
    """Προστασία από αλλαγές permissions σε roles από staff - ΕΙΔΙΚΑ BAN PERMISSIONS"""
    # Αν δεν είναι αλλαγή ρόλων, επιστροφή
    if before.roles == after.roles:
        return
    
    # Αν ο χρήστης που έκανε την αλλαγή είναι owner, επιτρέπεται
    if after.id == OWNER_ID:
        return
    
    # Βρες ποιοι ρόλοι προστέθηκαν
    added_roles = set(after.roles) - set(before.roles)
    
    # Έλεγχος για BAN PERMISSIONS - ΑΠΑΓΟΡΕΥΜΕΝΟ για όλους εκτός owner
    for role in added_roles:
        role_perms = role.permissions
        if role_perms.ban_members or role_perms.administrator:
            # ΑΦΑΙΡΕΣΗ του ρόλου αμέσως αν έχει ban permissions
            try:
                await after.remove_roles(role, reason="Απαγορευμένα ban permissions - μόνο owner")
                logger.warning(f"🚫 BLOCKED: Αφαίρεσα ρόλο {role.name} από {after.mention} - ban permissions!")
                
                # Ειδοποίηση σε DM στον owner
                owner = bot.get_user(OWNER_ID)
                if owner:
                    embed = discord.Embed(
                        title="🚫 SECURITY ALERT: Ban Permission Blocked",
                        description=f"Αφαίρεσα ρόλο **{role.name}** από {after.mention}",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Λόγος", value="Ρόλος με ban permissions - μόνο εσύ μπορείς να τον δώσεις", inline=False)
                    embed.add_field(name="Χρόνος", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=False)
                    await owner.send(embed=embed)
                    
            except discord.Forbidden:
                logger.error(f"❌ Δεν μπόρεσα να αφαιρέσω ρόλο {role.name} από {after.mention}")
        
        # Καταγραφή άλλων επικίνδυνων permissions
        elif any(getattr(role_perms, perm, False) for perm in ['manage_guild', 'manage_roles', 'manage_channels', 'kick_members']):
            logger.warning(f"⚠️ Επικίνδυνος ρόλος {role.name} δόθηκε στο {after.mention}")

@tree.command(name="protect_roles", description="Ενεργοποίηση προστασίας ρόλων (Owner μόνο)")
async def protect_roles(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Μόνο ο owner μπορεί να χρησιμοποιήσει αυτή την εντολή.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🛡️ Προστασία Ρόλων Ενεργή",
        description="Το bot **ΑΥΤΟΜΑΤΑ ΑΦΑΙΡΕΙ** ban permissions από όλους εκτός owner",
        color=discord.Color.red()
    )
    embed.add_field(
        name="🚫 ΑΥΤΟΜΑΤΗ ΑΦΑΙΡΕΣΗ:",
        value="• Ban Members (ΑΠΑΓΟΡΕΥΜΕΝΟ)\n• Administrator (ΑΠΑΓΟΡΕΥΜΕΝΟ)",
        inline=False
    )
    embed.add_field(
        name="⚠️ Παρακολούθηση:",
        value="• Manage Server\n• Manage Roles\n• Manage Channels\n• Kick Members",
        inline=False
    )
    embed.add_field(
        name="✅ Ασφάλεια:",
        value="Μόνο ο Owner μπορεί να έχει ban permissions",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Επιπλέον προστασία για ban command
@tree.command(name="ban", description="Ban χρήστη (ΜΟΝΟ OWNER)")
@app_commands.describe(user="Χρήστης για ban", reason="Λόγος ban")
async def ban_user(interaction: discord.Interaction, user: discord.Member, reason: str = "Δεν δόθηκε λόγος"):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("🚫 **ΑΠΑΓΟΡΕΥΜΕΝΟ**: Μόνο ο owner μπορεί να κάνει ban!", ephemeral=True)
        return
    
    try:
        await user.ban(reason=f"Ban από owner: {reason}")
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"**{user}** banned επιτυχώς",
            color=discord.Color.red()
        )
        embed.add_field(name="Λόγος", value=reason, inline=False)
        embed.add_field(name="Από", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Σφάλμα ban: {e}", ephemeral=True)

# Music Player Controls με Buttons
class MusicControlView(discord.ui.View):
    def __init__(self, voice_client, player):
        super().__init__(timeout=300)  # 5 λεπτά timeout
        self.voice_client = voice_client
        self.player = player
        self.is_paused = False

    @discord.ui.button(label='⏸️ Stop', style=discord.ButtonStyle.red, custom_id='stop')
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            await interaction.response.send_message("⏹️ Μουσική σταμάτησε!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)

    @discord.ui.button(label='▶️ Start/Pause', style=discord.ButtonStyle.green, custom_id='start_pause')
    async def start_pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.pause()
                self.is_paused = True
                button.label = '▶️ Resume'
                await interaction.response.edit_message(view=self)
                await interaction.followup.send("⏸️ Μουσική σε παύση!", ephemeral=True)
            elif self.voice_client.is_paused():
                self.voice_client.resume()
                self.is_paused = False
                button.label = '⏸️ Pause'
                await interaction.response.edit_message(view=self)
                await interaction.followup.send("▶️ Μουσική συνεχίζει!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν είμαι συνδεδεμένος!", ephemeral=True)

    @discord.ui.button(label='🔊 Φωνή', style=discord.ButtonStyle.blurple, custom_id='volume')
    async def volume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client and hasattr(self.voice_client.source, 'volume'):
            current_volume = self.voice_client.source.volume * 100
            await interaction.response.send_message(f"🔊 Τρέχουσα ένταση: {current_volume:.0f}%\nΧρησιμοποιήστε `/volume [0-100]` για αλλαγή!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν μπορώ να ελέγξω την ένταση αυτή τη στιγμή!", ephemeral=True)

    @discord.ui.button(label='📜 Info', style=discord.ButtonStyle.gray, custom_id='info')
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player and hasattr(self.player, 'title'):
            embed = discord.Embed(
                title="🎵 Τώρα Παίζει",
                description=f"**{self.player.title}**",
                color=discord.Color.blue()
            )
            if hasattr(self.player, 'webpage_url'):
                embed.add_field(name="🔗 Link", value=self.player.webpage_url, inline=False)
            if hasattr(self.player, 'thumbnail'):
                embed.set_thumbnail(url=self.player.thumbnail)
            
            embed.add_field(name="🎛️ Controls", value="Χρησιμοποιήστε τα buttons για έλεγχο!", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν βρέθηκαν πληροφορίες!", ephemeral=True)

@tree.command(name="play", description="Παίξε μουσική από URL ή όνομα με πλήρη controls (όλοι).")
@app_commands.describe(url="URL ή όνομα τραγουδιού")
async def play(interaction: discord.Interaction, url: str):
    # Όλοι μπορούν να χρησιμοποιήσουν το /play
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Πρέπει να είσαι σε φωνητικό κανάλι για να παίξεις μουσική.", ephemeral=True)
        return

    channel = interaction.user.voice.channel  
    voice_client = interaction.guild.voice_client  

    # Defer response για να έχουμε χρόνο για processing
    await interaction.response.defer()

    if not voice_client:  
        voice_client = await channel.connect()  
    elif voice_client.channel != channel:  
        await voice_client.move_to(channel)  

    try:
        # Καλύτερες ρυθμίσεις ήχου
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        
        if voice_client.is_playing():  
            voice_client.stop()  
        
        # Παίξιμο με καλύτερη ποιότητα
        voice_client.play(player, after=lambda e: logger.error(f'Player error: {e}') if e else None)
        
        # Δημιουργία embed με πληροφορίες
        embed = discord.Embed(
            title="🎵 Τώρα Παίζει",
            description=f"**{player.title}**",
            color=discord.Color.green()
        )
        
        if hasattr(player, 'webpage_url') and player.webpage_url:
            embed.add_field(name="🔗 Link", value=f"[Άνοιγμα στο YouTube]({player.webpage_url})", inline=True)
        
        embed.add_field(name="🎛️ Controls", value="Χρησιμοποιήστε τα buttons παρακάτω!", inline=False)
        embed.set_footer(text="🎧 Απολαύστε τη μουσική!")
        
        if hasattr(player, 'thumbnail') and player.thumbnail:
            embed.set_thumbnail(url=player.thumbnail)
        
        # Δημιουργία control view
        view = MusicControlView(voice_client, player)
        
        await interaction.followup.send(embed=embed, view=view)
        
    except Exception as e:
        logger.error(f"Music play error: {e}")
        await interaction.followup.send(f"❌ Σφάλμα στη μουσική: {str(e)}", ephemeral=True)

@tree.command(name="volume", description="Άλλαξε την ένταση της μουσικής (0-100).")
@app_commands.describe(volume="Ένταση από 0 έως 100")
async def volume(interaction: discord.Interaction, volume: int):
    if not interaction.guild.voice_client:
        await interaction.response.send_message("❌ Δεν είμαι συνδεδεμένος σε φωνητικό κανάλι!", ephemeral=True)
        return
    
    if not 0 <= volume <= 100:
        await interaction.response.send_message("❌ Η ένταση πρέπει να είναι μεταξύ 0 και 100!", ephemeral=True)
        return
    
    voice_client = interaction.guild.voice_client
    if voice_client.source and hasattr(voice_client.source, 'volume'):
        voice_client.source.volume = volume / 100.0
        await interaction.response.send_message(f"🔊 Ένταση ρυθμίστηκε στο {volume}%!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Δεν μπορώ να ρυθμίσω την ένταση αυτή τη στιγμή!", ephemeral=True)

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
