"""
Counting cog for the Discord Counting Bot.
Handles the core counting game logic and message processing.
"""

import logging
import os
import asyncio
from typing import Optional, Dict, Tuple

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class Counting(commands.Cog):
    """Cog for handling the counting game functionality."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the counting cog."""
        self.bot = bot
        # Track grace periods for each guild: {guild_id: (expected_number, embed_message, task, mistake_user_id)}
        self.grace_periods: Dict[int, Tuple[int, discord.Message, asyncio.Task, int]] = {}
    
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
            # Check if we're in a grace period
            if guild_id in self.grace_periods:
                await self._handle_grace_period_message(message)
                return
            
            # Check if message starts with emote-like characters
            if message.content.startswith((':', '<', '@')):
                return
            
            # Try to parse the first number from the message
            number = self._extract_first_number(message.content)
            if number is None:
                # No number found, ignore silently
                return
            
            # Get current count and last counter
            current_count = await self.bot.db.get_current_count(guild_id)
            last_counter = await self.bot.db.get_last_counter(guild_id)
            
            # Check if the same user is counting twice in a row FIRST
            if last_counter == user_id:
                # Same user counting twice in a row - ignore silently (regardless of number)
                return
            
            # Check if this is the correct next number
            expected_number = current_count + 1
            
            if number != expected_number:
                # Wrong number - start grace period
                await self._start_grace_period(message, expected_number, user_id)
                return
            
            # Valid count! Increment the count
            success = await self.bot.db.increment_count(guild_id, user_id)
            
            if success:
                # Use custom emote or fallback to default
                success_emote = os.getenv('SUCCESS_EMOTE', '✅')
                await self._add_reaction_safe(message, success_emote)
                logger.info(f"Valid count {number} by user {user_id} in guild {guild_id}")
            else:
                # Database error
                error_emote = os.getenv('ERROR_EMOTE', '❌')
                await self._add_reaction_safe(message, error_emote)
                logger.error(f"Failed to increment count for guild {guild_id}")
                
        except Exception as e:
            logger.error(f"Error processing counting message: {e}")
            # Don't show error to user, just log it
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Handle bot joining a new guild."""
        logger.info(f"Bot joined guild: {guild.name} (ID: {guild.id})")
    
    def _extract_first_number(self, text: str) -> Optional[int]:
        """
        Extract the first number from the start of a text string.
        
        Args:
            text: The text to search for a number
            
        Returns:
            The first number found, or None if no number is found
        """
        import re
        
        # Remove Discord formatting characters from the start
        # This handles: ***18***, **18**, *18*, __18__, etc.
        cleaned_text = re.sub(r'^[*_~`]+', '', text.strip())
        
        # Check if the cleaned text starts with digits
        match = re.match(r'^(\d+)', cleaned_text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None
    
    async def _start_grace_period(self, message: discord.Message, expected_number: int, mistake_user_id: int):
        """Start a 5-second grace period for someone to correct the mistake."""
        guild_id = message.guild.id
        
        # Cancel any existing grace period
        if guild_id in self.grace_periods:
            await self._end_grace_period(guild_id, reset_count=True)
        
        # Create the initial embed
        embed = discord.Embed(
            title="🚨 COUNTING MISTAKE! 🚨",
            description=f"**{expected_number}** was expected, but someone made a mistake!\n\n"
                       f"**You have 5 seconds for someone else to save the count!**\n"
                       f"Quick! Type **{expected_number}** to save it!",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="⏰ Time is running out!")
        
        # Send the embed
        embed_msg = await message.channel.send(embed=embed)
        
        # Start the countdown task
        countdown_task = asyncio.create_task(self._grace_period_countdown(guild_id, embed_msg, expected_number))
        
        # Store the grace period info with the mistake user ID
        self.grace_periods[guild_id] = (expected_number, embed_msg, countdown_task, mistake_user_id)
    
    async def _grace_period_countdown(self, guild_id: int, embed_msg: discord.Message, expected_number: int):
        """Handle the 5-second countdown with updating embed."""
        try:
            # Countdown: 5, 4, 3, 2, 1, 0
            for i in range(5, -1, -1):
                # Check if grace period was cancelled (someone saved the count)
                if guild_id not in self.grace_periods:
                    return
                
                if i == 0:
                    # Time's up! Show final message
                    embed = discord.Embed(
                        title="🚨 COUNTING MISTAKE! 🚨",
                        description=f"**{expected_number}** was expected, but someone made a mistake!\n\n"
                                   f"**⏰ TIME'S UP!**\n"
                                   f"No one saved the count in time!",
                        color=discord.Color.red(),
                        timestamp=discord.utils.utcnow()
                    )
                    embed.set_footer(text="💥 Count will be reset!")
                else:
                    # Update the embed
                    embed = discord.Embed(
                        title="🚨 COUNTING MISTAKE! 🚨",
                        description=f"**{expected_number}** was expected, but someone made a mistake!\n\n"
                                   f"**⏰ {i} second{'s' if i != 1 else ''} remaining!**\n"
                                   f"Quick! Type **{expected_number}** to save it!",
                        color=discord.Color.red(),
                        timestamp=discord.utils.utcnow()
                    )
                    embed.set_footer(text="⏰ Time is running out!")
                
                await embed_msg.edit(embed=embed)
                
                if i > 0:  # Sleep before the next update (including before showing "TIME'S UP")
                    await asyncio.sleep(1)
            
            # Time's up! Reset the count (only if count wasn't saved)
            if guild_id in self.grace_periods:
                try:
                    await self._end_grace_period(guild_id, reset_count=True)
                except Exception as e:
                    logger.error(f"Error in _end_grace_period for guild {guild_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in grace period countdown for guild {guild_id}: {e}")
            await self._end_grace_period(guild_id, reset_count=True)
    
    async def _handle_grace_period_message(self, message: discord.Message):
        """Handle messages during grace period."""
        guild_id = message.guild.id
        user_id = message.author.id
        
        if guild_id not in self.grace_periods:
            return
        
        expected_number, embed_msg, countdown_task, mistake_user_id = self.grace_periods[guild_id]
        
        # Check if the countdown task is still running (not cancelled)
        if countdown_task.done():
            # Countdown finished, grace period is over
            return
        
        # Don't allow the person who made the mistake to save it
        if user_id == mistake_user_id:
            return
        
        # Check if message starts with emote-like characters
        if message.content.startswith((':', '<', '@')):
            return
        
        # Try to extract the number
        number = self._extract_first_number(message.content)
        if number is None:
            return
        
        # Check if it's the correct number
        if number == expected_number:
            # SUCCESS! Save the count
            success = await self.bot.db.increment_count(guild_id, user_id)
            
            if success:
                # Cancel the countdown
                countdown_task.cancel()
                
                # Create celebration embed
                embed = discord.Embed(
                    title="🎉 GREAT TEAMWORK! 🎉",
                    description=f"**{message.author.display_name}** saved the count!\n\n"
                               f"✅ **{expected_number}** has been saved!\n"
                               f"The count continues!",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_footer(text="🎊 Count saved successfully!")
                
                await embed_msg.edit(embed=embed)
                
                # Add celebration reaction
                success_emote = os.getenv('SUCCESS_EMOTE', '✅')
                await self._add_reaction_safe(message, success_emote)
                
                # Clean up grace period
                del self.grace_periods[guild_id]
                
                logger.info(f"Count saved by {user_id} in guild {guild_id} during grace period")
            else:
                # Database error
                error_emote = os.getenv('ERROR_EMOTE', '❌')
                await self._add_reaction_safe(message, error_emote)
                logger.error(f"Failed to save count during grace period for guild {guild_id}")
    
    async def _end_grace_period(self, guild_id: int, reset_count: bool = False):
        """End the grace period and optionally reset the count."""
        if guild_id not in self.grace_periods:
            return
        
        expected_number, embed_msg, countdown_task, mistake_user_id = self.grace_periods[guild_id]
        
        # Cancel the countdown task
        try:
            countdown_task.cancel()
        except Exception as e:
            logger.warning(f"Error cancelling countdown task for guild {guild_id}: {e}")
        
        if reset_count:
            try:
                # Reset the count
                await self.bot.db.reset_count(guild_id)
                
                # Create failure embed
                embed = discord.Embed(
                    title="💥 COUNT RESET! 💥",
                    description=f"**Time's up!** No one saved the count in time.\n\n"
                               f"❌ The count has been reset to **0**\n"
                               f"Start counting from **1** again!",
                    color=discord.Color.dark_red(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_footer(text="💔 Better luck next time!")
                
                # Make embed update non-blocking
                async def update_embed():
                    try:
                        await embed_msg.edit(embed=embed)
                    except Exception as edit_error:
                        logger.error(f"Embed edit failed for guild {guild_id}: {edit_error}")
                
                # Start embed update as a task (non-blocking)
                asyncio.create_task(update_embed())
            except Exception as e:
                logger.error(f"Error ending grace period for guild {guild_id}: {e}")
        
        # Clean up
        try:
            del self.grace_periods[guild_id]
        except KeyError:
            pass  # Already cleaned up
    
    async def _add_reaction_safe(self, message: discord.Message, emote: str):
        """
        Safely add a reaction, falling back to default emotes if custom emote fails.
        
        Args:
            message: The message to add the reaction to
            emote: The emote to add (can be custom or Unicode)
        """
        try:
            await message.add_reaction(emote)
        except discord.HTTPException as e:
            if e.code == 10014:  # Unknown Emoji error
                # Fall back to default emotes
                if emote == os.getenv('SUCCESS_EMOTE', '✅'):
                    await message.add_reaction('✅')
                    logger.warning(f"Custom success emote not available, using default ✅")
                elif emote == os.getenv('ERROR_EMOTE', '❌'):
                    await message.add_reaction('❌')
                    logger.warning(f"Custom error emote not available, using default ❌")
                else:
                    # For any other custom emote, try a generic fallback
                    await message.add_reaction('✅')
                    logger.warning(f"Custom emote '{emote}' not available, using default ✅")
            else:
                # Re-raise other HTTP errors
                raise
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Handle bot leaving a guild."""
        logger.info(f"Bot left guild: {guild.name} (ID: {guild.id})")

async def setup(bot: commands.Bot):
    """Set up the counting cog."""
    await bot.add_cog(Counting(bot)) 