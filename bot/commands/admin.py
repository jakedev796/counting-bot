"""
Admin commands for the Discord Counting Bot.
Contains slash commands for server administrators.
"""

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    """Cog for admin commands."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the admin commands cog."""
        self.bot = bot
    
    @app_commands.command(
        name="setcountingchannel",
        description="Set the counting channel for this server"
    )
    @app_commands.describe(
        channel="The channel where counting will take place"
    )
    async def set_counting_channel(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel
    ):
        """Set the counting channel for the server."""
        # Check if user has Manage Server permission
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need the 'Manage Server' permission to use this command.",
                ephemeral=True
            )
            return
        
        try:
            guild_id = interaction.guild_id
            
            # Set the counting channel in database
            await self.bot.db.set_counting_channel(guild_id, channel.id)
            
            await interaction.response.send_message(
                f"✅ Counting channel set to {channel.mention}!",
                ephemeral=True
            )
            
            logger.info(f"Counting channel set to {channel.id} for guild {guild_id} by user {interaction.user.id}")
            
        except Exception as e:
            logger.error(f"Error setting counting channel: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while setting the counting channel.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="resetcount",
        description="Reset the count for this server"
    )
    @app_commands.describe(
        reason="Optional reason for resetting the count"
    )
    async def reset_count(
        self, 
        interaction: discord.Interaction, 
        reason: Optional[str] = None
    ):
        """Reset the count for the server."""
        # Check if user has Manage Server permission
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need the 'Manage Server' permission to use this command.",
                ephemeral=True
            )
            return
        
        try:
            guild_id = interaction.guild_id
            
            # Reset the count in database
            await self.bot.db.reset_count(guild_id)
            
            # Create response message
            response = "✅ Count has been reset to 0!"
            if reason:
                response += f"\nReason: {reason}"
            
            await interaction.response.send_message(
                response,
                ephemeral=True
            )
            
            logger.info(f"Count reset for guild {guild_id} by user {interaction.user.id}. Reason: {reason or 'None'}")
            
        except Exception as e:
            logger.error(f"Error resetting count: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while resetting the count.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Set up the admin commands cog."""
    await bot.add_cog(AdminCommands(bot)) 