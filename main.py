#!/usr/bin/env python3
"""
Main entry point for the Discord Counting Bot.
Handles bot initialization, cog loading, and startup.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from bot import CountingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to initialize and run the bot."""
    # Load environment variables
    load_dotenv()
    
    # Get bot token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        return
    
    # Create and run bot
    bot = CountingBot()
    
    try:
        logger.info("Starting Discord Counting Bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 