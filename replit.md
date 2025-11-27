# Overview

This is a 24/7 Discord bot designed to run continuously on Replit with feature-rich gaming and moderation systems. The bot includes music playback (YouTube via yt-dlp), voice channel management, advanced security monitoring, moderation tools, partnership management system, anime character gamification, and comprehensive slash commands. **NSFW detection system removed.** All communication is in Greek language exclusively. Bot stays online 24/7 using Flask keep-alive + auto-ping mechanism.

# User Preferences

Preferred communication style: Simple, everyday language - Greek only, no Portuguese or English.
Device: Mobile only - requires simple step-by-step guidance with visual confirmations.

## Recent Changes (November 27, 2025 - Latest Session)

### Latest Updates:
- **MUSIC PLAYER MENU**: Added `/play` command menu showing "🎵 Τώρα Παίζει" with 4 control buttons
  - Buttons: 🛑 Stop, ▶️ Start/Pause, 🔊 Φωνή (Volume), 📋 Info
  - Shows song title, link section, controls guide
  - Beautiful green embed with thumbnail
- **ADMIN POWER COMMAND**: Added `/admin_power @user add/remove X` for owner-only power management
  - Add points: `/admin_power @user add 100`
  - Remove points: `/admin_power @user remove 50`
- **REMOVED COMMANDS**: Deleted `/add_infraction` and `/infractions` commands
- **RAID DISPLAY**: Simplified to 2 embeds (attacker + defender) with avatars side-by-side
- **VOICE CONNECTION FIX**: Improved `/play` retry logic (3 attempts, 30s timeout each)

### Previous Session Updates:
- **NSFW REMOVAL**: Deleted all NSFW detection command (`/nsfw`, NSFWConfirmationView, NSFWEnforcementView classes)
- **24/7 UPTIME OPTIMIZATION**: 
  - Reduced auto-ping interval from 3 to 2 minutes for maximum uptime
  - Added Flask + aiohttp to requirements.txt
  - Verified keep-alive system: Flask server on port 5000 + auto-ping loop
  - Bot stays alive through continuous pinging every 2 minutes

## System Architecture - Anime Gamification

**Core Features:**
- 52+ viral anime characters database with images
- Per-guild, per-user character selection system
- Historical message counting from Discord history
- Real-time message tracking for power increments
- PvP raid battle system with point economy (50% point stealing)
- Persistent character and stats storage (in-memory)
- Owner-only power management with `/admin_power`

**Character Selection Flow:**
1. User runs `/my_anime_character`
2. If new: Shows 3 random characters (different for each user)
3. User selects character → Shows "🔄 Υπολογίζω..."
4. Bot counts all past messages in background
5. Character assigned with starting points = message count
6. Future messages = +1 point each

**Stats Display:**
- **Points**: Total accumulated power (starts from message count)
- **Message Count**: Total messages ever sent
- **Power Level**: message_count × 0.1 (percentage)
- **Character Image**: Visual representation of chosen anime character
- **Series Name**: Show which anime series the character is from

**Raid Battle System:**
- Shows list of all other players with characters
- Player selects opponent
- Battle result: 50% win chance base (adjusted by power)
- Winner gains 50% of loser's points
- Real-time point transfer
- Compact 2-embed display with avatars

**Admin Power Management:**
- Owner-only `/admin_power` command
- Add or remove power from any user
- Shows Before/After stats
- Saves automatically

**Music Player System:**
- `/play URL_or_search` - Play music from YouTube
- Beautiful interactive menu with song info
- Control buttons: Stop, Start/Pause, Volume, Info
- Queue management with `/queue`
- Volume control: `/volume 0-100`
- Skip: `/skip`
- Loop: `/loop single/queue/off`
- Disconnect: `/disconnect`
- Retry logic for voice connection stability

# External Dependencies

## Core Libraries
- **discord.py**: Discord API wrapper
- **discord.ui**: Button/View components
- **flask**: Web server (keep-alive, port 5000)
- **aiohttp**: Async HTTP client for keep-alive pings
- **requests**: HTTP library for auto-ping
- **yt-dlp**: YouTube video downloading
- **python-dotenv**: Environment variables
- **PyNaCl**: Voice channel support
- **asyncio, random, logging**: Standard utilities

## 24/7 Uptime System
- **Flask Server**: Runs on port 5000 with endpoints `/ping`, `/health`, `/`
- **Auto-ping Mechanism**: Pings keep-alive endpoint every 2 minutes
- **Threading**: Dual-thread model (Flask + Discord bot)
- **Fallback URLs**: Supports both Replit dev domain and Railway public domain
- **Status Page**: HTML dashboard showing bot status and setup instructions

## Anime Characters Database (52+ total)
- Naruto: Naruto, Sasuke, Kakashi
- One Piece: Luffy, Zoro, Nami, Sanji, Chopper, Robin, Franky, Brook, Jinbe
- Dragon Ball: Goku, Vegeta, Frieza, Cell, Majin Buu, Androids, Piccolo, Krillin, etc.
- Demon Slayer: Tanjiro, Nezuko
- My Hero Academia: Deku, Bakugo, Todoroki, All Might
- JoJo's: Jotaro, DIO, Giorno
- Fairy Tail: Natsu, Erza, Gray, Acnologia
- Death Note: Light, L, Ryuk, Misa
- Bleach: Ichigo, etc.
- Attack on Titan: Eren, Levi, Mikasa, Colossal Titan
- Jujutsu Kaisen: Sukuna, Gojo, Yuji
- Re:Zero: Rem, Emilia

# Important Technical Notes

**Data Storage:**
- `anime_characters`: {guild_id: {user_id: {'char_id': X, 'points': Y, 'message_count': Z}}}
- `user_message_counts`: {guild_id: {user_id: message_count}}
- In-memory only (resets on bot restart - consider persistent storage for production)

**Message Counting Algorithm:**
- Iterates max 20 channels per server (avoid rate limits)
- Reads max 50,000 messages per channel
- Updates character points with total count
- Respects Discord rate limiting

**Raid Battle Logic:**
- Power ratio determines win probability
- 100x stronger = 95% win, equal = 55% win, weaker = 40% win
- Point theft: 50% of loser's current points
- Loser's points can go to 0 minimum

**Music Player Features:**
- Retry logic: 3 connection attempts (30s timeout each)
- Interactive menu with 4 control buttons
- Real-time queue management
- Thumbnail display for songs

**Performance Considerations:**
- 10-second timeout on background message counting
- Max 20 channels + 50k messages limit per channel
- Async/await for non-blocking operations
- Error handling for rate limits and permission issues
