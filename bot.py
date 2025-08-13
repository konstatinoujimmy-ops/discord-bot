"""
Discord Bot Implementation
Contains all bot commands and event handlers
"""

import discord
from discord.ext import commands
import os
import logging
import asyncio
from datetime import datetime
import random

# Configure logging
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    logger.info(f'{bot.user} έχει συνδεθεί στο Discord!')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Guilds: {len(bot.guilds)}')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="24/7 on Replit!"
        )
    )

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

# Basic Commands
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
    embed.add_field(name="📅 Created", value=bot.user.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text="Powered by Replit")
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status(ctx):
    """Check bot status"""
    uptime_seconds = (datetime.utcnow() - bot.user.created_at).total_seconds()
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    embed = discord.Embed(
        title="📊 Bot Status",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🟢 Status", value="Online & Running", inline=True)
    embed.add_field(name="⏱️ Session Time", value=f"{hours}h {minutes}m", inline=True)
    embed.add_field(name="🔗 Keep-Alive", value="Active", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='hello')
async def hello(ctx):
    """Simple greeting command"""
    greetings = [
        f"Γεια σου {ctx.author.mention}! 👋",
        f"Καλώς ήρθες {ctx.author.mention}! 🎉",
        f"Χαίρομαι να σε βλέπω {ctx.author.mention}! 😊"
    ]
    await ctx.send(random.choice(greetings))

# Remove the default help command
bot.remove_command('help')

@bot.command(name='help')
async def help_command(ctx, command_name=None):
    """Custom help command"""
    if command_name:
        # Help for specific command
        command = bot.get_command(command_name)
        if command:
            embed = discord.Embed(
                title=f"📖 Βοήθεια για `!{command.name}`",
                description=command.help or "Δεν υπάρχει περιγραφή.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Χρήση", value=f"`!{command.name}`", inline=False)
        else:
            embed = discord.Embed(
                title="❌ Σφάλμα",
                description="Η εντολή δεν βρέθηκε.",
                color=discord.Color.red()
            )
    else:
        # General help
        embed = discord.Embed(
            title="📚 Διαθέσιμες Εντολές",
            description="Ορίστε οι διαθέσιμες εντολές:",
            color=discord.Color.blue()
        )
        
        commands_list = [
            ("!ping", "Έλεγχος καθυστέρησης bot"),
            ("!info", "Πληροφορίες για το bot"),
            ("!status", "Κατάσταση λειτουργίας bot"),
            ("!hello", "Απλός χαιρετισμός"),
            ("!help [εντολή]", "Εμφάνιση αυτού του μηνύματος")
        ]
        
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.set_footer(text="Χρησιμοποιήστε !help [εντολή] για περισσότερες λεπτομέρειες")
    
    await ctx.send(embed=embed)

@bot.command(name='restart')
@commands.is_owner()
async def restart(ctx):
    """Restart command (owner only)"""
    await ctx.send("🔄 Επανεκκίνηση bot...")
    logger.info("Bot restart requested by owner")
    await bot.close()

@bot.event
async def on_guild_join(guild):
    """Event when bot joins a new guild"""
    logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
    
    # Try to send a welcome message
    if guild.system_channel:
        embed = discord.Embed(
            title="👋 Γεια σας!",
            description="Ευχαριστώ που με προσθέσατε στον server σας!\nΧρησιμοποιήστε `!help` για να δείτε τις διαθέσιμες εντολές.",
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
