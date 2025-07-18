"""
Main bot class for the Discord Counting Bot.
Handles bot initialization, cog loading, and core functionality.
"""

import logging
import os
import asyncio
from typing import Optional

import discord
from discord.ext import commands, tasks

from .db.database import Database

logger = logging.getLogger(__name__)

class CountingBot(commands.Bot):
    """Main bot class for the Discord Counting Bot."""
    
    def __init__(self):
        """Initialize the bot with required intents and configuration."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None  # We'll use slash commands instead
        )
        
        # Initialize database
        self.db: Optional[Database] = None
    
    async def setup_hook(self):
        """Async setup hook called when the bot is starting up."""
        logger.info("Setting up bot...")
        
        # Initialize database
        db_path = os.getenv('DATABASE_PATH', './counting_bot.db')
        self.db = Database(db_path)
        await self.db.initialize()
        
        # Load cogs and commands
        await self._load_extensions()
        
        # Start the presence update task
        self.update_presence.start()
        
        logger.info("Bot setup complete!")
    
    async def _load_extensions(self):
        """Load all bot extensions (cogs and commands)."""
        extensions = [
            'bot.cogs.counting',
            'bot.commands.admin',
            'bot.commands.leaderboard'
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        """Event called when the bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # Set initial presence
        try:
            total_count = await self._get_total_count()
            custom_status = discord.CustomActivity(name=f"counted {total_count:,} times")
            await self.change_presence(activity=custom_status)
            logger.info(f"Set initial presence: counted {total_count:,} times")
        except Exception as e:
            logger.error(f"Failed to set initial presence: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_guild_join(self, guild: discord.Guild):
        """Event called when the bot joins a new guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Initialize guild in database
        if self.db:
            await self.db.initialize_guild(guild.id)
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Event called when the bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
        
        # Clean up guild data from database
        if self.db:
            await self.db.remove_guild(guild.id)
    
    @tasks.loop(minutes=5)
    async def update_presence(self):
        """Update the bot's presence with total count every 5 minutes."""
        if not self.db or not self.is_ready():
            return
        
        try:
            # Get total count across all guilds
            total_count = await self._get_total_count()
            
            # Update presence
            custom_status = discord.CustomActivity(name=f"counted {total_count:,} times")
            await self.change_presence(activity=custom_status)
            
            logger.info(f"Updated presence: counted {total_count:,} times")
            
        except Exception as e:
            logger.error(f"Failed to update presence: {e}")
    
    @update_presence.before_loop
    async def before_update_presence(self):
        """Wait until the bot is ready before starting the presence update task."""
        await self.wait_until_ready()
    
    async def _get_total_count(self) -> int:
        """Get the total count across all guilds."""
        return await self.db.get_total_count()
    
    async def close(self):
        """Clean up resources when the bot is shutting down."""
        logger.info("Shutting down bot...")
        
        if self.db:
            await self.db.close()
        
        await super().close() 