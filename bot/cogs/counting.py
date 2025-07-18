"""
Counting cog for the Discord Counting Bot.
Handles the core counting game logic and message processing.
"""

import logging
from typing import Optional

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class Counting(commands.Cog):
    """Cog for handling the counting game functionality."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the counting cog."""
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle incoming messages for the counting game."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Get guild and check if it's a valid guild
        if not message.guild:
            return
        
        guild_id = message.guild.id
        
        # Get the counting channel for this guild
        counting_channel_id = await self.bot.db.get_counting_channel(guild_id)
        if not counting_channel_id or message.channel.id != counting_channel_id:
            return
        
        # Process the counting message
        await self._process_counting_message(message)
    
    async def _process_counting_message(self, message: discord.Message):
        """Process a message in the counting channel."""
        guild_id = message.guild.id
        user_id = message.author.id
        
        try:
            # Try to parse the message as an integer
            try:
                number = int(message.content.strip())
            except ValueError:
                # Not an integer, ignore silently
                return
            
            # Get current count and last counter
            current_count = await self.bot.db.get_current_count(guild_id)
            last_counter = await self.bot.db.get_last_counter(guild_id)
            
            # Check if this is the correct next number
            expected_number = current_count + 1
            
            if number != expected_number:
                # Wrong number
                await message.add_reaction('❌')
                logger.info(f"Wrong number {number} (expected {expected_number}) by user {user_id} in guild {guild_id}")
                return
            
            # Check if the same user is counting twice in a row
            if last_counter == user_id:
                # Same user counting twice in a row
                await message.add_reaction('❌')
                logger.info(f"User {user_id} tried to count twice in a row in guild {guild_id}")
                return
            
            # Valid count! Increment the count
            success = await self.bot.db.increment_count(guild_id, user_id)
            
            if success:
                await message.add_reaction('✅')
                logger.info(f"Valid count {number} by user {user_id} in guild {guild_id}")
            else:
                # Database error
                await message.add_reaction('❌')
                logger.error(f"Failed to increment count for guild {guild_id}")
                
        except Exception as e:
            logger.error(f"Error processing counting message: {e}")
            # Don't show error to user, just log it
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Handle bot joining a new guild."""
        logger.info(f"Bot joined guild: {guild.name} (ID: {guild.id})")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Handle bot leaving a guild."""
        logger.info(f"Bot left guild: {guild.name} (ID: {guild.id})")

async def setup(bot: commands.Bot):
    """Set up the counting cog."""
    await bot.add_cog(Counting(bot)) 