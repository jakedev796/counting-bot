# Discord Counting Bot

A Discord bot built with `discord.py` that enables a counting game in a specified channel. Users count upwards from 1, one number per message. The bot validates the sequence, reacts to correct/incorrect entries, and maintains per-server and global leaderboards.

## Features

- **Counting Game**: Users count upwards from 1 in a designated channel
- **Validation**: Bot validates correct sequence and prevents consecutive counting by same user
- **Reactions**: ✅ for correct counts, ❌ for incorrect counts
- **Admin Commands**: Set counting channel and reset count
- **Leaderboards**: Per-server stats with global rankings
- **Multi-Server Support**: Maintains separate counts for each server
- **Local Storage**: All data stored in SQLite database

## Requirements

- Python 3.10+
- Discord Bot Token
- Required permissions for the bot

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/jakedev796/better-counting.git
   cd better-counting
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   DATABASE_PATH=./counting_bot.db
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your Discord bot token.

2. **Create data directory**
   ```bash
   mkdir data
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## Bot Setup

1. **Create a Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section and create a bot
   - Copy the bot token to your `.env` file

2. **Invite the Bot to Your Server**
   - Go to OAuth2 > URL Generator
   - Select scopes: `bot` and `applications.commands`
   - Select permissions: `Send Messages`, `Add Reactions`, `Use Slash Commands`
   - Use the generated URL to invite the bot

3. **Set Required Intents**
   - In the Bot section, enable:
     - Message Content Intent
     - Server Members Intent

## Usage

### Admin Commands

- `/setcountingchannel [channel]` - Set the counting channel for the server
  - Requires "Manage Server" permission
  - Only one channel per server can be set

- `/resetcount [reason]` - Reset the count for the server
  - Requires "Manage Server" permission
  - Clears all user stats for the server
  - Optional reason parameter

### User Commands

- `/leaderboard` - View server statistics with global rankings
  - Shows Current Number, High Score, and Total Score
  - Displays global rank for each stat
  - Available to all users

### Counting Game Rules

1. **Valid Messages**: Only integer messages are processed
2. **Sequence**: Must count in correct order (1, 2, 3, ...)
3. **User Alternation**: No user can count twice in a row
4. **Reactions**: 
   - ✅ for correct counts
   - ❌ for incorrect counts or rule violations
5. **Rapid Counting**: Allowed as long as users alternate

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `DATABASE_PATH` | Path to SQLite database | `./counting_bot.db` |

### Database

The bot uses SQLite for data storage with the following tables:

- **guild_settings**: Server configuration and stats
- **user_stats**: Individual user statistics per server

## Development

### Project Structure

```
better-counting/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Main bot class
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── admin.py         # Admin slash commands
│   │   └── leaderboard.py   # Leaderboard command
│   ├── cogs/
│   │   ├── __init__.py
│   │   └── counting.py      # Counting game logic
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py      # Database operations
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Utility functions
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── .env.example            # Environment template
└── README.md               # This file
```

### Adding New Features

1. **Commands**: Add new slash commands in `bot/commands/`
2. **Cogs**: Add new functionality in `bot/cogs/`
3. **Database**: Extend `bot/db/database.py` for new data needs
4. **Utilities**: Add helper functions in `bot/utils/helpers.py`

## Troubleshooting

### Common Issues

1. **Bot not responding to commands**
   - Check if bot has required permissions
   - Verify slash commands are synced
   - Check bot token is correct

2. **Database errors**
   - Ensure write permissions for database directory
   - Check database path in environment variables

3. **Counting not working**
   - Verify counting channel is set with `/setcountingchannel`
   - Check bot has permission to add reactions

### Logs

The bot logs all activities to console. Check logs for:
- Command usage
- Counting events
- Error messages
- Database operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue in the repository 