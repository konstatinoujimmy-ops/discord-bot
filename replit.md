# Overview

This is a 24/7 Discord bot designed to run continuously on Replit with feature-rich gaming and moderation systems. The bot includes music playback (YouTube via yt-dlp), voice channel management, advanced security monitoring, moderation tools, partnership management system, anime character gamification, and comprehensive slash commands. **NSFW detection system removed.** All communication is in Greek language exclusively. Bot stays online 24/7 using Flask keep-alive + auto-ping mechanism.

# User Preferences

Preferred communication style: Simple, everyday language - Greek only, no Portuguese or English.
Device: Mobile only - requires simple step-by-step guidance with visual confirmations.

## Recent Changes (November 27, 2025 - Latest)

### Session 27/11 Updates:
- **NSFW REMOVAL**: Deleted all NSFW detection command (`/nsfw`, NSFWConfirmationView, NSFWEnforcementView classes)
- **24/7 UPTIME OPTIMIZATION**: 
  - Reduced auto-ping interval from 3 to 2 minutes for maximum uptime
  - Added Flask + aiohttp to requirements.txt
  - Verified keep-alive system: Flask server on port 5000 + auto-ping loop
  - Bot stays alive through continuous pinging every 2 minutes
- **Anime Character Raid System**: Three-embed display with user avatars (attacker, battle result, defender)
- **Character Stats System**: Points ⭐, Message Count 📝, Power Level 💪
- **Complete Infraction Tracking**: Types now TIMEOUT/MUTE/KICK/BAN (NSFW removed)

## System Architecture - Anime Gamification

**Core Features:**
- 52+ viral anime characters database with images
- Per-guild, per-user character selection system
- Historical message counting from Discord history
- Real-time message tracking for power increments
- PvP raid battle system with point economy
- Persistent character and stats storage (in-memory)

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

**Infraction System:**
- Manual tracking with `/add_infraction`
- Types: NSFW, TIMEOUT, MUTE, KICK, BAN
- View history with `/infractions @user`
- Automatic NSFW detection with timeout

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
- Base 50% win probability
- Adjusted if attacker_power > defender_power × 0.8 → attacker wins
- Point theft: 50% of defender's current points transferred to winner
- Loser's points can go to 0 minimum

**Message Integration:**
- Every message from any user tracked in real-time
- Character power increases if user has selected a character
- Message counting in `on_message` event handler
- Seamless integration with existing bot events

**Performance Considerations:**
- 10-second timeout on background message counting
- Max 20 channels + 50k messages limit per channel
- Async/await for non-blocking operations
- Error handling for rate limits and permission issues
