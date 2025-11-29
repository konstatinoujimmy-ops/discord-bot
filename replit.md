# Overview

This is a 24/7 Discord bot designed to run continuously on Replit using free keep-alive mechanisms. The bot features a Flask web server that acts as a health check endpoint, allowing external monitoring services to ping it and prevent the Replit from going to sleep. The bot includes Greek language support for commands and messages, comprehensive logging, and automatic restart capabilities.

# User Preferences

- Preferred communication style: Simple, everyday language
- **IMPORTANT**: Greek language ONLY - ALWAYS and EXCLUSIVELY. Never switch languages randomly.
- Mobile-friendly step-by-step guidance
- Owner: mitsos_283 (ID: 839148474314129419)

## Recent Changes (November 29, 2025 - LATEST)
- ✅ **Fixed `/recall_left_members` command** - Restructured to find 400+ left members
  - Changed logic: scans ALL audit logs (kicks + bans) without time limit
  - Combines current members + audit log members to create "all_ever_members"
  - Now detects voluntary departures + kicked + banned members correctly
  - Expected to find 400+ members that need recall DMs
  - Uses 9-second delay between DMs to prevent rate limiting

## Previous Changes (November 27, 2025)
- ✅ **Added `/check_partnerships` command** (Owner-only)
  - Monitors partnership channel (ID: 1250102945589100554)
  - Identifies which partnership servers have removed our server link
  - Generates detailed report with active/deleted links
  - Shows which servers removed the link
  
- **Music Feature Status**: FFmpeg cannot process YouTube HLS streams (error 183)
  - yt-dlp extracts URLs that expire too quickly for FFmpeg
  - This is a known discord.py + YouTube limitation on Replit
  - Requires architectural changes (Lavalink service, local caching, or mpv backend)

## Fully Functional Features (November 27, 2025)
- ✅ Bot joins voice channels and stays online 24/7
- ✅ `/raid` - Anime character PvP battles (2-embed compact display)
- ✅ `/admin_power` - Add/remove power points from users
- ✅ `/now_playing` - Display music control menu on demand
- ✅ `/check_partnerships` - Monitor partnership links and detect removed links
- ✅ Moderation: `/dm`, `/dm2`, `/mute`, `/ban`, `/announce`
- ✅ `/permissions` - View user permissions
- ✅ `/my_anime_character` - Select anime character
- ✅ `/security_status` / `/security_report` - Security monitoring
- ✅ `/partnership` - Partnership application system
- ✅ Greek language interface throughout

## Known Limitations
- ❌ Audio playback not functional (FFmpeg + YouTube HLS stream issue)
- ⚠️ Music menu displays but no sound is heard

# System Architecture

## Core Components

**Bot Architecture**: discord.py with command-based system
- `bot.py` - Main Discord bot logic with 25+ commands
- `main.py` - Entry point for bot + keep-alive server
- `keep_alive.py` - Flask web server for health checks
- `auto_ping.py` - 2-minute auto-ping system for uptime

**Keep-Alive System**: 
- Flask server on port 5000
- External auto-ping every 2 minutes
- Double heartbeat: bot heartbeat + auto-ping

**Threading Model**: 
- Flask daemon thread + discord.py main thread
- Concurrent operation of web server and Discord bot

**Music System** (non-functional):
- yt-dlp for YouTube extraction
- FFmpeg for audio processing
- discord.py PCMVolumeTransformer for audio playback
- Issue: YouTube HLS streams cannot be processed

## Design Patterns

**Security**: 
- Role-based access control for commands
- Owner-only commands for sensitive operations
- Real-time role permission monitoring
- Auto-removal of ban permissions from non-owners

**Data Persistence**:
- JSON-based anime character data storage
- Message tracking for power level calculations
- Partnership data tracking

# External Dependencies

## Core Libraries
- **discord.py 2.5.2**: Discord API wrapper
- **Flask 3.1.1**: Web framework for keep-alive
- **yt-dlp 2025.08.11**: YouTube content extraction
- **ffmpeg 7.1.1**: Audio processing (non-functional with HLS)
- **PyNaCl**: Voice support
- **requests**: HTTP requests
- **Python 3.11**: Runtime

## Deployment Platforms
- **Replit**: Development and deployment platform
- **Railway**: Available for production 24/7 deployment
- **Dual Compatibility**: Auto-detection of environment

# Commands Reference (Greek)

| Command | Description | Owner-Only |
|---------|-------------|-----------|
| `/raid` | Anime character PvP battles | No |
| `/admin_power` | Add/remove power from users | Yes |
| `/now_playing` | Show music control menu | No |
| `/check_partnerships` | Monitor partnership links | Yes |
| `/dm` | Send private message | Staff |
| `/dm2` | Mass DM to role members | Yes |
| `/mute` | Mute user | Staff |
| `/ban` | Ban user | Yes |
| `/announce` | Announce in channel | Staff |
| `/permissions` | View user permissions | No |
| `/my_anime_character` | Select anime character | No |
| `/security_status` | View security stats | Staff |
| `/security_report` | Generate security report | Staff |
| `/partnership` | Apply for partnership | Yes |

# Next Steps for Complete Feature

To fix music playback, one of these approaches is needed:
1. **Lavalink Integration**: External audio service for Discord
2. **Local Caching**: Download and cache audio files before playing
3. **Alternative Backend**: Switch to mpv library instead of FFmpeg
4. **URL Proxying**: Implement mechanism to refresh expired YouTube URLs
