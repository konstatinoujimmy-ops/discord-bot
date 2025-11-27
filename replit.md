# Overview

This is a 24/7 Discord bot designed to run continuously on Bot-Hosting.net with feature-rich gaming and moderation systems. The bot includes music playback (YouTube via yt-dlp), voice channel management, advanced security monitoring, moderation tools, partnership management system, NSFW content detection, anime character gamification, and comprehensive slash commands. All communication is in Greek language exclusively.

# User Preferences

Preferred communication style: Simple, everyday language - Greek only, no Portuguese or English.
Device: Mobile only - requires simple step-by-step guidance with visual confirmations.

## Recent Changes (November 27, 2025 - Latest)
- **ANIME CHARACTER SYSTEM COMPLETE**: Full gamification system with 52 viral anime characters
- **Character Selection**: `/my_anime_character` command with 3 random unique options per user
- **Character Display**: Each character shows image + series name + stats
- **Historical Message Counting**: Automatically counts all past messages (up to 50k per channel) when character is selected
- **Stats Display**: Shows Points ⭐, Message Count 📝, Power Level 💪% with formatted numbers
- **Persistent Stats**: When user re-runs `/my_anime_character`, shows their current character with all stats
- **Power Calculation**: Power Level = Message Count × 0.1%
- **Raid System**: `/raid` command to battle other players' characters
- **Point Theft Mechanic**: Winner takes 50% of loser's points in raid battles
- **Real-time Updates**: Message counter updates character power automatically
- **Complete Infraction Tracking**: `/infractions` and `/add_infraction` commands with violation history

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
- **flask**: Web server (keep-alive)
- **yt-dlp**: YouTube video downloading
- **python-dotenv**: Environment variables
- **asyncio, random, logging**: Standard utilities

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
