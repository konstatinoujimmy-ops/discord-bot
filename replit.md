# Overview

This is a 24/7 Discord bot designed to run continuously on Replit with feature-rich gaming and moderation systems. The bot includes music playback (YouTube via yt-dlp), voice channel management, advanced security monitoring, moderation tools, partnership management system, anime character gamification, and comprehensive slash commands. **NSFW detection system removed.** All communication is in Greek language exclusively. Bot stays online 24/7 using Flask keep-alive + auto-ping mechanism.

# User Preferences

Preferred communication style: Simple, everyday language - Greek only, no Portuguese or English.
Device: Mobile only - requires simple step-by-step guidance with visual confirmations.

## Recent Changes (November 27, 2025 - Latest Session)

### Final Updates:
- **MUSIC PLAYER FIXED**: 
  - `/play` now shows "🎵 Τώρα Παίζει" menu with 4 control buttons (Stop, Start/Pause, Volume, Info)
  - Works for both single songs and playlists
  - No more "Προστέθηκε" messages cluttering the chat
- **AUDIO PLAYBACK FIXED**: 
  - Changed from FFmpegOpusAudio to FFmpegPCMAudio for reliability
  - Simplified ffmpeg options for better compatibility
  - Audio now plays properly in voice channels
- **ADMIN POWER COMMAND**: `/admin_power @user add/remove X` for owner-only power management
- **REMOVED COMMANDS**: Deleted `/add_infraction` and `/infractions` commands
- **RAID DISPLAY**: Compact 2-embed format (attacker + defender) with avatars

### Previous Session Updates:
- **NSFW REMOVAL**: Deleted all NSFW detection commands
- **24/7 UPTIME**: Auto-ping every 2 minutes
- **Voice Connection**: Improved retry logic (3 attempts, 30s timeout each)

## System Architecture - Music Player

**Music Player Features:**
- `/play URL_or_search` - Play from YouTube
- Interactive menu shows song info with thumbnail
- Control buttons: 🛑 Stop, ▶️ Start/Pause, 🔊 Volume, 📋 Info
- Queue management with `/queue` command
- Loop modes: `/loop single/queue/off`
- Skip: `/skip`
- Disconnect: `/disconnect`
- Now playing: `/now_playing` (shows menu anytime)

**Audio Configuration:**
- FFmpegPCMAudio for maximum compatibility
- 128k bitrate, 48kHz sample rate, stereo audio
- Automatic stream reconnection with max 5 second delay

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
2. If new: Shows 3 random characters
3. User selects character
4. Bot counts all past messages in background
5. Character assigned with starting points = message count
6. Future messages = +1 point each

**Raid Battle System:**
- `/raid` shows list of other players
- Select opponent and battle
- 50% base win chance (adjusted by power ratio)
- Winner gains 50% of loser's points
- Compact 2-embed display with user avatars

# External Dependencies

## Core Libraries
- **discord.py**: Discord API wrapper
- **discord.ui**: Button/View components
- **flask**: Web server (keep-alive, port 5000)
- **aiohttp**: Async HTTP client
- **yt-dlp**: YouTube video downloading
- **python-dotenv**: Environment variables
- **PyNaCl**: Voice channel support

## 24/7 Uptime System
- **Flask Server**: Port 5000 endpoints (`/ping`, `/health`, `/`)
- **Auto-ping**: Every 2 minutes to keep bot alive
- **Threading**: Dual-thread (Flask + Discord bot)
- **Fallback URLs**: Replit dev domain + Railway support

## Music Streaming
- **yt-dlp**: Format: bestaudio/best, Opus extraction enabled
- **FFmpeg**: PCMAudio at 128k, 48kHz, stereo with reconnect
- **Discord Voice**: Full audio streaming with buffer management

## Anime Characters Database (52+ total)
- Naruto, One Piece, Dragon Ball, Demon Slayer, My Hero Academia, JoJo's, Fairy Tail, Death Note, Bleach, Attack on Titan, Jujutsu Kaisen, Re:Zero and more

# Important Technical Notes

**Data Storage:**
- `anime_characters`: {guild_id: {user_id: {'char_id': X, 'points': Y, 'message_count': Z}}}
- In-memory only (resets on bot restart)

**Raid Battle Logic:**
- Power ratio determines win probability (100x = 95%, equal = 55%, weaker = 40%)
- Point theft: 50% of loser's points to winner
- Cooldown: 2 minutes between raids

**Performance:**
- 10-second timeout on message counting
- Max 20 channels + 50k messages per channel
- Async/await for non-blocking operations
- Error handling for rate limits and Discord issues
