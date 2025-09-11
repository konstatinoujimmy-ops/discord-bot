"""
Discord Bot with 24/7 Keep-Alive for Replit
Main entry point that starts both the Discord bot and Flask server
"""

import os
import threading
import time
import logging
from keep_alive import keep_alive
from bot import run_bot
from auto_ping import start_auto_ping

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot and keep-alive server"""
    try:
        logger.info("Starting Discord Bot with Keep-Alive mechanism...")
        
        # Start the Flask keep-alive server in a separate thread
        logger.info("Starting keep-alive web server...")
        keep_alive()
        
        # Small delay to ensure Flask server starts
        time.sleep(2)
        
        # Start auto-ping system μόνο στο Replit για 24/7 uptime
        if os.getenv('REPLIT_DEV_DOMAIN') or os.getenv('REPL_SLUG'):
            logger.info("Starting auto-ping system (Replit detected)...")
            start_auto_ping()
        else:
            logger.info("Skipping auto-ping system (Railway/Production environment detected)")
        
        # Start the Discord bot
        logger.info("Starting Discord bot...")
        run_bot()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        # Auto-restart mechanism
        logger.info("Attempting to restart in 10 seconds...")
        time.sleep(30)
        main()

if __name__ == "__main__":
    main()
