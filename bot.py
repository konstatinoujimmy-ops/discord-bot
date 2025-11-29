"""
Discord Bot Implementation με Ultra Premium Audio System
Περιέχει όλες τις εντολές και event handlers του bot
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import os
import yt_dlp
import logging
import io
import random
import aiohttp
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
from anime_data import ANIME_CHARACTERS, get_random_characters

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

STAFF_ROLE_IDS = {
    1250890557279178864,
    1293607647223746661,
    1292372795631603847
}
OWNER_ID = 839148474314129419

# Recall tracking file
RECALL_TRACKING_FILE = 'recall_tracking.json'

def load_recall_tracking():
    """Load recall tracking data"""
    if os.path.exists(RECALL_TRACKING_FILE):
        try:
            with open(RECALL_TRACKING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_recall_tracking(data):
    """Save recall tracking data"""
    with open(RECALL_TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_contacted_members():
    """Load list of members we've established DM contact with"""
    tracking = load_recall_tracking()
    return set(tracking.get('contacted', []))

def add_contacted_member(user_id):
    """Add a member to the contacted list (we've opened DM channel with them)"""
    tracking = load_recall_tracking()
    if 'contacted' not in tracking:
        tracking['contacted'] = []
    if user_id not in tracking['contacted']:
        tracking['contacted'].append(user_id)
    save_recall_tracking(tracking)

active_mutes = {}
dm2_sent_count = 0
recall_left_members_sent_count = 0

security_tracker = {
    'channel_creations': defaultdict(list),
    'everyone_mentions': defaultdict(list),
    'bans': defaultdict(list),
    'kicks': defaultdict(list),
    'timeouts': defaultdict(list),
    'role_removals': {}
}

active_giveaways = {}
infractions_db = {}  # {guild_id: {user_id: [{'type': 'TIMEOUT'|'MUTE'|'KICK'|'BAN', 'date': timestamp, 'reason': str}]}}

# Anime Character System
anime_characters = {}  # {guild_id: {user_id: {'char_id': X, 'points': Y, 'message_count': Z}}}
user_message_counts = {}  # {guild_id: {user_id: message_count}}

# Persistent storage file
DATA_FILE = "anime_data.json"

def load_anime_data():
    """Load anime characters from file"""
    global anime_characters
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys to integers
                anime_characters.clear()  # Clear existing data
                for guild_id_str, users in data.items():
                    guild_id = int(guild_id_str)
                    anime_characters[guild_id] = {}
                    for user_id_str, char_data in users.items():
                        user_id = int(user_id_str)
                        # Ensure all required fields exist
                        if 'last_raid_time' not in char_data:
                            char_data['last_raid_time'] = 0
                        anime_characters[guild_id][user_id] = char_data
                logger.info(f"✅ Loaded anime data for {sum(len(v) for v in anime_characters.values())} users")
        else:
            logger.info("📄 No anime_data.json file found - starting fresh")
    except Exception as e:
        logger.error(f"Error loading anime data: {e}")

def save_anime_data():
    """Save anime characters to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(anime_characters, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving anime data: {e}")

def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to minutes.
    Accepts: '5m', '2h', '1d', or plain numbers like '60'
    Returns: duration in minutes
    """
    duration_str = duration_str.strip().lower()
    
    if duration_str.endswith('m'):
        return int(duration_str[:-1])
    elif duration_str.endswith('h'):
        hours = int(duration_str[:-1])
        return hours * 60
    elif duration_str.endswith('d'):
        days = int(duration_str[:-1])
        return days * 24 * 60
    else:
        return int(duration_str)

ytdl_format_options = {
    'format': 'worstaudio/worst',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'socket_timeout': 30,
    'ignoreerrors': False,
    'nocheckcertificate': True,
    'no_color': True,
    'noplaylist': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn -q:a 9 -ar 48000 -ac 2'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.loop = False
        self.loop_queue = False
        
    def add(self, song):
        self.queue.append(song)
    
    def next(self):
        if self.loop and self.current:
            return self.current
        if self.loop_queue and self.current:
            self.queue.append(self.current)
        if self.queue:
            self.current = self.queue.popleft()
            return self.current
        self.current = None
        return None
    
    def skip(self):
        if self.queue:
            self.current = self.queue.popleft()
            return self.current
        self.current = None
        return None
    
    def clear(self):
        self.queue.clear()
        self.current = None
    
    def shuffle(self):
        temp_list = list(self.queue)
        random.shuffle(temp_list)
        self.queue = deque(temp_list)
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def size(self):
        return len(self.queue)

music_queues = {}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.8):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.webpage_url = data.get('webpage_url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label='🎟️ Enter', style=discord.ButtonStyle.green, custom_id='giveaway_enter')
    async def enter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.giveaway_id not in active_giveaways:
            await interaction.response.send_message("❌ Αυτό το giveaway δεν είναι πια ενεργό!", ephemeral=True)
            return
        
        giveaway = active_giveaways[self.giveaway_id]
        
        if interaction.user.id in giveaway['participants']:
            await interaction.response.send_message("⚠️ Έχεις ήδη μπει στο giveaway!", ephemeral=True)
            return
        
        giveaway['participants'].append(interaction.user.id)
        await interaction.response.send_message("✅ Μπήκες επιτυχώς στο giveaway! Καλή τύχη! 🍀", ephemeral=True)
        
        logger.info(f"{interaction.user} entered giveaway {self.giveaway_id}")

    @discord.ui.button(label='View Giveaway', style=discord.ButtonStyle.gray, custom_id='giveaway_view')
    async def view_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.giveaway_id not in active_giveaways:
            await interaction.response.send_message("❌ Αυτό το giveaway δεν είναι πια ενεργό!", ephemeral=True)
            return
        
        giveaway = active_giveaways[self.giveaway_id]
        participant_count = len(giveaway['participants'])
        
        embed = discord.Embed(
            title=f"🎉 {giveaway['prize']}",
            description=f"**Συμμετέχοντες:** {participant_count}",
            color=discord.Color.blue()
        )
        
        if participant_count > 0:
            participant_list = []
            for user_id in giveaway['participants'][:10]:
                user = bot.get_user(user_id)
                if user:
                    participant_list.append(f"• {user.mention}")
            
            embed.add_field(
                name=f"👥 Πρώτοι {min(10, participant_count)} Συμμετέχοντες",
                value="\n".join(participant_list) if participant_list else "Κανένας ακόμα",
                inline=False
            )
            
            if participant_count > 10:
                embed.add_field(
                    name="➕ Περισσότεροι",
                    value=f"και {participant_count - 10} ακόμα...",
                    inline=False
                )
        
        time_left = giveaway['end_time'] - datetime.now()
        minutes_left = int(time_left.total_seconds() / 60)
        embed.add_field(name="⏱️ Χρόνος που απομένει", value=f"{minutes_left} λεπτά", inline=True)
        embed.add_field(name="🏆 Νικητές", value=giveaway['winners'], inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.red, custom_id='giveaway_cancel')
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Μόνο ο owner μπορεί να ακυρώσει το giveaway!", ephemeral=True)
            return
        
        if self.giveaway_id not in active_giveaways:
            await interaction.response.send_message("❌ Αυτό το giveaway δεν είναι πια ενεργό!", ephemeral=True)
            return
        
        giveaway = active_giveaways[self.giveaway_id]
        prize_name = giveaway['prize']
        channel = bot.get_channel(giveaway['channel_id'])
        
        del active_giveaways[self.giveaway_id]
        
        cancel_embed = discord.Embed(
            title="🚫 Giveaway Cancelled",
            description=f"**{prize_name}**\n\nΤο giveaway ακυρώθηκε από τον host.",
            color=discord.Color.red()
        )
        
        try:
            if channel:
                await channel.send(embed=cancel_embed)
            await interaction.message.delete()
        except:
            pass
        
        await interaction.response.send_message(f"🚫 Το giveaway **{prize_name}** ακυρώθηκε επιτυχώς!", ephemeral=True)
        logger.info(f"Giveaway {self.giveaway_id} cancelled by owner")

@bot.event
async def on_ready():
    # Load persistent anime character data
    load_anime_data()
    
    # Initialize all_members_ever with current guild members (first run)
    tracking = load_recall_tracking()
    if 'all_members_ever' not in tracking:
        tracking['all_members_ever'] = []
        for guild in bot.guilds:
            try:
                async for member in guild.fetch_members(limit=None):
                    if member.id not in tracking['all_members_ever']:
                        tracking['all_members_ever'].append(member.id)
            except:
                pass
        save_recall_tracking(tracking)
        logger.info(f"✅ Initialized all_members_ever with {len(tracking['all_members_ever'])} members")
    
    try:
        synced = await tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")
    
    logger.info(f"✅ Bot online ως {bot.user}")
    logger.info(f'Bot ID: {bot.user.id if bot.user else "Unknown"}')
    logger.info(f'Guilds: {len(bot.guilds)}')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="🎵 Ultra Premium Music | 🛡️ Security 24/7"
        )
    )
    
    cleanup_security_logs.start()
    update_giveaway_timers.start()

@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Command error: {error}")
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Σφάλμα: {error}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    logger.error(f"Slash command error: {error}")
    if interaction.response.is_done():
        await interaction.followup.send(f"❌ Σφάλμα: {error}", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Σφάλμα: {error}", ephemeral=True)

@bot.event
async def on_guild_channel_create(channel):
    if hasattr(channel, 'guild') and channel.guild:
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if entry.user and entry.user.id != OWNER_ID:
                if await check_rate_limit(entry.user.id, 'channel_creations', 2, 10):
                    member = channel.guild.get_member(entry.user.id)
                    if member:
                        await remove_all_roles_except_everyone(
                            member, 
                            f"Rapid channel creation (3+ channels in 10 minutes)"
                        )
            break

@bot.event
async def on_message(message):
    if message.author.id == OWNER_ID or message.author.bot:
        return
    
    if message.mention_everyone or '@everyone' in message.content or '@here' in message.content:
        if await check_rate_limit(message.author.id, 'everyone_mentions', 1, 60):
            await remove_all_roles_except_everyone(
                message.author,
                f"Multiple @everyone/@here mentions (10 hour penalty)"
            )
    
    await bot.process_commands(message)

@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if entry.user and entry.user.id != OWNER_ID:
            if await check_rate_limit(entry.user.id, 'bans', 4, 60):
                member = guild.get_member(entry.user.id)
                if member:
                    await remove_all_roles_except_everyone(
                        member,
                        f"Excessive banning (5+ bans in 1 hour)"
                    )
        break

@bot.event
async def on_member_join(member):
    """Ανοίγει DM κανάλι με νέο member ώστε να μπορούμε να του στείλουμε μήνυμα αργότερα"""
    try:
        # Προσθέτουμε το member στη "contacted" list πριν προσπαθήσουμε να ανοίξουμε DM
        add_contacted_member(member.id)
        
        # Track ALL members that have ever joined (for finding voluntary departures)
        tracking = load_recall_tracking()
        if 'all_members_ever' not in tracking:
            tracking['all_members_ever'] = []
        if member.id not in tracking['all_members_ever']:
            tracking['all_members_ever'].append(member.id)
            save_recall_tracking(tracking)
        
        # Ανοίγουμε DM channel με ένα μικρό μήνυμα
        # Αυτό κάνει το Discord να δημιουργήσει μόνιμο κανάλι DM ακόμα κι αν ο user φύγει ή έχει κλειστά τα DMsΓια να είναι ασφαλέστερο, ανοίγουμε απλώς το κανάλι χωρίς να στείλουμε μήνυμα
        try:
            dm = await member.create_dm()
            logger.info(f"✅ DM channel opened με {member.name} (ID: {member.id}) - Ready for recall!")
        except:
            logger.info(f"⚠️ Could not open DM με {member.name}, αλλά προστέθηκε στη contacted list")
    except Exception as e:
        logger.error(f"Error processing member join {member.name}: {e}")

@bot.event
async def on_member_remove(member):
    if member.guild:
        async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
            if entry.user and entry.user.id != OWNER_ID and entry.target.id == member.id:
                if await check_rate_limit(entry.user.id, 'kicks', 10, 60):
                    perpetrator = member.guild.get_member(entry.user.id)
                    if perpetrator:
                        await remove_all_roles_except_everyone(
                            perpetrator,
                            f"Excessive kicking (11+ kicks in 1 hour)"
                        )
            break

@bot.event
async def on_member_update(before, after):
    if before.timed_out_until is None and after.timed_out_until is not None:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
            if (entry.user and entry.user.id != OWNER_ID and 
                entry.target.id == after.id):
                
                if await check_rate_limit(entry.user.id, 'timeouts', 10, 60):
                    perpetrator = after.guild.get_member(entry.user.id)
                    if perpetrator:
                        await remove_all_roles_except_everyone(
                            perpetrator,
                            f"Excessive timeouts (11+ timeouts in 1 hour)"
                        )
            break
    
    if before.roles == after.roles:
        return
    
    if after.id == OWNER_ID:
        return
    
    added_roles = set(after.roles) - set(before.roles)
    
    for role in added_roles:
        role_perms = role.permissions
        if role_perms.ban_members or role_perms.administrator:
            try:
                await after.remove_roles(role, reason="Απαγορευμένα ban permissions - μόνο owner")
                logger.warning(f"🚫 BLOCKED: Αφαίρεσα ρόλο {role.name} από {after.mention} - ban permissions!")
                
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

def is_staff_or_owner(member: discord.Member) -> bool:
    return member.id == OWNER_ID or any(role.id in STAFF_ROLE_IDS for role in member.roles)

async def remove_all_roles_except_everyone(member: discord.Member, reason: str):
    try:
        roles_to_remove = [role for role in member.roles if role.name != "@everyone"]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason=f"🛡️ Security violation: {reason}")
            
            if "everyone/here mentions" in reason:
                security_tracker['role_removals'][member.id] = datetime.now() + timedelta(hours=10)
            
            owner = bot.get_user(OWNER_ID)
            if owner:
                embed = discord.Embed(
                    title="🚨 SECURITY ALERT",
                    description=f"**User:** {member.mention} ({member.id})\n**Reason:** {reason}\n**Action:** All roles removed",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                try:
                    await owner.send(embed=embed)
                except:
                    pass
            
            logger.warning(f"🛡️ SECURITY: Removed all roles from {member} - {reason}")
            return True
    except Exception as e:
        logger.error(f"Failed to remove roles from {member}: {e}")
        return False

@tasks.loop(hours=1)
async def cleanup_security_logs():
    now = datetime.now()
    cutoff_time = now - timedelta(hours=24)
    
    for action_type in ['channel_creations', 'everyone_mentions', 'bans', 'kicks', 'timeouts']:
        for user_id in list(security_tracker[action_type].keys()):
            security_tracker[action_type][user_id] = [
                timestamp for timestamp in security_tracker[action_type][user_id] 
                if timestamp > cutoff_time
            ]
            if not security_tracker[action_type][user_id]:
                del security_tracker[action_type][user_id]
    
    expired_users = [
        user_id for user_id, expiry_time in security_tracker['role_removals'].items()
        if now > expiry_time
    ]
    for user_id in expired_users:
        del security_tracker['role_removals'][user_id]

async def check_rate_limit(user_id: int, action_type: str, limit: int, window_minutes: int = 60) -> bool:
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=window_minutes)
    
    security_tracker[action_type][user_id] = [
        timestamp for timestamp in security_tracker[action_type][user_id] 
        if timestamp > cutoff_time
    ]
    
    security_tracker[action_type][user_id].append(now)
    
    return len(security_tracker[action_type][user_id]) > limit

@tasks.loop(minutes=1)
async def update_giveaway_timers():
    now = datetime.now()
    finished_giveaways = []
    
    for giveaway_id, giveaway in active_giveaways.items():
        if now >= giveaway['end_time']:
            finished_giveaways.append(giveaway_id)
    
    for giveaway_id in finished_giveaways:
        await end_giveaway(giveaway_id)

async def end_giveaway(giveaway_id):
    if giveaway_id not in active_giveaways:
        return
    
    giveaway = active_giveaways[giveaway_id]
    channel = bot.get_channel(giveaway['channel_id'])
    
    if not channel:
        del active_giveaways[giveaway_id]
        return
    
    participants = giveaway['participants']
    
    if giveaway['fixed_winner']:
        winner_id = giveaway['fixed_winner']
        logger.info(f"Giveaway {giveaway_id}: Fixed winner selected (hidden) - {winner_id}")
    elif len(participants) > 0:
        winner_id = random.choice(participants)
        logger.info(f"Giveaway {giveaway_id}: Random winner selected - {winner_id}")
    else:
        embed = discord.Embed(
            title="🎉 Giveaway Ended",
            description=f"**{giveaway['prize']}**\n\n❌ Κανένας δεν συμμετείχε!",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        del active_giveaways[giveaway_id]
        return
    
    winner = bot.get_user(winner_id)
    
    embed = discord.Embed(
        title="🎉 GIVEAWAY ENDED! 🎉",
        description=f"**{giveaway['prize']}**",
        color=discord.Color.gold()
    )
    embed.add_field(name="🏆 Νικητής", value=winner.mention if winner else "Unknown User", inline=False)
    embed.add_field(name="👥 Συμμετέχοντες", value=len(participants), inline=True)
    embed.add_field(name="🎊 Συγχαρητήρια!", value="Ο νικητής θα ειδοποιηθεί!", inline=False)
    embed.set_footer(text=f"Hosted by {giveaway['host_name']}")
    
    await channel.send(content=winner.mention if winner else None, embed=embed)
    
    if winner:
        try:
            dm_embed = discord.Embed(
                title="🎊 Συγχαρητήρια! Κέρδισες!",
                description=f"Κέρδισες το giveaway: **{giveaway['prize']}**!",
                color=discord.Color.gold()
            )
            dm_embed.add_field(name="Server", value=giveaway.get('guild_name', 'Unknown'), inline=False)
            await winner.send(embed=dm_embed)
        except:
            logger.warning(f"Could not DM winner {winner_id}")
    
    try:
        message = await channel.fetch_message(giveaway['message_id'])
        await message.edit(view=None)
    except:
        pass
    
    del active_giveaways[giveaway_id]
    logger.info(f"Giveaway {giveaway_id} ended successfully")

@tree.command(name="giveaway", description="🎁 Δημιούργησε ένα giveaway (Owner μόνο)")
@app_commands.describe(
    channel="Κανάλι για το giveaway",
    winners="Αριθμός νικητών",
    duration="Διάρκεια (π.χ. 5m, 2h, 1d ή 60 για λεπτά)",
    prize="Το βραβείο/όνομα του giveaway",
    fixed_winner="(ΚΡΥΦΟ) Όρισε συγκεκριμένο νικητή - προαιρετικό"
)
async def giveaway(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    winners: int,
    duration: str,
    prize: str,
    fixed_winner: discord.User = None
):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Μόνο ο owner μπορεί να δημιουργήσει giveaway!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        duration_minutes = parse_duration(duration)
    except (ValueError, IndexError):
        await interaction.followup.send("❌ Άκυρο format διάρκειας! Χρησιμοποίησε: 5m (λεπτά), 2h (ώρες), 1d (ημέρες) ή απλό νούμερο (π.χ. 60)", ephemeral=True)
        return
    
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    giveaway_id = f"{channel.id}_{int(datetime.now().timestamp())}"
    
    duration_display = duration if any(duration.endswith(x) for x in ['m', 'h', 'd']) else f"{duration} minutes"
    
    embed = discord.Embed(
        title=prize,
        description=f"Πάτησε **🎟️ Enter** για να μπεις!\n\n**Time Remaining**\nin {duration_display} (<t:{int(end_time.timestamp())}:R>)",
        color=discord.Color.blue()
    )
    embed.add_field(name="Hosted By", value=interaction.user.mention, inline=False)
    embed.set_image(url="https://i.imgur.com/9n8z5YQ.png")
    embed.set_footer(text=f"{winners} winner{'s' if winners > 1 else ''} | Ends At")
    embed.timestamp = end_time
    
    view = GiveawayView(giveaway_id)
    
    message = await channel.send(embed=embed, view=view)
    
    active_giveaways[giveaway_id] = {
        'channel_id': channel.id,
        'message_id': message.id,
        'prize': prize,
        'winners': winners,
        'duration': duration_display,
        'end_time': end_time,
        'participants': [],
        'host_id': interaction.user.id,
        'host_name': interaction.user.display_name,
        'fixed_winner': fixed_winner.id if fixed_winner else None,
        'guild_name': interaction.guild.name if interaction.guild else 'Unknown'
    }
    
    confirmation_msg = f"✅ Το giveaway δημιουργήθηκε στο {channel.mention}!\n\n**Prize:** {prize}\n**Duration:** {duration_display}\n**Winners:** {winners}"
    
    if fixed_winner:
        confirmation_msg += f"\n\n🎯 **ΚΡΥΦΟΣ ΝΙΚΗΤΗΣ:** {fixed_winner.mention} (μόνο εσύ το βλέπεις αυτό)"
    
    await interaction.followup.send(confirmation_msg, ephemeral=True)
    
    logger.info(f"Giveaway created by {interaction.user}: {prize} in {channel.name} for {duration_display}")
    if fixed_winner:
        logger.info(f"Fixed winner set: {fixed_winner}")

@tree.command(name="giveaway_add", description="🎁 Πρόσθεσε κάποιον στο giveaway χειροκίνητα (Owner μόνο)")
@app_commands.describe(
    message_id="Το ID του μηνύματος του giveaway",
    user="Ο χρήστης που θα προστεθεί"
)
async def giveaway_add(interaction: discord.Interaction, message_id: str, user: discord.User):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Μόνο ο owner!", ephemeral=True)
        return
    
    found_giveaway = None
    for giveaway_id, giveaway in active_giveaways.items():
        if str(giveaway['message_id']) == message_id:
            found_giveaway = giveaway
            break
    
    if not found_giveaway:
        await interaction.response.send_message("❌ Δεν βρέθηκε ενεργό giveaway με αυτό το message ID!", ephemeral=True)
        return
    
    if user.id in found_giveaway['participants']:
        await interaction.response.send_message(f"⚠️ Ο {user.mention} έχει ήδη μπει στο giveaway!", ephemeral=True)
        return
    
    found_giveaway['participants'].append(user.id)
    await interaction.response.send_message(
        f"✅ Ο {user.mention} προστέθηκε χειροκίνητα στο giveaway!\n**Prize:** {found_giveaway['prize']}\n**Συνολικοί συμμετέχοντες:** {len(found_giveaway['participants'])}",
        ephemeral=True
    )
    
    logger.info(f"Owner manually added {user} to giveaway: {found_giveaway['prize']}")

@tree.command(name="security_status", description="Εμφανίζει την κατάσταση ασφαλείας του server")
async def security_status(interaction: discord.Interaction):
    if not is_staff_or_owner(interaction.user):
        await interaction.response.send_message("❌ Μόνο ο owner και το staff μπορούν να δουν τα security stats!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🛡️ Security Monitor Status", 
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    for action_type, display_name in [
        ('channel_creations', 'Channel Creations'),
        ('everyone_mentions', '@everyone/@here Mentions'),
        ('bans', 'Bans'),
        ('kicks', 'Kicks'),
        ('timeouts', 'Timeouts')
    ]:
        active_users = len(security_tracker[action_type])
        total_actions = sum(len(actions) for actions in security_tracker[action_type].values())
        embed.add_field(
            name=f"📊 {display_name}",
            value=f"Active users: {active_users}\nTotal actions: {total_actions}",
            inline=True
        )
    
    active_removals = len(security_tracker['role_removals'])
    embed.add_field(
        name="🚫 Active Role Removals",
        value=f"{active_removals} users currently without roles",
        inline=True
    )
    
    embed.set_footer(text="Monitoring 24/7 | Auto-cleanup every hour")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="security_report", description="Generates a comprehensive security report")
async def security_report(interaction: discord.Interaction):
    if not is_staff_or_owner(interaction.user):
        await interaction.response.send_message("❌ Only owner and staff can generate security reports!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    report_content = generate_security_report(interaction.guild)
    
    report_file = discord.File(
        fp=io.BytesIO(report_content.encode()),
        filename=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    
    summary_embed = discord.Embed(
        title="🛡️ Security Report Generated",
        description="Complete security analysis attached as file",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    summary_embed.add_field(
        name="📊 Report Contents",
        value="• Violation statistics\n• User activity logs\n• Security timeline\n• Risk assessment\n• Recommendations",
        inline=False
    )
    
    await interaction.followup.send(
        embed=summary_embed,
        file=report_file,
        ephemeral=True
    )

def generate_security_report(guild) -> str:
    now = datetime.now()
    report = []
    
    report.append("=" * 80)
    report.append(f"SECURITY REPORT - {guild.name}")
    report.append(f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("=" * 80)
    report.append("")
    
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 40)
    total_violations = 0
    active_penalties = len(security_tracker['role_removals'])
    
    for action_type in ['channel_creations', 'everyone_mentions', 'bans', 'kicks', 'timeouts']:
        total_violations += sum(len(actions) for actions in security_tracker[action_type].values())
    
    report.append(f"Total Security Violations (24h): {total_violations}")
    report.append(f"Users Currently Penalized: {active_penalties}")
    report.append(f"Security Status: {'HIGH RISK' if total_violations > 50 else 'MODERATE RISK' if total_violations > 20 else 'LOW RISK'}")
    report.append("")
    
    report.append("=" * 80)
    report.append("End of Report")
    report.append("=" * 80)
    
    return "\n".join(report)

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
            await asyncio.sleep(9)
        except:
            pass

@tree.command(name="dm2_status", description="Πόσα μηνύματα έχουν σταλθεί με το /dm2")
async def dm2_status(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Δεν έχεις δικαιώματα.", ephemeral=True)
        return
    await interaction.response.send_message(f"✉️ Έχουν σταλεί μηνύματα σε {dm2_sent_count} μέλη μέχρι τώρα.", ephemeral=True)

@tree.command(name="recall_left_members_status", description="📊 LIVE πόσα DMs στέλνονται με το /recall_left_members (Zeno only)")
async def recall_left_members_status(interaction: discord.Interaction):
    """Δείχνει LIVE πόσα DMs έχουν σταλεί με το /recall_left_members σε members που έφυγαν"""
    # Permission check: Zeno role or Owner
    ZENO_ROLE_ID = 1162022515846172723
    is_owner = interaction.user.id == OWNER_ID
    has_zeno_role = any(role.id == ZENO_ROLE_ID for role in interaction.user.roles) if hasattr(interaction.user, 'roles') else False
    
    if not (is_owner or has_zeno_role):
        await interaction.response.send_message("❌ Μόνο ο owner ή Zeno role μπορούν να χρησιμοποιήσουν αυτό το command!", ephemeral=True)
        return
    
    await interaction.response.send_message(f"📢 Έχουν σταλεί DMs σε **{recall_left_members_sent_count}** μέλη που έφυγαν τις τελευταίες 180 ημέρες μέχρι τώρα.", ephemeral=True)

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

class PlayMenuView(discord.ui.View):
    def __init__(self, guild_id, song_data=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.song_data = song_data or {}

    @discord.ui.button(label='🛑 Stop', style=discord.ButtonStyle.red, custom_id='play_stop')
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client:
            if self.guild_id in music_queues:
                music_queues[self.guild_id].clear()
            voice_client.stop()
            await voice_client.disconnect()
            await interaction.response.send_message("⏹️ Μουσική σταμάτησε!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν είμαι συνδεδεμένος!", ephemeral=True)

    @discord.ui.button(label='▶️ Start/Pause', style=discord.ButtonStyle.green, custom_id='play_toggle')
    async def toggle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ Σε παύση!", ephemeral=True)
        elif voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ Συνεχίζει!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)

    @discord.ui.button(label='🔊 Φωνή', style=discord.ButtonStyle.blurple, custom_id='play_volume')
    async def volume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💬 Χρησιμοποίησε `/volume 50` για να ρυθμίσεις την ένταση!", ephemeral=True)

    @discord.ui.button(label='📋 Info', style=discord.ButtonStyle.gray, custom_id='play_info')
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.guild_id in music_queues:
            queue = music_queues[self.guild_id]
            if queue.current:
                embed = discord.Embed(
                    title="ℹ️ Now Playing Info",
                    description=f"**{queue.current.get('title', 'Unknown')}**",
                    color=discord.Color.blue()
                )
                if queue.current.get('thumbnail'):
                    embed.set_thumbnail(url=queue.current['thumbnail'])
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Δεν υπάρχει τραγούδι!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν υπάρχει ουρά!", ephemeral=True)

class MusicControlView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label='⏸️ Pause', style=discord.ButtonStyle.blurple, custom_id='pause')
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            button.label = '▶️ Resume'
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("⏸️ Μουσική σε παύση!", ephemeral=True)
        elif voice_client and voice_client.is_paused():
            voice_client.resume()
            button.label = '⏸️ Pause'
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("▶️ Μουσική συνεχίζει!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)

    @discord.ui.button(label='⏭️ Skip', style=discord.ButtonStyle.green, custom_id='skip')
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏭️ Επόμενο τραγούδι!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)

    @discord.ui.button(label='⏹️ Stop', style=discord.ButtonStyle.red, custom_id='stop')
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client:
            if self.guild_id in music_queues:
                music_queues[self.guild_id].clear()
            voice_client.stop()
            await voice_client.disconnect()
            await interaction.response.send_message("⏹️ Μουσική σταμάτησε και αποσυνδέθηκα!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν είμαι συνδεδεμένος!", ephemeral=True)

    @discord.ui.button(label='🔀 Shuffle', style=discord.ButtonStyle.gray, custom_id='shuffle')
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.guild_id in music_queues:
            queue = music_queues[self.guild_id]
            if not queue.is_empty():
                queue.shuffle()
                await interaction.response.send_message(f"🔀 Ανακάτεψα {queue.size()} τραγούδια!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Η ουρά είναι άδεια!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν υπάρχει ουρά!", ephemeral=True)

    @discord.ui.button(label='📜 Queue', style=discord.ButtonStyle.gray, custom_id='queue')
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.guild_id in music_queues:
            queue = music_queues[self.guild_id]
            if queue.current or not queue.is_empty():
                embed = discord.Embed(
                    title="🎵 Music Queue",
                    color=discord.Color.blue()
                )
                
                if queue.current:
                    embed.add_field(
                        name="🎶 Now Playing",
                        value=f"**{queue.current.get('title', 'Unknown')}**",
                        inline=False
                    )
                
                if not queue.is_empty():
                    queue_list = []
                    for i, song in enumerate(list(queue.queue)[:10], 1):
                        queue_list.append(f"{i}. {song.get('title', 'Unknown')}")
                    
                    embed.add_field(
                        name=f"📋 Up Next ({queue.size()} songs)",
                        value="\n".join(queue_list),
                        inline=False
                    )
                
                if queue.loop:
                    embed.add_field(name="🔁 Loop", value="Single track", inline=True)
                elif queue.loop_queue:
                    embed.add_field(name="🔁 Loop", value="Queue", inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Η ουρά είναι άδεια!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Δεν υπάρχει ουρά!", ephemeral=True)

async def play_next(guild):
    if guild.id not in music_queues:
        return
    
    queue = music_queues[guild.id]
    voice_client = guild.voice_client
    
    if not voice_client or not voice_client.is_connected():
        return
    
    next_song = queue.next()
    
    if next_song:
        try:
            player = await YTDLSource.from_url(next_song['url'], loop=bot.loop, stream=True)
            voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild), bot.loop) if not e else logger.error(f'Player error: {e}')
            )
            
            logger.info(f"Now playing: {next_song.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error playing next song: {e}")
            await play_next(guild)

@tree.command(name="play", description="🎵 Παίξε μουσική από YouTube")
@app_commands.describe(search="URL ή όνομα τραγουδιού")
async def play(interaction: discord.Interaction, search: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Πρέπει να είσαι σε φωνητικό κανάλι!", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    await interaction.response.defer()

    # Connect if not already connected
    if not voice_client or voice_client.channel != channel:
        try:
            if voice_client:
                await voice_client.disconnect(force=True)
            voice_client = await channel.connect(timeout=30.0, reconnect=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Σφάλμα σύνδεσης: {str(e)[:100]}", ephemeral=True)
            return

    if interaction.guild.id not in music_queues:
        music_queues[interaction.guild.id] = MusicQueue()

    try:
        data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
        
        if 'entries' in data:
            for entry in data['entries'][:10]:
                music_queues[interaction.guild.id].add({
                    'url': entry['webpage_url'],
                    'title': entry.get('title', 'Unknown'),
                    'duration': entry.get('duration', 0),
                    'thumbnail': entry.get('thumbnail')
                })
            
            # Start playing if nothing is playing
            if not voice_client.is_playing() and not voice_client.is_paused():
                await play_next(interaction.guild)
                for i in range(20):
                    await asyncio.sleep(0.1)
                    if voice_client.is_playing():
                        break
            
            # Show now playing menu for first song in playlist
            queue = music_queues[interaction.guild.id]
            if queue.current:
                embed = discord.Embed(
                    title="🎵 Τώρα Παίζει",
                    description=f"▶️ **{queue.current.get('title', 'Unknown')}**\n\n🔗 **Link**\nΆνοιγμα στο YouTube\n\n🎮 **Controls**\nΧρησιμοποιήστε τα buttons παρακάτω!\n\n↓ Απολάύστε τη μουσική!",
                    color=discord.Color.green()
                )
                if queue.current.get('thumbnail'):
                    embed.set_thumbnail(url=queue.current['thumbnail'])
                view = PlayMenuView(interaction.guild.id, queue.current)
                await interaction.followup.send(embed=embed, view=view)
        else:
            song_data = {
                'url': data['webpage_url'],
                'title': data.get('title', 'Unknown'),
                'duration': data.get('duration', 0),
                'thumbnail': data.get('thumbnail')
            }
            
            music_queues[interaction.guild.id].add(song_data)
            
            # Start playing if nothing is playing
            if not voice_client.is_playing() and not voice_client.is_paused():
                await play_next(interaction.guild)
                for i in range(20):
                    await asyncio.sleep(0.1)
                    if voice_client.is_playing():
                        break
            
            # Show now playing menu
            queue = music_queues[interaction.guild.id]
            if queue.current:
                embed = discord.Embed(
                    title="🎵 Τώρα Παίζει",
                    description=f"▶️ **{queue.current.get('title', 'Unknown')}**\n\n🔗 **Link**\nΆνοιγμα στο YouTube\n\n🎮 **Controls**\nΧρησιμοποιήστε τα buttons παρακάτω!\n\n↓ Απολάύστε τη μουσική!",
                    color=discord.Color.green()
                )
                
                if queue.current.get('thumbnail'):
                    embed.set_thumbnail(url=queue.current['thumbnail'])
                
                view = PlayMenuView(interaction.guild.id, queue.current)
                await interaction.followup.send(embed=embed, view=view)
        
    except Exception as e:
        logger.error(f"Music play error: {e}")
        await interaction.followup.send(f"❌ Σφάλμα: {str(e)}", ephemeral=True)

@tree.command(name="now_playing", description="🎵 Δες τη μουσική που παίζει τώρα με controls")
async def now_playing(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    
    if not voice_client or not voice_client.is_playing():
        await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)
        return
    
    if interaction.guild.id not in music_queues:
        await interaction.response.send_message("❌ Δεν υπάρχει ουρά!", ephemeral=True)
        return
    
    queue = music_queues[interaction.guild.id]
    if not queue.current:
        await interaction.response.send_message("❌ Δεν υπάρχει τραγούδι!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎵 Τώρα Παίζει",
        description=f"▶️ **{queue.current.get('title', 'Unknown')}**\n\n🔗 **Link**\nΆνοιγμα στο YouTube\n\n🎮 **Controls**\nΧρησιμοποιήστε τα buttons παρακάτω!\n\n↓ Απολάύστε τη μουσική!",
        color=discord.Color.green()
    )
    
    if queue.current.get('thumbnail'):
        embed.set_thumbnail(url=queue.current['thumbnail'])
    
    view = PlayMenuView(interaction.guild.id, queue.current)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="loop", description="🔁 Loop το τρέχον τραγούδι ή την ουρά")
@app_commands.describe(mode="single = ένα τραγούδι, queue = όλη η ουρά, off = κανένα")
async def loop(interaction: discord.Interaction, mode: str):
    if interaction.guild.id not in music_queues:
        await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)
        return
    
    queue = music_queues[interaction.guild.id]
    
    if mode.lower() == 'single':
        queue.loop = True
        queue.loop_queue = False
        await interaction.response.send_message("🔁 Loop: Ένα τραγούδι", ephemeral=True)
    elif mode.lower() == 'queue':
        queue.loop = False
        queue.loop_queue = True
        await interaction.response.send_message("🔁 Loop: Όλη η ουρά", ephemeral=True)
    elif mode.lower() == 'off':
        queue.loop = False
        queue.loop_queue = False
        await interaction.response.send_message("🔁 Loop: Off", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Άγνωστο mode! Χρησιμοποίησε: single, queue, ή off", ephemeral=True)

@tree.command(name="queue", description="📋 Δες την ουρά μουσικής")
async def queue_command(interaction: discord.Interaction):
    if interaction.guild.id not in music_queues:
        await interaction.response.send_message("❌ Δεν υπάρχει ουρά!", ephemeral=True)
        return
    
    queue = music_queues[interaction.guild.id]
    
    if not queue.current and queue.is_empty():
        await interaction.response.send_message("❌ Η ουρά είναι άδεια!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎵 Music Queue",
        color=discord.Color.blue()
    )
    
    if queue.current:
        embed.add_field(
            name="🎶 Now Playing",
            value=f"**{queue.current.get('title', 'Unknown')}**",
            inline=False
        )
    
    if not queue.is_empty():
        queue_list = []
        for i, song in enumerate(list(queue.queue)[:10], 1):
            queue_list.append(f"{i}. {song.get('title', 'Unknown')}")
        
        embed.add_field(
            name=f"📋 Up Next ({queue.size()} songs)",
            value="\n".join(queue_list),
            inline=False
        )
    
    if queue.loop:
        embed.add_field(name="🔁 Loop", value="Single track", inline=True)
    elif queue.loop_queue:
        embed.add_field(name="🔁 Loop", value="Queue", inline=True)
    
    view = MusicControlView(interaction.guild.id)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="skip", description="⏭️ Πήγαινε στο επόμενο τραγούδι")
async def skip(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    
    if not voice_client or not voice_client.is_playing():
        await interaction.response.send_message("❌ Δεν παίζει μουσική!", ephemeral=True)
        return
    
    voice_client.stop()
    await interaction.response.send_message("⏭️ Επόμενο τραγούδι!", ephemeral=True)

@tree.command(name="volume", description="🔊 Άλλαξε την ένταση (0-100)")
@app_commands.describe(volume="Ένταση από 0 έως 100")
async def volume(interaction: discord.Interaction, volume: int):
    if not interaction.guild.voice_client:
        await interaction.response.send_message("❌ Δεν είμαι συνδεδεμένος!", ephemeral=True)
        return
    
    if not 0 <= volume <= 100:
        await interaction.response.send_message("❌ Η ένταση πρέπει να είναι 0-100!", ephemeral=True)
        return
    
    voice_client = interaction.guild.voice_client
    if voice_client.source and hasattr(voice_client.source, 'volume'):
        voice_client.source.volume = volume / 100.0
        await interaction.response.send_message(f"🔊 Ένταση: {volume}%", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Δεν μπορώ να ρυθμίσω την ένταση!", ephemeral=True)

@tree.command(name="disconnect", description="👋 Αποσύνδεση από το voice channel")
async def disconnect(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        if interaction.guild.id in music_queues:
            music_queues[interaction.guild.id].clear()
        await voice_client.disconnect()
        await interaction.response.send_message("👋 Αποσυνδέθηκα!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Δεν είμαι συνδεδεμένος!", ephemeral=True)

@tree.command(name="move_all", description="Μετακίνησε όλα τα μέλη στο voice channel σου")
async def move_all(interaction: discord.Interaction):
    if not is_staff_or_owner(interaction.user):
        await interaction.response.send_message("❌ Μόνο ο owner και οι head admins!", ephemeral=True)
        return
    
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Πρέπει να είσαι σε voice channel!", ephemeral=True)
        return
    
    target_channel = interaction.user.voice.channel
    moved_count = 0
    failed_moves = []
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        for voice_channel in interaction.guild.voice_channels:
            if voice_channel == target_channel:
                continue
            
            members_to_move = list(voice_channel.members)
            
            for member in members_to_move:
                try:
                    await member.move_to(target_channel)
                    moved_count += 1
                    await asyncio.sleep(0.2)
                except Exception as e:
                    failed_moves.append(member.display_name)
                    logger.warning(f"Failed to move {member.display_name}: {e}")
        
        if moved_count > 0:
            embed = discord.Embed(
                title="🚀 Move All Command",
                description=f"✅ Μετακινήθηκαν **{moved_count}** μέλη στο {target_channel.name}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            if failed_moves:
                embed.add_field(name="⚠️ Αποτυχίες", value=f"{len(failed_moves)} μέλη", inline=True)
            
            embed.set_footer(text=f"By {interaction.user.display_name}")
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("ℹ️ Δεν υπήρχαν μέλη για μετακίνηση.", ephemeral=True)
            
    except Exception as e:
        logger.error(f"Critical error in move_all: {e}")
        await interaction.followup.send(f"❌ Σφάλμα: {str(e)}", ephemeral=True)

@tree.command(name="movie_night", description="🎬 Έναρξη movie night - ο bot μπαίνει στο voice channel")
async def movie_night(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Πρέπει να είσαι σε ένα voice channel!", ephemeral=True)
        return
    
    target_channel = interaction.user.voice.channel
    
    try:
        # Αν ο bot είναι ήδη συνδεδεμένος, αποσυνδέεται πρώτα
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await asyncio.sleep(1)
        
        # Ο bot μπαίνει στο voice channel
        await target_channel.connect()
        
        embed = discord.Embed(
            title="🎬 Movie Night Ενεργοποιήθηκε!",
            description=f"Το bot είναι τώρα στο **{target_channel.name}**\n\n👥 Όταν κάποιος κάνει screen share, θα ειδοποιηθείτε!",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📺 Τι κάνω", value="Παρακολουθώ τις screen shares και ενημερώνω όλους!", inline=False)
        embed.add_field(name="🎥 Screen Share Tips", value="Κάντε κλικ στο εικονίδιο βιντεοκάμερας για να μοιραστείτε την ταινία!", inline=False)
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Bot joined voice channel {target_channel.name} for movie night")
        
    except Exception as e:
        logger.error(f"Error in movie_night: {e}")
        await interaction.response.send_message(f"❌ Σφάλμα: {str(e)}", ephemeral=True)

# Track screen shares
screen_sharing_users = {}

@bot.event
async def on_presence_update(before, after):
    """Detects when someone starts/stops screen sharing"""
    try:
        # Check if activities changed
        if before.activities != after.activities:
            guild = after.guild
            
            for activity in after.activities:
                # Screen sharing detection
                if isinstance(activity, discord.Streaming) and activity.type == discord.ActivityType.streaming:
                    if after.id not in screen_sharing_users.get(guild.id, []):
                        # Someone started streaming/screen sharing
                        embed = discord.Embed(
                            title="🎥 Screen Share Ενεργοποιήθηκε!",
                            description=f"**{after.display_name}** κάνει screen share!\n\n👀 Όλοι μπορούν να δουν την ταινία/περιεχόμενο!",
                            color=discord.Color.red(),
                            timestamp=datetime.utcnow()
                        )
                        embed.set_thumbnail(url=after.display_avatar.url)
                        
                        # Find voice channel where guild members are
                        for vc in guild.voice_channels:
                            if after in vc.members and vc.members:
                                # Send notification to the channel text
                                try:
                                    # Try to find a text channel to announce
                                    general = discord.utils.get(guild.text_channels, name="general") or guild.text_channels[0]
                                    if general:
                                        await general.send(embed=embed)
                                except:
                                    pass
                        
                        # Track this user
                        if guild.id not in screen_sharing_users:
                            screen_sharing_users[guild.id] = []
                        screen_sharing_users[guild.id].append(after.id)
                        break
            
            # Check for stopped streaming
            for activity in before.activities:
                if isinstance(activity, discord.Streaming):
                    if after.id in screen_sharing_users.get(guild.id, []):
                        # Someone stopped streaming
                        embed = discord.Embed(
                            title="⏹️ Screen Share Σταμάτησε",
                            description=f"**{after.display_name}** σταμάτησε το screen share.",
                            color=discord.Color.gray(),
                            timestamp=datetime.utcnow()
                        )
                        screen_sharing_users[guild.id].remove(after.id)
                        
                        try:
                            general = discord.utils.get(guild.text_channels, name="general") or guild.text_channels[0]
                            if general:
                                await general.send(embed=embed)
                        except:
                            pass
                        break
    
    except Exception as e:
        logger.error(f"Error in presence update: {e}")

class PartnershipModal(discord.ui.Modal, title="📧 Partnership Submission"):
    server_link = discord.ui.TextInput(label="Server Link", placeholder="discord.gg/...", min_length=5, max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        link = str(self.server_link).strip()
        
        # Clean up the link if needed
        if link.startswith("https://"):
            link = link.replace("https://", "")
        if link.startswith("http://"):
            link = link.replace("http://", "")
        
        if "discord.gg/" not in link and "discord.com/invite/" not in link:
            await interaction.response.send_message("❌ Λάθος link! Χρησιμοποίησε ένα Discord server link.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            invite = await bot.fetch_invite(link, with_expiration=True)
            guild = invite.guild
            
            # Use invite's approximate_member_count as primary source
            member_count = invite.approximate_member_count
            if member_count is None or member_count == 0:
                member_count = guild.approximate_member_count or 0
            
            logger.info(f"Partnership request: {guild.name} with {member_count} members (from {interaction.user})")
            
            if member_count >= 450:
                partnership_channel = bot.get_channel(1250102945589100554)
                
                if partnership_channel:
                    # Format the link properly
                    formatted_link = link
                    if "discord.gg/" in link:
                        formatted_link = "https://" + link
                    elif "discord.com/invite/" in link:
                        formatted_link = "https://" + link
                    
                    embed = discord.Embed(
                        title="🔍 Νέα Partnership Αίτηση - Περιμένει Έγκριση",
                        description=f"**Server:** {guild.name}\n**Link:** [{formatted_link}]({formatted_link})",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="👥 Μέλη", value=f"{member_count}+", inline=True)
                    embed.add_field(name="👤 Αιτητής", value=f"{interaction.user.mention}", inline=True)
                    embed.add_field(name="🔗 Link", value=f"`{formatted_link}`", inline=False)
                    
                    if guild.icon:
                        embed.set_thumbnail(url=guild.icon.url)
                    
                    embed.set_footer(text=f"ID: {guild.id}")
                    
                    # Create the approval view
                    approval_view = PartnershipApprovalView(guild.name, formatted_link, member_count, interaction.user.id)
                    
                    await partnership_channel.send(embed=embed, view=approval_view)
                    await interaction.followup.send("✅ Η αίτησή σου έχει αποσταλθεί! Περίμενε την έγκριση! 🎉", ephemeral=True)
                else:
                    await interaction.followup.send("⚠️ Το partnership channel δεν βρέθηκε. Προσπάθησε αργότερα.", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Ο server σου έχει **{member_count}** μέλη. Χρειάζεται τουλάχιστον **450**! 📌", ephemeral=True)
        
        except discord.NotFound:
            await interaction.followup.send("❌ Το link δεν ισχύει ή ο server διαγράφηκε!", ephemeral=True)
        except discord.HTTPException as e:
            logger.error(f"Partnership HTTP error: {e}")
            await interaction.followup.send(f"❌ Σφάλμα σύνδεσης: Δοκίμασε ξανά σε λίγα λεπτά.", ephemeral=True)
        except Exception as e:
            logger.error(f"Partnership error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Σφάλμα: Δοκίμασε ξανά με ένα έγκυρο link.", ephemeral=True)

class PartnershipApprovalView(discord.ui.View):
    def __init__(self, guild_name, link, member_count, requester_id):
        super().__init__(timeout=None)
        self.guild_name = guild_name
        self.link = link
        self.member_count = member_count
        self.requester_id = requester_id
    
    @discord.ui.button(label="✅ Accept Partnership", style=discord.ButtonStyle.green, custom_id="partnership_accept")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID and not any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message("❌ Μόνο ο owner ή staff μπορούν να εγκρίνουν!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Create approval embed
        approval_embed = discord.Embed(
            title="🎉 Partnership Εγκρίθηκε!",
            description=f"**{self.guild_name}**",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        approval_embed.add_field(name="👥 Μέλη", value=f"{self.member_count}+", inline=True)
        approval_embed.add_field(name="🔗 Link", value=f"[Μπείτε εδώ!]({self.link})", inline=True)
        approval_embed.add_field(name="📩 Link", value=f"`{self.link}`", inline=False)
        approval_embed.set_footer(text="Καλώς ήρθατε στην κοινότητα!")
        
        # Send to partnership channel
        partnership_channel = bot.get_channel(1250102945589100554)
        if partnership_channel:
            await partnership_channel.send(embed=approval_embed)
        
        # Edit the original message
        approved_embed = discord.Embed(
            title="✅ Partnership Εγκρίθηκε",
            description=f"**{self.guild_name}** εγκρίθηκε ως partner!\n\n🔗 **Link:** {self.link}",
            color=discord.Color.green()
        )
        
        await interaction.message.edit(embed=approved_embed, view=None)
        await interaction.followup.send(f"✅ Το partnership για **{self.guild_name}** εγκρίθηκε!", ephemeral=True)
    
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, custom_id="partnership_reject")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID and not any(role.id in STAFF_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message("❌ Μόνο ο owner ή staff μπορούν να απορρίψουν!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        rejected_embed = discord.Embed(
            title="❌ Partnership Απορρίφθηκε",
            description=f"**{self.guild_name}** απορρίφθηκε.",
            color=discord.Color.red()
        )
        
        await interaction.message.edit(embed=rejected_embed, view=None)
        await interaction.followup.send(f"❌ Το partnership για **{self.guild_name}** απορρίφθηκε!", ephemeral=True)

class PartnershipView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📤 Submit Server", style=discord.ButtonStyle.green, custom_id="partnership_submit")
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PartnershipModal())


@tree.command(name="partnership", description="🤝 Υποβολή Partnership Αίτησης")
async def partnership(interaction: discord.Interaction):
    # Check if user has the required role (1162022515846172723)
    required_role_id = 1162022515846172723
    has_role = any(role.id == required_role_id for role in interaction.user.roles)
    
    if not has_role and interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Χρειάζεσαι συγκεκριμένο role για να χρησιμοποιήσεις αυτό το command!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🤝 Partnership Program",
        description="Ενδιαφέρεσαι για partnership; Κάνε submit τον server σου!\n\n📌 **Απαιτήσεις:**\n• Τουλάχιστον 450 μέλη\n• Active community",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Συνολικά: ∞ | Status: Open")
    
    view = PartnershipView()
    await interaction.response.send_message(embed=embed, view=view)
    await interaction.followup.send("✅ Partnership menu δημιουργήθηκε!", ephemeral=True)

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Καθυστέρηση: {latency}ms",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(
        title="🤖 Bot Information",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📊 Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Users", value=len(bot.users), inline=True)
    embed.add_field(name="⚡ Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🎵 Music System", value="Ultra Premium Audio", inline=True)
    embed.add_field(name="🏠 Hosting", value="Replit 24/7", inline=True)
    if bot.user:
        embed.add_field(name="📅 Created", value=bot.user.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text="Powered by Replit | Ultra Premium Music")
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    """Monitor messages for NSFW images and track anime character points"""
    if message.author.bot:
        await bot.process_commands(message)
        return
    
    # Track message count for anime character power
    guild = message.guild
    if guild:
        if guild.id not in user_message_counts:
            user_message_counts[guild.id] = {}
        
        if message.author.id not in user_message_counts[guild.id]:
            user_message_counts[guild.id][message.author.id] = 0
        
        user_message_counts[guild.id][message.author.id] += 1
        
        # Update character points
        if guild.id in anime_characters and message.author.id in anime_characters[guild.id]:
            anime_characters[guild.id][message.author.id]['points'] = user_message_counts[guild.id][message.author.id]
            anime_characters[guild.id][message.author.id]['message_count'] = user_message_counts[guild.id][message.author.id]
            save_anime_data()  # Save after each message
    
    try:
        pass  # Message tracking removed
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
    
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
    
    if guild.system_channel:
        embed = discord.Embed(
            title="👋 Γεία σας!",
            description="Ευχαριστώ που με προσθέσατε!\n🎵 Ultra Premium Music Player\n🛡️ Advanced Security System",
            color=discord.Color.green()
        )
        try:
            await guild.system_channel.send(embed=embed)
        except:
            logger.warning(f"Could not send welcome message to {guild.name}")

# Helper function to count all historical messages from a user
async def count_user_messages(guild, user) -> int:
    """Count all messages from user in all channels of the guild (max 10k per channel to avoid rate limit)"""
    total_count = 0
    
    try:
        # Iterate through all channels in the guild
        for channel in guild.text_channels:
            try:
                # Skip channels bot can't read
                if not channel.permissions_for(guild.me).read_message_history:
                    continue
                
                # Count messages from this user (limit to 10k per channel to avoid rate limiting)
                async for message in channel.history(limit=10000):
                    if message.author.id == user.id:
                        total_count += 1
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout counting messages in {channel.name}")
                continue
            except Exception as e:
                logger.warning(f"Error counting messages in {channel.name}: {e}")
                continue
    except Exception as e:
        logger.warning(f"Error in count_user_messages: {e}")
    
    return total_count

# Anime Character System Views
class AnimeCharacterView(discord.ui.View):
    def __init__(self, user_id, char_options):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.char_options = char_options
        
        # Χρώματα για κάθε επιλογή
        colors = [discord.ButtonStyle.success, discord.ButtonStyle.primary, discord.ButtonStyle.secondary]
        
        for i, char_id in enumerate(char_options, 1):
            char = ANIME_CHARACTERS[char_id]
            button = discord.ui.Button(
                label=f"{i}. {char['name']}",
                custom_id=f"anime_select_{char_id}",
                style=colors[i-1] if i <= len(colors) else discord.ButtonStyle.primary
            )
            button.callback = self.select_character
            self.add_item(button)
    
    async def select_character(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Αυτό δεν είναι για σένα!", ephemeral=True)
            return
        
        try:
            char_id = int(interaction.data['custom_id'].replace('anime_select_', ''))
            char = ANIME_CHARACTERS[char_id]
            guild = interaction.guild
            user = interaction.user
            
            # Αποθήκευση character - ΓΡΗΓΟΡΟ, χωρίς διάβασμα μηνυμάτων!
            if guild.id not in anime_characters:
                anime_characters[guild.id] = {}
            
            # Ξεκίνα με 0 points - μόνο τα νέα μηνύματα από εδώ και πέρα μετράνε!
            anime_characters[guild.id][user.id] = {
                'char_id': char_id,
                'points': 0,
                'message_count': 0,
                'last_raid_time': 0,
                'raid_cooldowns': {}
            }
            
            # Ξέχνα τα παλιά μηνύματα - reset στο 0 για αυτόν τον user
            if guild.id in user_message_counts:
                user_message_counts[guild.id][user.id] = 0
            else:
                user_message_counts[guild.id] = {user.id: 0}
            
            save_anime_data()
            
            # Αμέσως απάντηση - ΧΩΡΙΣ ΑΡΓΟ!
            embed = discord.Embed(
                title=f"🎌 Επέλεξες: {char['name']}!",
                description=f"**Series:** {char['series']}\n**Points:** {message_count} ⭐",
                color=discord.Color.purple()
            )
            embed.set_image(url=char['image'])
            embed.set_footer(text=f"Ξεκίνησες με {message_count} points! Νέα = +1 Power")
            
            await interaction.response.edit_message(embed=embed, view=None)
        
        except Exception as e:
            logger.error(f"Error selecting anime character: {e}")
            try:
                error_embed = discord.Embed(
                    title="❌ Σφάλμα",
                    description=f"Κάτι πήγε στραβά: {str(e)}",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=error_embed, view=None)
            except:
                pass

class RaidView(discord.ui.View):
    def __init__(self, attacker_id, defenders):
        super().__init__(timeout=300)
        self.attacker_id = attacker_id
        self.defenders = defenders
        
        for defender_id in defenders[:5]:  # Max 5 buttons
            user = None
            for guild_id in anime_characters:
                if defender_id in anime_characters[guild_id]:
                    user = discord.utils.get(bot.get_all_members(), id=defender_id)
                    break
            
            if user:
                button = discord.ui.Button(
                    label=f"⚔️ Raid {user.name[:15]}",
                    custom_id=f"raid_attack_{defender_id}",
                    style=discord.ButtonStyle.red
                )
                button.callback = self.raid_attack
                self.add_item(button)
    
    async def raid_attack(self, interaction: discord.Interaction):
        if interaction.user.id != self.attacker_id:
            await interaction.response.send_message("❌ Αυτό δεν είναι για σένα!", ephemeral=True)
            return
        
        # Reload latest data
        load_anime_data()
        
        defender_id = int(interaction.data['custom_id'].replace('raid_attack_', ''))
        guild = interaction.guild
        
        attacker_data = anime_characters[guild.id][interaction.user.id]
        defender_data = anime_characters[guild.id][defender_id]
        
        # Check per-target cooldown (5 hours = 18000 seconds)
        RAID_COOLDOWN = 18000  # 5 hours
        current_time = datetime.now(timezone.utc).timestamp()
        
        # Initialize raid_cooldowns dict if not exists
        if 'raid_cooldowns' not in attacker_data:
            attacker_data['raid_cooldowns'] = {}
        
        # Check cooldown specifically for this defender
        last_raid_time_on_target = attacker_data['raid_cooldowns'].get(defender_id, 0)
        time_since_raid = current_time - last_raid_time_on_target
        
        if time_since_raid < RAID_COOLDOWN:
            remaining_time = RAID_COOLDOWN - int(time_since_raid)
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            seconds = remaining_time % 60
            
            defender_user_name = guild.get_member(defender_id)
            defender_user_name = defender_user_name.name if defender_user_name else "Unknown"
            
            cooldown_embed = discord.Embed(
                title="⏳ Cooldown Active",
                description=f"Δεν μπορείς να κάνεις raid στον **{defender_user_name}** ακόμα!\n\n⏱️ Περιμένε: **{hours}h {minutes}m {seconds}s**",
                color=discord.Color.orange()
            )
            cooldown_embed.add_field(name="💡 Tip", value="Μπορείς να κάνεις raid σε κάποιον άλλο στο μεταξύ! 🎯", inline=False)
            await interaction.response.edit_message(embed=cooldown_embed, view=None)
            return
        
        # Update last raid time for this specific defender
        attacker_data['raid_cooldowns'][defender_id] = current_time
        
        attacker_power = attacker_data['points']
        defender_power = defender_data['points']
        
        # Get character info
        attacker_char = ANIME_CHARACTERS[attacker_data['char_id']]
        defender_char = ANIME_CHARACTERS[defender_data['char_id']]
        defender_user = guild.get_member(defender_id)
        defender_name = defender_user.name if defender_user else "Unknown"
        
        # Battle result: Όποιος έχει πιο πολλά points νικάει 100%!
        attacker_win = attacker_power > defender_power
        
        if attacker_win:
            # Attacker wins 50% of defender's points
            stolen_points = int(defender_power * 0.5)
            attacker_data['points'] += stolen_points
            defender_data['points'] = max(0, defender_data['points'] - stolen_points)
            
            result_title = f"🎉 **ΝΙΚΗ!** {attacker_char['name']} έκλεψε {stolen_points} points!"
            result_text = f"**Attacker:** {attacker_char['name']} ({attacker_data['points']} ⭐)\n"
            result_text += f"**Defender:** {defender_char['name']} ({defender_data['points']} ⭐)\n\n"
            result_text += f"💰 {stolen_points} points κλάπηκαν!"
            color = discord.Color.green()
        else:
            # Defender wins - steals 50% of attacker's points
            stolen_points = int(attacker_power * 0.5)
            defender_data['points'] += stolen_points
            attacker_data['points'] = max(0, attacker_data['points'] - stolen_points)
            
            result_title = f"❌ **ΗΤΤΑ!** {defender_char['name']} νίκησε και έκλεψε {stolen_points} points!"
            result_text = f"**Attacker:** {attacker_char['name']} ({attacker_data['points']} ⭐)\n"
            result_text += f"**Defender:** {defender_char['name']} ({defender_data['points']} ⭐)\n\n"
            result_text += f"💰 {stolen_points} points κλάπηκαν!"
            color = discord.Color.red()
        
        # Create attacker embed with image
        attacker_embed = discord.Embed(
            title=f"⚔️ {interaction.user.name}",
            description=f"**{attacker_char['name']}**\n{attacker_char['series']}\n\n{result_title}\n\n💰 **Points Stolen:** {stolen_points} ⭐",
            color=discord.Color.blue() if attacker_win else discord.Color.red()
        )
        attacker_embed.add_field(name="💪 Power", value=f"{attacker_power} ⭐", inline=True)
        attacker_embed.add_field(name="💰 Now", value=f"{attacker_data['points']} ⭐", inline=True)
        attacker_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        # Create defender embed with image
        defender_embed = discord.Embed(
            title=f"🛡️ {defender_name}",
            description=f"**{defender_char['name']}**\n{defender_char['series']}",
            color=discord.Color.red() if attacker_win else discord.Color.blue()
        )
        defender_embed.add_field(name="💪 Power", value=f"{defender_power} ⭐", inline=True)
        defender_embed.add_field(name="💰 Now", value=f"{defender_data['points']} ⭐", inline=True)
        defender_embed.set_thumbnail(url=defender_user.display_avatar.url)
        
        save_anime_data()  # Save raid results
        await interaction.response.edit_message(embeds=[attacker_embed, defender_embed], view=None)

@tree.command(name="my_anime_character", description="🎌 Διάλεξε τον anime character σου και γίνε πιο δυνατός!")
async def my_anime_character(interaction: discord.Interaction):
    # Reload data from file to ensure we have latest
    load_anime_data()
    
    guild = interaction.guild
    
    # Check if already has character
    if guild.id in anime_characters and interaction.user.id in anime_characters[guild.id]:
        char_id = anime_characters[guild.id][interaction.user.id]['char_id']
        char = ANIME_CHARACTERS[char_id]
        points = anime_characters[guild.id][interaction.user.id]['points']
        msg_count = anime_characters[guild.id][interaction.user.id]['message_count']
        
        # Calculate power level
        power_level = int(msg_count * 0.1) if msg_count > 0 else 0
        
        embed = discord.Embed(
            title=f"🎌 Ο Character σου: {char['name']}",
            description=f"**Series:** {char['series']}",
            color=discord.Color.gold()
        )
        embed.add_field(name="⭐ Points", value=f"{points:,}", inline=True)
        embed.add_field(name="📝 Messages", value=f"{msg_count:,}", inline=True)
        embed.add_field(name="💪 Power Level", value=f"{power_level}%", inline=True)
        embed.set_image(url=char['image'])
        embed.set_footer(text="💡 Όσο περισσότερα μηνύματα, τόσα περισσότερα points παίρνεις! Μετά μπορείς να κάνεις /raid για να κάνεις μάχες!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Get 3 random characters
    char_ids = get_random_characters()
    view = AnimeCharacterView(interaction.user.id, char_ids)
    
    embed = discord.Embed(
        title="🎌 Διάλεξε τον Anime Character σου!",
        description="Πάτησε ένα κουμπί για να διαλέξεις. Κάθε μήνυμα = +1 Power! 💪",
        color=discord.Color.blurple()
    )
    
    for char_id in char_ids:
        char = ANIME_CHARACTERS[char_id]
        embed.add_field(
            name=f"⭐ {char['name']}",
            value=f"Series: {char['series']}",
            inline=False
        )
    
    embed.set_footer(text="💡 Όσο περισσότερα μηνύματα, τόσα περισσότερα points παίρνεις! Μετά μπορείς να κάνεις /raid για να κάνεις μάχες!")
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@tree.command(name="admin_power", description="🔧 [OWNER] Προσθέσε ή αφαίρεσε power level από κάποιον")
@app_commands.describe(
    user="Ποιον χρήστη;",
    operation="Add (Προσθήκη) ή Remove (Αφαίρεση)",
    amount="Πόσο power level;"
)
@app_commands.choices(operation=[
    app_commands.Choice(name="Add (Προσθήκη)", value="add"),
    app_commands.Choice(name="Remove (Αφαίρεση)", value="remove")
])
async def admin_power(interaction: discord.Interaction, user: discord.User, operation: str, amount: app_commands.Range[int, 1, 99999]):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Μόνο ο owner μπορεί να κάνει αυτό!", ephemeral=True)
        return
    
    load_anime_data()
    guild = interaction.guild
    
    # Check if target user has character
    if guild.id not in anime_characters or user.id not in anime_characters[guild.id]:
        await interaction.response.send_message(f"❌ Ο {user.mention} δεν έχει διαλέξει character ακόμα!", ephemeral=True)
        return
    
    user_data = anime_characters[guild.id][user.id]
    old_points = user_data['points']
    
    if operation == "add":
        user_data['points'] += amount
        embed = discord.Embed(
            title="✅ Power Added",
            description=f"{user.mention} πήρε **+{amount} ⭐ power**",
            color=discord.Color.green()
        )
    else:  # remove
        user_data['points'] = max(0, user_data['points'] - amount)
        embed = discord.Embed(
            title="✅ Power Removed",
            description=f"{user.mention} έχασε **-{amount} ⭐ power**",
            color=discord.Color.red()
        )
    
    embed.add_field(name="Before", value=f"{old_points} ⭐", inline=True)
    embed.add_field(name="After", value=f"{user_data['points']} ⭐", inline=True)
    
    save_anime_data()
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="raid", description="⚔️ Κάνε raid σε άλλον anime character και κλέψε points!")
async def raid(interaction: discord.Interaction):
    # Reload data from file to ensure we have latest
    load_anime_data()
    
    guild = interaction.guild
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has character
    if guild.id not in anime_characters or interaction.user.id not in anime_characters[guild.id]:
        await interaction.followup.send("❌ Πρώτα πρέπει να διαλέξεις έναν anime character με `/my_anime_character`!", ephemeral=True)
        return
    
    # Initialize guild data if needed
    if guild.id not in anime_characters:
        anime_characters[guild.id] = {}
    
    # Update points ONLY for users who ALREADY have characters
    # Χρησιμοποίησε τα μηνύματα που ήδη έχουν μετρηθεί από το on_message - ΑΜΕΣΟ!
    logger.info("🔄 Ενημέρωση points (FAST MODE)...")
    
    if guild.id in user_message_counts:
        for user_id, msg_count in user_message_counts[guild.id].items():
            if user_id == interaction.user.id:
                continue
            
            # Update ONLY if they have a character
            if user_id in anime_characters[guild.id]:
                anime_characters[guild.id][user_id]['points'] = msg_count
                anime_characters[guild.id][user_id]['message_count'] = msg_count
    
    save_anime_data()
    
    # Get all users with characters
    defenders = [uid for uid in anime_characters[guild.id].keys() if uid != interaction.user.id]
    
    if not defenders:
        await interaction.followup.send("❌ Κανένας άλλος δεν έχει διαλέξει character ακόμα!", ephemeral=True)
        return
    
    # Show raid options with beautiful UI
    attacker_data = anime_characters[guild.id][interaction.user.id]
    attacker_char = ANIME_CHARACTERS[attacker_data['char_id']]
    
    # Sort defenders by power for ranking
    defender_list = [(uid, anime_characters[guild.id][uid]['points']) for uid in defenders]
    defender_list.sort(key=lambda x: x[1], reverse=True)
    
    rank_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    embed = discord.Embed(
        title="⚔️ RAID BATTLE ARENA",
        description=f"**Your Character:** {attacker_char['name']} ({attacker_data['points']} ⭐)\n\nΕπέλεξε το target σου:",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    
    embed.set_thumbnail(url="https://via.placeholder.com/200?text=⚔️+RAID")
    
    for rank, (defender_id, power) in enumerate(defender_list[:5]):
        defender_data = anime_characters[guild.id][defender_id]
        defender_char = ANIME_CHARACTERS[defender_data['char_id']]
        user = guild.get_member(defender_id)
        
        rank_icon = rank_icons[rank]
        username = user.mention if user else 'Unknown'
        
        # Power level bar (visual indicator)
        max_power = max([d['points'] for d in anime_characters[guild.id].values()])
        bar_length = int((power / max_power * 10)) if max_power > 0 else 0
        power_bar = "█" * bar_length + "░" * (10 - bar_length)
        
        field_value = (
            f"{rank_icon} **{defender_char['name']}**\n"
            f"👤 Player: {username}\n"
            f"📊 Power: **{power} ⭐**\n"
            f"📈 {power_bar} [{power}/{max_power}]\n"
            f"🎌 Series: *{defender_char['series']}*"
        )
        
        embed.add_field(
            name="▬▬▬▬▬▬▬▬▬",
            value=field_value,
            inline=False
        )
    
    embed.set_footer(text="⏳ Cooldown: 2 minutes between raids | 🔄 Choose wisely!")
    embed.color = discord.Color.from_rgb(180, 0, 0)
    
    view = RaidView(interaction.user.id, defenders)
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@tree.command(name="check_partnerships", description="📊 Μέτρησε πόσα server links υπάρχουν στο partnership channel")
async def check_partnerships(interaction: discord.Interaction):
    # Check if user is owner or has zeno role
    ZENO_ROLE_ID = 1162022515846172723
    is_owner = interaction.user.id == OWNER_ID
    has_zeno_role = any(role.id == ZENO_ROLE_ID for role in interaction.user.roles) if hasattr(interaction.user, 'roles') else False
    
    if not (is_owner or has_zeno_role):
        await interaction.response.send_message("❌ Μόνο ο owner ή κάποιος με το role zeno μπορεί να το χρησιμοποιήσει!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    PARTNERSHIP_CHANNEL_ID = 1250102945589100554
    
    try:
        partnership_channel = await bot.fetch_channel(PARTNERSHIP_CHANNEL_ID)
        
        if not partnership_channel:
            await interaction.followup.send("❌ Δεν βρέθηκε το partnership channel!", ephemeral=True)
            return
        
        import re
        
        # Ψάχνω όλα τα messages για discord.gg links
        all_links = []
        link_sources = {}
        
        async for message in partnership_channel.history(limit=500):
            content = message.content
            
            # Εξάγω όλα τα discord.gg links
            links = re.findall(r'discord\.gg/(\w+)', content)
            
            if links:
                for link in links:
                    all_links.append(link)
                    if link not in link_sources:
                        link_sources[link] = 0
                    link_sources[link] += 1
        
        if not all_links:
            await interaction.followup.send("❌ Δεν βρέθηκαν links στο partnership channel!", ephemeral=True)
            return
        
        # Μοναδικά links
        unique_links = len(set(all_links))
        total_mentions = len(all_links)
        
        # Δημιουργώ embed
        report_embed = discord.Embed(
            title="📊 Partnership Links Report",
            description=f"Στατιστικά των links στο partnership channel",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        
        # Summary
        report_embed.add_field(
            name="📈 Σύνοψη",
            value=f"**Μοναδικά Links:** {unique_links}\n**Συνολικές Αναφορές:** {total_mentions}",
            inline=False
        )
        
        # Top links
        sorted_links = sorted(link_sources.items(), key=lambda x: x[1], reverse=True)
        top_links_text = "\n".join([f"🔗 `discord.gg/{link}` - {count} φορές" for link, count in sorted_links[:15]])
        report_embed.add_field(
            name="🔝 Top Links",
            value=top_links_text,
            inline=False
        )
        
        await interaction.followup.send(embed=report_embed, ephemeral=True)
        logger.info(f"Partnership check: {unique_links} unique links, {total_mentions} total mentions")
        
    except Exception as e:
        logger.error(f"Error checking partnerships: {e}")
        await interaction.followup.send(f"❌ Σφάλμα: {str(e)[:100]}", ephemeral=True)

def run_bot():
    # Use new token (third bot - DISCORD_BOT_TOKEN_NEW)
    token = os.getenv('DISCORD_BOT_TOKEN_NEW')
    
    if not token:
        logger.error("❌ DISCORD_BOT_TOKEN_NEW not found in environment variables!")
        return
    
    try:
        logger.info("Starting Discord bot...")
        logger.info(f"Token format check: length={len(token)}, has dots={token.count('.')}")
        bot.run(token, log_handler=None)
    except discord.LoginFailure as e:
        logger.error(f"❌ Invalid Discord token! Error: {e}")
        logger.error("Πρέπει να κάνεις REGENERATE το token από το Discord Developer Portal")
    except discord.HTTPException as e:
        logger.error(f"❌ HTTP Error: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import time
        time.sleep(30)
        run_bot()

if __name__ == "__main__":
    run_bot()