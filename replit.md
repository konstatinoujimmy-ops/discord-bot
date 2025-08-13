# Overview

This is a 24/7 Discord bot designed to run continuously on Replit using free keep-alive mechanisms. The bot features a Flask web server that acts as a health check endpoint, allowing external monitoring services to ping it and prevent the Replit from going to sleep. The bot includes Greek language support for commands and messages, comprehensive logging, and automatic restart capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (August 13, 2025)
- Successfully integrated user's existing Discord bot code with 24/7 keep-alive system
- Preserved all original slash commands: /dm, /dm2, /mute, /announce, /play, /disconnect, /permissions
- Added yt-dlp dependency for music functionality
- Bot successfully connected to Discord as "Dragon ball greece official#6692"
- Keep-alive web server running on port 5000 with Greek interface
- Auto-restart mechanism and comprehensive logging implemented
- Enhanced music player with interactive control buttons (Stop, Start/Pause, Volume, Info)
- Improved audio quality with Opus codec and optimized FFMPEG settings
- Fixed UptimeRobot integration with correct Replit dev domain URL
- User confirmed UptimeRobot setup complete for 24/7 operation
- Opened /play command to all users (not just staff)
- Ultra premium audio quality (512k bitrate, 48kHz, Discord-optimized Opus)
- Advanced security: Auto-removal of ban permissions from non-owners
- Added /ban command (owner-only) and /protect_roles for security monitoring
- Real-time role permission monitoring with owner notifications
- CONFIRMED: 24/7 system working perfectly with UptimeRobot monitoring
- Bot auto-restarts every ~20min (normal Replit behavior) and UptimeRobot immediately re-activates it
- Ultra premium audio quality implemented with dynamic audio normalization
- ULTIMATE SECURITY SYSTEM: Auto-monitors channels, @everyone mentions, bans, kicks, timeouts
- Auto-ping system ensures 24/7 uptime without external services
- /security_status command accessible to owner and staff roles

# System Architecture

## Core Components

**Bot Architecture**: The system uses discord.py library with a command-based architecture. The main bot logic is separated into `bot.py` which handles Discord events and commands, while `main.py` serves as the entry point that orchestrates both the Discord bot and keep-alive server.

**Keep-Alive Mechanism**: A Flask web server runs in a separate thread to provide HTTP endpoints that external services can ping. This prevents Replit from putting the application to sleep due to inactivity. The keep-alive server provides both a status page and a `/ping` endpoint for monitoring services.

**Threading Model**: The application uses Python threading to run the Discord bot and Flask server concurrently. The main thread starts the Flask server in a daemon thread, then runs the Discord bot in the main thread.

**Error Handling**: Comprehensive error handling includes global command error handlers for the Discord bot and automatic restart mechanisms in the main application loop. The system logs all errors and attempts to recover from failures automatically.

**Logging System**: Centralized logging configuration using Python's logging module with INFO level logging to console, providing visibility into bot operations and debugging information.

## Design Patterns

**Configuration Management**: Uses environment variables for sensitive data like Discord tokens, accessed through Replit's Secrets system for secure token storage.

**Event-Driven Architecture**: The Discord bot operates on an event-driven model, responding to Discord events like `on_ready` and `on_command_error`.

**Template Rendering**: The Flask server uses inline HTML templates for the status page, avoiding external template dependencies.

# External Dependencies

## Core Libraries
- **discord.py**: Primary Discord API wrapper for bot functionality
- **Flask**: Lightweight web framework for the keep-alive HTTP server
- **Python standard libraries**: threading, logging, os, time, datetime, asyncio, random

## External Services Integration
- **Discord API**: Direct integration with Discord servers for bot operations
- **UptimeRobot**: Recommended external monitoring service for keep-alive pings
- **Cron-Job.org**: Alternative monitoring service option
- **Replit Secrets**: Environment variable management for secure token storage

## Deployment Platform
- **Replit**: Cloud-based development and hosting platform with built-in environment variable management and automatic HTTPS endpoints