<div align="center">
  <img src="countingBotIcon.png" alt="Counting Bot Icon" width="200" height="200">
  
  # Discord Counting Bot
  
  A Discord bot built with `discord.py` that enables a counting game in a specified channel. Users count upwards from 1, one number per message. The bot validates the sequence, reacts to correct/incorrect entries, and maintains per-server and global leaderboards.
  
  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
</div>

---

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Bot Setup](#bot-setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Support](#support)

## ✨ Features

- 🎯 **Counting Game**: Users count upwards from 1 in a designated channel
- ✅ **Smart Validation**: Bot validates correct sequence and prevents consecutive counting by same user
- 🎨 **Custom Reactions**: Support for custom emotes or default ✅/❌ reactions
- ⚙️ **Admin Commands**: Set counting channel and reset count with permission checks
- 📊 **Leaderboards**: Per-server stats with global rankings
- 🌐 **Multi-Server Support**: Maintains separate counts for each server
- 💾 **Local Storage**: All data stored in SQLite database with async support
- 🔄 **Flexible Input**: Accepts numbers anywhere in messages (e.g., "5 this is a test")
- 📈 **Live Presence**: Custom status showing total count across all servers
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose

## 📋 Requirements

- **Python** 3.10+
- **Discord Bot Token** (from Discord Developer Portal)
- **Required Bot Permissions**:
  - Send Messages
  - Add Reactions
  - Use Slash Commands
  - Read Message History

## 🤖 Public Bot

**Ready to use immediately!** Invite the public bot to your server:

[![Invite Bot](https://img.shields.io/badge/Invite%20Bot-Discord-blue.svg)](https://discord.com/oauth2/authorize?client_id=1395776535629266985&permissions=2147551296&integration_type=0&scope=bot)

**Direct Link:** https://discord.com/oauth2/authorize?client_id=1395776535629266985&permissions=8&integration_type=0&scope=bot+applications.commands

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/jakedev796/counting-bot.git
cd counting-bot

# Set up environment
cp .env.example .env
# Edit .env with your Discord bot token

# Run with Docker (recommended)
docker-compose up -d

# Or run locally
pip install -r requirements.txt
python main.py
```

## 📦 Installation

### Local Development

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
| `SUCCESS_EMOTE` | Custom emote for correct counts | `✅` |
| `ERROR_EMOTE` | Custom emote for incorrect counts | `❌` |

### Database

The bot uses SQLite for data storage with the following tables:

- **guild_settings**: Server configuration and stats
- **user_stats**: Individual user statistics per server

## Development

### Project Structure

```
counting-bot/
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

## 🤝 Contributing

Always welcoming contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### 🐛 Bug Reports

Found a bug? Please [open an issue](https://github.com/jakedev796/counting-bot/issues) with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Bot logs (if applicable)

### 💡 Feature Requests

Have an idea? I'd love to hear it! [Open an issue](https://github.com/jakedev796/counting-bot/issues) with your suggestion.

## 🆘 Support

Need help? Here are your options:

### 📖 Self-Help
1. Check the [troubleshooting section](#troubleshooting) above
2. Review the bot logs for error messages
3. Check the [Discord.py documentation](https://discordpy.readthedocs.io/)

### 🐛 Get Help
- **GitHub Issues**: [Open an issue](https://github.com/jakedev796/counting-bot/issues) for bugs or feature requests

---

<div align="center">
  <p>Made with ❤️ by the Jake</p>
  <p>If this project helped you, consider giving it a ⭐!</p>
</div> 
