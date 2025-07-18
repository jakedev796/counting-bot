"""
Helper utilities for the Discord Counting Bot.
Contains common utility functions used across the bot.
"""

import logging
from typing import Optional

import discord

logger = logging.getLogger(__name__)

def check_permissions(member: discord.Member, permission: str) -> bool:
    """
    Check if a member has a specific permission.
    
    Args:
        member: The Discord member to check
        permission: The permission to check for
        
    Returns:
        True if the member has the permission, False otherwise
    """
    return getattr(member.guild_permissions, permission, False)

def format_number(number: int) -> str:
    """
    Format a number with commas for better readability.
    
    Args:
        number: The number to format
        
    Returns:
        Formatted number string
    """
    return f"{number:,}"

def safe_int_parse(value: str) -> Optional[int]:
    """
    Safely parse a string to an integer.
    
    Args:
        value: The string to parse
        
    Returns:
        The parsed integer or None if parsing fails
    """
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None

def log_command_usage(command_name: str, user_id: int, guild_id: int, **kwargs):
    """
    Log command usage for debugging and analytics.
    
    Args:
        command_name: Name of the command used
        user_id: ID of the user who used the command
        guild_id: ID of the guild where the command was used
        **kwargs: Additional context to log
    """
    context = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"Command used: {command_name} by user {user_id} in guild {guild_id} {context}")

def log_error(error: Exception, context: str = ""):
    """
    Log an error with context for debugging.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    logger.error(f"Error in {context}: {error}", exc_info=True) 