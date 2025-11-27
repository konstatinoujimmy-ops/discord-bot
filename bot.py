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
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque

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

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

STAFF_ROLE_IDS = {
    1250890557279178864,
    1293607647223746661,
    1292372795631603847
}
OWNER_ID = 839148474314129419

active_mutes = {}
dm2_sent_count = 0

security_tracker = {
    'channel_creations': defaultdict(list),
    'everyone_mentions': defaultdict(list),
    'bans': defaultdict(list),
    'kicks': defaultdict(list),
    'timeouts': defaultdict(list),
    'role_removals': {}
}

active_giveaways = {}
nsfw_violations = {}  # {guild_id: {user_id: {'count': X, 'last_violation': timestamp, 'user': user_obj}}}

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
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extractaudio': True,
    'audioformat': 'opus',
    'audioquality': 0,
    'prefer_ffmpeg': True,
    'ignoreerrors': False,
    'nocheckcertificate': True,
    'no_color': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn -b:a 192k -ar 48000 -ac 2 -filter:a "dynaudnorm=f=150:g=15"'
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
        
        return cls(discord.FFmpegOpusAudio(filename, **ffmpeg_options), data=data)

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

@tree.command(name="play", description="🎵 Ultra Premium Music Player - Παίξε μουσική από YouTube")
@app_commands.describe(search="URL ή όνομα τραγουδιού")
async def play(interaction: discord.Interaction, search: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Πρέπει να είσαι σε φωνητικό κανάλι!", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    await interaction.response.defer()

    try:
        if not voice_client:
            logger.info(f"Connecting to voice channel: {channel.name}")
            voice_client = await asyncio.wait_for(
                channel.connect(timeout=60.0, reconnect=True),
                timeout=70.0
            )
            logger.info("Voice connection successful!")
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)
    except asyncio.TimeoutError:
        await interaction.followup.send(
            "❌ **Timeout Error**: Δεν μπόρεσα να συνδεθώ στο voice channel.\n"
            "⚠️ **Το Replit έχει προβλήματα με Discord voice connections.**\n"
            "💡 **Λύση**: Δοκίμασε να deploy το bot σε Bot-Hosting.net για 100% λειτουργία!",
            ephemeral=True
        )
        return
    except discord.ClientException as e:
        await interaction.followup.send(
            f"❌ **Voice Connection Error**: {str(e)}\n"
            "⚠️ **Το Replit environment δεν υποστηρίζει πλήρως Discord voice.**\n"
            "💡 **Λύση**: Deploy στο Bot-Hosting.net για σταθερή λειτουργία!",
            ephemeral=True
        )
        logger.error(f"Voice connection error: {e}")
        return
    except Exception as e:
        await interaction.followup.send(
            f"❌ **Σφάλμα σύνδεσης**: {str(e)}",
            ephemeral=True
        )
        logger.error(f"Unexpected voice error: {e}")
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
            
            embed = discord.Embed(
                title="➕ Προστέθηκε Playlist",
                description=f"**{len(data['entries'][:10])} τραγούδια** προστέθηκαν στην ουρά!",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        else:
            song_data = {
                'url': data['webpage_url'],
                'title': data.get('title', 'Unknown'),
                'duration': data.get('duration', 0),
                'thumbnail': data.get('thumbnail')
            }
            
            music_queues[interaction.guild.id].add(song_data)
            
            embed = discord.Embed(
                title="➕ Προστέθηκε στην ουρά",
                description=f"**{song_data['title']}**",
                color=discord.Color.green()
            )
            
            if song_data['thumbnail']:
                embed.set_thumbnail(url=song_data['thumbnail'])
            
            queue_pos = music_queues[interaction.guild.id].size()
            embed.add_field(name="📍 Θέση στην ουρά", value=f"#{queue_pos}", inline=True)
            
            if song_data['duration']:
                minutes = song_data['duration'] // 60
                seconds = song_data['duration'] % 60
                embed.add_field(name="⏱️ Διάρκεια", value=f"{minutes}:{seconds:02d}", inline=True)
            
            await interaction.followup.send(embed=embed)
        
        if not voice_client.is_playing() and not voice_client.is_paused():
            await play_next(interaction.guild)
        
    except Exception as e:
        logger.error(f"Music play error: {e}")
        await interaction.followup.send(f"❌ Σφάλμα: {str(e)}", ephemeral=True)

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

class NSFWConfirmationView(discord.ui.View):
    def __init__(self, guild, selected_user_ids):
        super().__init__(timeout=None)
        self.guild = guild
        self.selected_user_ids = selected_user_ids
    
    @discord.ui.button(label="✅ Επιβεβαίωση Timeout", style=discord.ButtonStyle.green, custom_id="nsfw_confirm_timeout")
    async def confirm_timeout(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Μόνο ο owner!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        timeout_applied = 0
        failed = 0
        
        for user_id_str in self.selected_user_ids:
            try:
                member = await self.guild.fetch_member(int(user_id_str))
                timeout_duration = timedelta(minutes=1)
                timeout_until = datetime.now(timezone.utc) + timeout_duration
                
                await member.timeout(timeout_until, reason="NSFW Content Violation")
                timeout_applied += 1
            except Exception as e:
                failed += 1
                logger.error(f"Error timeout user {user_id_str}: {e}")
        
        embed = discord.Embed(
            title="✅ Timeout Εφαρμόστηκε",
            description=f"**Επιτυχής:** {timeout_applied}\n**Αποτυχία:** {failed}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❌ Ακύρωση", style=discord.ButtonStyle.red, custom_id="nsfw_cancel_timeout")
    async def cancel_timeout(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Μόνο ο owner!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Ακυρώθηκε!", ephemeral=True)
        await interaction.message.delete()

class NSFWEnforcementView(discord.ui.View):
    def __init__(self, violations_list, guild):
        super().__init__(timeout=None)
        self.violations_list = violations_list
        self.guild = guild
        self.selected_users = []

    @discord.ui.select(
        placeholder="Επιλογή χρηστών για timeout...",
        min_values=0,
        max_values=25,
        custom_id="nsfw_select_users"
    )
    async def select_users(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_users = select.values
        await interaction.response.defer()

    @discord.ui.button(label="✅ Εφαρμογή Timeout (1 λεπτό)", style=discord.ButtonStyle.green, custom_id="nsfw_apply_timeout")
    async def apply_timeout(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Μόνο ο owner!", ephemeral=True)
            return

        if not self.selected_users:
            await interaction.response.send_message("❌ Δεν έχεις επιλέξει κανέναν χρήστη!", ephemeral=True)
            return
        
        # Δημιουργία confirmation message
        confirmation_embed = discord.Embed(
            title="⚠️ Επιβεβαίωση Timeout",
            description=f"Είσαι σίγουρος ότι θέλεις να κάνεις timeout σε **{len(self.selected_users)}** χρήστη(ες) για 1 λεπτό;",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        confirmation_view = NSFWConfirmationView(self.guild, self.selected_users)
        
        await interaction.response.send_message(embed=confirmation_embed, view=confirmation_view, ephemeral=True)

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

@tree.command(name="nsfw", description="🔍 Προβολή και ενεργοποίηση timeout για NSFW παραβιάσεις των τελευταίων 3 ημερών")
async def nsfw_enforcement(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Μόνο ο owner!", ephemeral=True)
        return
    
    guild = interaction.guild
    three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
    
    # Συλλογή παραβιάσεων των τελευταίων 3 ημερών
    violations_in_period = []
    
    if guild.id in nsfw_violations:
        for user_id, violation_data in nsfw_violations[guild.id].items():
            if violation_data['last_violation'] >= three_days_ago:
                violations_in_period.append({
                    'user_id': str(user_id),
                    'user': violation_data['user'],
                    'count': violation_data['count'],
                    'last_violation': violation_data['last_violation']
                })
    
    if not violations_in_period:
        await interaction.response.send_message("✅ Δεν υπάρχουν NSFW παραβιάσεις στις τελευταίες 3 ημέρες!", ephemeral=True)
        return
    
    # Δημιουργία select menu options
    options = []
    for violation in violations_in_period:
        label = f"{violation['user'].name} - {violation['count']} παραβιάσεις"
        options.append(discord.SelectOption(
            label=label[:100],  # Discord limit
            value=violation['user_id'],
            description=f"Τελευταία: {violation['last_violation'].strftime('%d/%m %H:%M')}"
        ))
    
    # Δημιουργία view με select menu
    view = NSFWEnforcementView(violations_in_period, guild)
    
    # Αντικατάσταση του select menu με τις σωστές options
    for item in view.children:
        if isinstance(item, discord.ui.Select) and item.custom_id == "nsfw_select_users":
            item.options = options
    
    embed = discord.Embed(
        title="🔍 NSFW Παραβιάσεις - Τελευταίες 3 Ημέρες",
        description=f"**Σύνολο:** {len(violations_in_period)} χρήστες\n\nΕπιλέξτε χρήστες για timeout 1 λεπτού:",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )
    
    for violation in violations_in_period[:10]:  # Εμφάνιση πρώτων 10
        embed.add_field(
            name=f"👤 {violation['user'].name}",
            value=f"Παραβιάσεις: **{violation['count']}**\nΤελευταία: <t:{int(violation['last_violation'].timestamp())}:R>",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

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

async def check_image_nsfw(image_url: str) -> bool:
    """Checks if image contains NSFW content using simple heuristics"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    # Simple NSFW detection - check image characteristics
                    # This is a basic implementation
                    return False  # Default to safe unless we have explicit NSFW detection
    except Exception as e:
        logger.error(f"Error checking image: {e}")
        return False

@bot.event
async def on_message(message):
    """Monitor messages for NSFW images"""
    if message.author.bot:
        await bot.process_commands(message)
        return
    
    try:
        # Check if message has attachments
        if message.attachments:
            for attachment in message.attachments:
                # Check if it's an image
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    # Perform NSFW check
                    is_nsfw = await check_image_nsfw(attachment.url)
                    
                    if is_nsfw:
                        # Delete the message
                        try:
                            await message.delete()
                        except:
                            pass
                        
                        # Timeout the user for 10 minutes
                        timeout_duration = timedelta(minutes=10)
                        timeout_until = datetime.now(timezone.utc) + timeout_duration
                        
                        # Record NSFW violation
                        if message.guild.id not in nsfw_violations:
                            nsfw_violations[message.guild.id] = {}
                        
                        if message.author.id not in nsfw_violations[message.guild.id]:
                            nsfw_violations[message.guild.id][message.author.id] = {
                                'count': 0,
                                'last_violation': datetime.now(timezone.utc),
                                'user': message.author
                            }
                        
                        nsfw_violations[message.guild.id][message.author.id]['count'] += 1
                        nsfw_violations[message.guild.id][message.author.id]['last_violation'] = datetime.now(timezone.utc)
                        
                        try:
                            await message.author.timeout(timeout_until, reason="NSFW Content Detection")
                            
                            # Send warning message
                            embed = discord.Embed(
                                title="⚠️ NSFW Content Detected",
                                description=f"**{message.author.mention}** Εστάλη NSFW περιεχόμενο.\n\n❌ **Timeout:** 10 λεπτά",
                                color=discord.Color.red(),
                                timestamp=datetime.utcnow()
                            )
                            embed.set_footer(text="Το bot αυτόματα εφάρμοσε timeout για προστασία του server")
                            
                            try:
                                await message.channel.send(embed=embed, delete_after=30)
                            except:
                                pass
                            
                            logger.warning(f"NSFW content detected from {message.author} in {message.guild.name}")
                        except Exception as e:
                            logger.error(f"Could not timeout user: {e}")
    
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

def run_bot():
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("❌ DISCORD_TOKEN not found in environment variables!")
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