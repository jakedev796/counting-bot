"""
Database module for the Discord Counting Bot.
Handles all SQLite database operations with async support.
"""

import logging
import aiosqlite
import sqlite3
from typing import Optional, List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    """Database class for managing counting bot data."""
    
    def __init__(self, db_path: str):
        """Initialize database with path."""
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """Initialize database connection and create tables."""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create all necessary database tables."""
        async with self.connection.cursor() as cursor:
            # Guild settings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    counting_channel_id INTEGER,
                    current_count INTEGER DEFAULT 0,
                    high_score INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User stats table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    counts INTEGER DEFAULT 0,
                    score INTEGER DEFAULT 0,
                    last_count_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, user_id)
                )
            """)
            
            # Create indexes for better performance
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_stats_guild_user 
                ON user_stats(guild_id, user_id)
            """)
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_guild_settings_guild_id 
                ON guild_settings(guild_id)
            """)
            
            await self.connection.commit()
    
    async def initialize_guild(self, guild_id: int):
        """Initialize a new guild in the database."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT OR IGNORE INTO guild_settings (guild_id)
                    VALUES (?)
                """, (guild_id,))
                await self.connection.commit()
                logger.info(f"Initialized guild {guild_id} in database")
        except Exception as e:
            logger.error(f"Failed to initialize guild {guild_id}: {e}")
    
    async def remove_guild(self, guild_id: int):
        """Remove a guild and all its data from the database."""
        try:
            async with self.connection.cursor() as cursor:
                # Remove user stats for this guild
                await cursor.execute("""
                    DELETE FROM user_stats WHERE guild_id = ?
                """, (guild_id,))
                
                # Remove guild settings
                await cursor.execute("""
                    DELETE FROM guild_settings WHERE guild_id = ?
                """, (guild_id,))
                
                await self.connection.commit()
                logger.info(f"Removed guild {guild_id} from database")
        except Exception as e:
            logger.error(f"Failed to remove guild {guild_id}: {e}")
    
    async def set_counting_channel(self, guild_id: int, channel_id: int):
        """Set the counting channel for a guild."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT OR REPLACE INTO guild_settings 
                    (guild_id, counting_channel_id, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (guild_id, channel_id))
                await self.connection.commit()
                logger.info(f"Set counting channel {channel_id} for guild {guild_id}")
        except Exception as e:
            logger.error(f"Failed to set counting channel for guild {guild_id}: {e}")
    
    async def get_counting_channel(self, guild_id: int) -> Optional[int]:
        """Get the counting channel ID for a guild."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT counting_channel_id FROM guild_settings 
                    WHERE guild_id = ?
                """, (guild_id,))
                result = await cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get counting channel for guild {guild_id}: {e}")
            return None
    
    async def get_current_count(self, guild_id: int) -> int:
        """Get the current count for a guild."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT current_count FROM guild_settings 
                    WHERE guild_id = ?
                """, (guild_id,))
                result = await cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Failed to get current count for guild {guild_id}: {e}")
            return 0
    
    async def increment_count(self, guild_id: int, user_id: int) -> bool:
        """Increment the count for a guild and update user stats."""
        try:
            async with self.connection.cursor() as cursor:
                # Get current count
                current_count = await self.get_current_count(guild_id)
                new_count = current_count + 1
                
                # Update guild count
                await cursor.execute("""
                    UPDATE guild_settings 
                    SET current_count = ?, 
                        high_score = CASE WHEN ? > high_score THEN ? ELSE high_score END,
                        total_score = total_score + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE guild_id = ?
                """, (new_count, new_count, new_count, guild_id))
                
                # Update user stats
                await cursor.execute("""
                    INSERT OR REPLACE INTO user_stats 
                    (guild_id, user_id, counts, score, last_count_time, updated_at)
                    VALUES (?, ?, 
                        COALESCE((SELECT counts + 1 FROM user_stats WHERE guild_id = ? AND user_id = ?), 1),
                        COALESCE((SELECT score + 1 FROM user_stats WHERE guild_id = ? AND user_id = ?), 1),
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                """, (guild_id, user_id, guild_id, user_id, guild_id, user_id))
                
                await self.connection.commit()
                logger.info(f"Incremented count to {new_count} for guild {guild_id} by user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to increment count for guild {guild_id}: {e}")
            return False
    
    async def get_last_counter(self, guild_id: int) -> Optional[int]:
        """Get the user ID of the last person who counted in a guild."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT user_id FROM user_stats 
                    WHERE guild_id = ? 
                    ORDER BY last_count_time DESC 
                    LIMIT 1
                """, (guild_id,))
                result = await cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get last counter for guild {guild_id}: {e}")
            return None
    
    async def reset_count(self, guild_id: int):
        """Reset the count for a guild and clear user stats."""
        try:
            # Use synchronous SQLite to avoid async deadlocks
            with sqlite3.connect(self.db_path) as sync_connection:
                cursor = sync_connection.cursor()
                
                # Reset guild count
                cursor.execute("""
                    UPDATE guild_settings 
                    SET current_count = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE guild_id = ?
                """, (guild_id,))
                
                # Clear user stats for this guild
                cursor.execute("""
                    DELETE FROM user_stats WHERE guild_id = ?
                """, (guild_id,))
                
                sync_connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to reset count for guild {guild_id}: {e}")
            raise
    
    async def get_guild_stats(self, guild_id: int) -> Dict[str, Any]:
        """Get comprehensive stats for a guild."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT current_count, high_score, total_score
                    FROM guild_settings 
                    WHERE guild_id = ?
                """, (guild_id,))
                result = await cursor.fetchone()
                
                if result:
                    return {
                        'current_count': result[0],
                        'high_score': result[1],
                        'total_score': result[2]
                    }
                else:
                    return {
                        'current_count': 0,
                        'high_score': 0,
                        'total_score': 0
                    }
        except Exception as e:
            logger.error(f"Failed to get guild stats for guild {guild_id}: {e}")
            return {
                'current_count': 0,
                'high_score': 0,
                'total_score': 0
            }
    
    async def get_global_rankings(self) -> Dict[str, List[Tuple[int, int]]]:
        """Get global rankings for all stats."""
        try:
            async with self.connection.cursor() as cursor:
                # Get current count rankings
                await cursor.execute("""
                    SELECT guild_id, current_count 
                    FROM guild_settings 
                    ORDER BY current_count DESC
                """)
                current_count_rankings = await cursor.fetchall()
                
                # Get high score rankings
                await cursor.execute("""
                    SELECT guild_id, high_score 
                    FROM guild_settings 
                    ORDER BY high_score DESC
                """)
                high_score_rankings = await cursor.fetchall()
                
                # Get total score rankings
                await cursor.execute("""
                    SELECT guild_id, total_score 
                    FROM guild_settings 
                    ORDER BY total_score DESC
                """)
                total_score_rankings = await cursor.fetchall()
                
                return {
                    'current_count': current_count_rankings,
                    'high_score': high_score_rankings,
                    'total_score': total_score_rankings
                }
        except Exception as e:
            logger.error(f"Failed to get global rankings: {e}")
            return {
                'current_count': [],
                'high_score': [],
                'total_score': []
            }
    
    async def get_total_count(self) -> int:
        """Get the total count across all guilds."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT SUM(total_score) FROM guild_settings
                """)
                result = await cursor.fetchone()
                return result[0] if result and result[0] else 0
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            return 0
    
    async def close(self):
        """Close the database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed") 