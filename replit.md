# Overview

This is a 24/7 Discord bot designed to run continuously on Bot-Hosting.net with feature-rich gaming and moderation systems. The bot includes music playback (YouTube via yt-dlp), voice channel management, advanced security monitoring, moderation tools, partnership management system, NSFW content detection, anime character gamification, and comprehensive slash commands. All communication is in Greek language exclusively.

# User Preferences

Preferred communication style: Simple, everyday language - Greek only, no Portuguese or English.
Device: Mobile only - requires simple step-by-step guidance with visual confirmations.

## Recent Changes (November 27, 2025)
- **ANIME CHARACTER SYSTEM**: Complete gamification system with 52 viral anime characters
- Players can use `/my_anime_character` to select from 3 random unique characters (different for each player)
- Each character displays its image automatically when selected
- Character power increases with every message sent (1 message = 1 power point)
- `/raid` command enables PvP battles between characters with 50% point theft on victory
- Real-time points calculation based on message count
- Battle system with 50% base win chance (influenced by power levels)
- `/infractions` and `/add_infraction` commands for tracking user violations
- Manual infraction addition with multiple types (NSFW, TIMEOUT, MUTE, KICK, BAN)
- Created anime_data.py with 52 viral anime characters from Naruto, One Piece, Dragon Ball, Demon Slayer, My Hero Academia, JoJo's, Fairy Tail, Death Note, Bleach, Attack on Titan, Jujutsu Kaisen, Re:Zero, and more

## Previous Changes (November 2025)
- Successfully deployed bot to Bot-Hosting.net with 6 core files
- Fixed DISCORD_TOKEN loading using python-dotenv in start.py
- Implemented partnership system with approval workflow (validates 450+ member requirement)
- Created NSFW detection system with automatic 10-minute timeout
- Added role-based permissions (role ID: 1162022515846172723)

# System Architecture

## Core Components

**Bot Architecture**: Discord.py with command-based architecture. Main logic in `bot.py`, entry point in `main.py` or `start.py` for Bot-Hosting.net compatibility.

**Anime Character System**: 
- 52+ viral anime characters database in `anime_data.py`
- Per-user character selection with unique 3-character choices per user
- Message-based power progression system
- PvP raid battles with point theft mechanics
- Database: `anime_characters` (guild_id → user_id → character data)

**Keep-Alive Mechanism**: Flask web server for health checks (Replit compatibility).

**Threading Model**: Concurrent Discord bot and Flask server execution.

**Error Handling**: Global error handlers with automatic recovery.

**Logging System**: Centralized INFO-level logging to console.

## Anime Gamification System

**Character Selection** (`/my_anime_character`):
- First-time users see 3 random unique characters from 52+ database
- Each user gets different random selection (no duplicates between users)
- Selected character displays with series name and image
- Starting power: 0 points

**Power System**:
- Every message = +1 point to character power
- Points tracked globally for raid battles
- Persistent across commands

**Raid System** (`/raid`):
- Battle against other players' characters
- View all active characters with their power levels
- 50% base win chance (adjusted by power differential)
- Winner takes 50% of loser's points
- Real-time point transfers

**Violation Tracking**:
- `/infractions @user`: View complete violation history
- `/add_infraction @user TYPE reason`: Manual violation recording (Owner-only)
- Types: NSFW, TIMEOUT, MUTE, KICK, BAN
- Automatic NSFW tracking with 10-minute timeout
- Persistent violation database per guild

## Design Patterns

**Configuration Management**: Environment variables for Discord token (DISCORD_TOKEN).

**Event-Driven Architecture**: Discord events (on_message, on_raid, etc.) trigger business logic.

**View-Based UI**: Discord.py Views for button interactions (AnimeCharacterView, RaidView).

**Game State Management**: In-memory databases for real-time character and raid data.

# External Dependencies

## Core Libraries
- **discord.py**: Discord API wrapper
- **discord.ui**: Button/View components for interactive UI
- **flask**: Web server (keep-alive)
- **yt-dlp**: YouTube video downloading
- **python-dotenv**: Environment variable loading
- **Standard libraries**: random, asyncio, datetime, logging, threading

## Anime Characters Database
52+ viral characters from:
- Naruto (Naruto, Sasuke, etc.)
- One Piece (Luffy, Zoro, Nami, Sanji, etc.)
- Dragon Ball (Goku, Vegeta, Frieza, Cell, etc.)
- Demon Slayer (Tanjiro, Nezuko, etc.)
- My Hero Academia (Deku, Bakugo, All Might, etc.)
- JoJo's Bizarre Adventure (Jotaro, DIO, Giorno, etc.)
- Fairy Tail (Natsu, Erza, Gray, etc.)
- Death Note (Light, L, Ryuk, Misa)
- Bleach (Ichigo, Kenpachi, etc.)
- Attack on Titan (Eren, Levi, Mikasa, Colossal Titan, etc.)
- Jujutsu Kaisen (Sukuna, Gojo, Yuji, etc.)
- Re:Zero (Rem, Emilia, etc.)

## External Services
- **Discord API**: Bot communication and events
- **Bot-Hosting.net**: Production deployment platform
- **YouTube (yt-dlp)**: Music streaming via /play command
- **Image URLs**: Character images from pinimg.com (placeholder URLs in anime_data.py)

## Important Technical Notes

**In-Memory Storage**: 
- `anime_characters`: Character selections and points (per guild)
- `user_message_counts`: Message tracking for power calculation
- `nsfw_violations`: NSFW violation tracking
- `infractions_db`: User infraction history
- Data persists during bot runtime but resets on restart (consider persistent storage for production)

**Raid Battle Logic**:
- Base 50% win probability
- Adjusted by: if attacker_power > defender_power * 0.8 → attacker wins
- Point theft: 50% of defender's current points

**Message Counter Integration**:
- Integrated into existing `on_message` event handler
- Tracks message count per user per guild
- Updates character power in real-time
- Only counts messages from users with selected characters

**Infraction Types**:
- NSFW: Automatic detection and manual addition
- TIMEOUT: Manual record
- MUTE: Manual record
- KICK: Manual record
- BAN: Manual record
