"""
Leaderboard command for the Discord Counting Bot.
Displays server statistics with global rankings.
"""

import logging
from typing import List, Tuple

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

class LeaderboardCommands(commands.Cog):
    """Cog for leaderboard commands."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the leaderboard commands cog."""
        self.bot = bot
    
    @app_commands.command(
        name="leaderboard",
        description="View the counting leaderboard for this server"
    )
    async def leaderboard(self, interaction: discord.Interaction):
        """Display the leaderboard for the server."""
        try:
            guild_id = interaction.guild_id
            guild_name = interaction.guild.name
            
            # Get guild stats
            guild_stats = await self.bot.db.get_guild_stats(guild_id)
            
            # Get global rankings
            global_rankings = await self.bot.db.get_global_rankings()
            
            # Calculate global ranks
            current_count_rank = self._get_rank(guild_id, global_rankings['current_count'])
            high_score_rank = self._get_rank(guild_id, global_rankings['high_score'])
            total_score_rank = self._get_rank(guild_id, global_rankings['total_score'])
            
            # Create embed
            embed = discord.Embed(
                title=f"📊 {guild_name}",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add stats fields
            embed.add_field(
                name="Current Number",
                value=f"{guild_stats['current_count']} (#{current_count_rank})",
                inline=True
            )
            
            embed.add_field(
                name="High Score",
                value=f"{guild_stats['high_score']} (#{high_score_rank})",
                inline=True
            )
            
            embed.add_field(
                name="Total Score",
                value=f"{guild_stats['total_score']} (#{total_score_rank})",
                inline=True
            )
            
            # Add footer
            embed.set_footer(text="Counting Bot Leaderboard")
            
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"Leaderboard displayed for guild {guild_id} by user {interaction.user.id}")
            
        except Exception as e:
            logger.error(f"Error displaying leaderboard: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while fetching the leaderboard.",
                ephemeral=True
            )
    
    def _get_rank(self, guild_id: int, rankings: List[Tuple[int, int]]) -> int:
        """Get the rank of a guild in a given ranking list."""
        for i, (guild, _) in enumerate(rankings, 1):
            if guild == guild_id:
                return i
        return len(rankings) + 1  # If not found, rank is last + 1

async def setup(bot: commands.Bot):
    """Set up the leaderboard commands cog."""
    await bot.add_cog(LeaderboardCommands(bot)) 