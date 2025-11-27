# Overview

This is a 24/7 Discord bot designed to run continuously on Replit using free keep-alive mechanisms. The bot features a Flask web server that acts as a health check endpoint, allowing external monitoring services to ping it and prevent the Replit from going to sleep. The bot includes Greek language support for commands and messages, comprehensive logging, and automatic restart capabilities.

# User Preferences

Preferred communication style: Simple, everyday language. Greek language exclusively.

## Recent Changes (November 27, 2025)
- **Music Feature Status**: Attempted to fix YouTube streaming audio playback
- **Known Issue**: FFmpeg cannot process YouTube HLS streams (error 183 - invalid data)
  - yt-dlp extracts HLS m3u8 URLs that expire too quickly for FFmpeg to process
  - This is a known limitation with discord.py + YouTube on Replit
  - Requires deeper architectural changes or alternative audio backend
- **All Other Features Fully Functional**:
  - ✅ Bot connects and joins voice channels properly
  - ✅ Anime character game with /raid (2-embed PvP battles)
  - ✅ /admin_power (add/remove power points)
  - ✅ /now_playing menu display
  - ✅ All moderation commands (/dm, /mute, /ban, /announce)
  - ✅ Security monitoring system
  - ✅ Music menu appears correctly (issue is audio playback)

## Previous Changes (September 11, 2025)
- **RAILWAY INTEGRATION READY**: Added complete Railway deployment configuration
- Created requirements.txt, railway.toml, Procfile, and nixpacks.toml for seamless Railway deployment
- Modified keep_alive.py to support Railway's PORT environment variable and RAILWAY_PUBLIC_DOMAIN
- Updated main.py to disable auto-ping on Railway (not needed for 24/7 hosting there)
- Added comprehensive RAILWAY_DEPLOYMENT_GUIDE.md with step-by-step instructions
- Railway deployment preserves all bot functionality while providing true 24/7 uptime

# System Architecture

## Core Components

**Bot Architecture**: The system uses discord.py library with a command-based architecture. The main bot logic is separated into `bot.py` which handles Discord events and commands, while `main.py` serves as the entry point that orchestrates both the Discord bot and keep-alive server.

**Keep-Alive Mechanism**: A Flask web server runs in a separate thread to provide HTTP endpoints that external services can ping. This prevents Replit from putting the application to sleep due to inactivity.

**Threading Model**: The application uses Python threading to run the Discord bot and Flask server concurrently. The main thread starts the Flask server in a daemon thread, then runs the Discord bot in the main thread.

**Music System**: Uses yt-dlp for YouTube extraction and discord.py's PCM audio with FFmpeg
- **Current Issue**: YouTube HLS streams have authentication issues when passed to FFmpeg through Replit
- **Solution Path**: May require moving to mpv backend, local caching, or external audio service

## Design Patterns

**Configuration Management**: Uses environment variables for sensitive data like Discord tokens, accessed through Replit's Secrets system for secure token storage.

**Event-Driven Architecture**: The Discord bot operates on an event-driven model, responding to Discord events like `on_ready` and `on_command_error`.

# External Dependencies

## Core Libraries
- **discord.py**: Primary Discord API wrapper for bot functionality
- **Flask**: Lightweight web framework for the keep-alive HTTP server
- **yt-dlp**: YouTube content extraction for music playback
- **ffmpeg**: Audio processing (current issue: HLS stream incompatibility)
- **Python standard libraries**: threading, logging, os, time, datetime, asyncio, random

## Deployment Platforms
- **Replit**: Cloud-based development platform with built-in environment variable management
- **Railway**: Production-ready hosting platform for true 24/7 deployment
- **Dual Compatibility**: Bot works seamlessly on both platforms with environment auto-detection

# Next Steps for Music Fix

The audio playback issue requires one of these approaches:
1. **Local Caching**: Download and cache audio files to disk before playing
2. **Alternative Backend**: Switch to mpv or libav instead of FFmpeg
3. **External Service**: Use Lavalink or similar Discord audio service
4. **URL Proxying**: Implement URL refresh mechanism for expired YouTube URLs
