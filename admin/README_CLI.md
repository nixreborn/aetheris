# Shards of Eternity - Admin CLI

## Overview

The Admin CLI provides comprehensive command-line tools for managing the Shards of Eternity game server, world state, players, and database.

## Installation

The CLI is already included in your project. All required dependencies are in `requirements.txt`:

```bash
pip install click rich
```

## Usage

```bash
# General format
python -m admin.cli <command> [options]

# Get help
python -m admin.cli --help

# Get help for specific command
python -m admin.cli <command> --help
```

## Available Commands

### Server Management

#### start-server
Start the master server
```bash
python -m admin.cli start-server [--host HOST] [--port PORT] [--background]
```

#### stop-server
Stop the running server
```bash
python -m admin.cli stop-server [--force]
```

#### server-status
Check server status and health
```bash
python -m admin.cli server-status
```

### World Management

#### trigger-aetherfall
Manually trigger world reset (Aetherfall)
```bash
python -m admin.cli trigger-aetherfall [--faction FACTION_NAME]
```

#### set-reality
Change current reality state
```bash
python -m admin.cli set-reality <REALITY_TYPE>
# Available types: "Blood Realm", "Aether Storm", "Iron Age", "Twilight Dominion", "Shadow World", "Radiant Era", "Neutral"
```

#### reset-world
Reset world to neutral state
```bash
python -m admin.cli reset-world
```

### Player Management

#### list-players
Show all registered players
```bash
python -m admin.cli list-players [--faction FACTION] [--limit N]
```

#### ban-player
Ban a player by name
```bash
python -m admin.cli ban-player <NAME>
```

#### unban-player
Unban a player
```bash
python -m admin.cli unban-player <NAME>
```

#### delete-character
Delete a character permanently
```bash
python -m admin.cli delete-character <NAME>
```

### Shard Management

#### list-shards
Show all Crystal Shards and their ownership
```bash
python -m admin.cli list-shards [--verbose]
```

#### assign-shard
Manually assign a shard to a faction
```bash
python -m admin.cli assign-shard <SHARD_ID> <FACTION>
# Example: python -m admin.cli assign-shard 1 "Crimson Covenant"
```

#### reset-shards
Reset all shards to uncaptured state
```bash
python -m admin.cli reset-shards
```

### Monitoring

#### view-logs
Tail server logs
```bash
python -m admin.cli view-logs [--lines N] [--follow]
```

#### world-events
Show recent world events
```bash
python -m admin.cli world-events [--limit N]
```

#### player-stats
Show player statistics
```bash
python -m admin.cli player-stats
```

### Database

#### backup-db
Create database backup
```bash
python -m admin.cli backup-db [--output PATH]
```

#### restore-db
Restore database from backup
```bash
python -m admin.cli restore-db <FILE>
```

#### export-data
Export game data to JSON
```bash
python -m admin.cli export-data [--output PATH] [--pretty]
```

#### init-db
Initialize the database
```bash
python -m admin.cli init-db
```

#### reset-db
Reset the database (WARNING: deletes all data)
```bash
python -m admin.cli reset-db
```

### Utility

#### version
Show version information
```bash
python -m admin.cli version
```

## Examples

### Complete Workflow Example

```bash
# 1. Initialize database
python -m admin.cli init-db

# 2. Start server in background
python -m admin.cli start-server --background

# 3. Check server status
python -m admin.cli server-status

# 4. List all shards
python -m admin.cli list-shards --verbose

# 5. Assign a shard to a faction
python -m admin.cli assign-shard 1 "Crimson Covenant"

# 6. View recent world events
python -m admin.cli world-events --limit 10

# 7. List players
python -m admin.cli list-players --limit 20

# 8. Create backup
python -m admin.cli backup-db

# 9. Trigger Aetherfall
python -m admin.cli trigger-aetherfall --faction "Aether Seekers"

# 10. Export data
python -m admin.cli export-data --pretty

# 11. Stop server
python -m admin.cli stop-server
```

### Monitoring Workflow

```bash
# Check status
python -m admin.cli server-status

# View logs (last 100 lines)
python -m admin.cli view-logs --lines 100

# Follow logs in real-time
python -m admin.cli view-logs --follow

# View player statistics
python -m admin.cli player-stats

# View world events
python -m admin.cli world-events --limit 50
```

### World Management Workflow

```bash
# Check current shards
python -m admin.cli list-shards

# Change reality
python -m admin.cli set-reality "Shadow World"

# Trigger manual Aetherfall
python -m admin.cli trigger-aetherfall

# Reset world to neutral
python -m admin.cli reset-world

# Reset all shards
python -m admin.cli reset-shards
```

## Features

### Colorful Output
The CLI uses Rich library for beautiful, colorful terminal output:
- ✓ Green checkmarks for success
- ✗ Red X for errors
- ℹ Blue icons for information
- ⚠ Yellow warnings for warnings

### Confirmation Prompts
Destructive actions require confirmation:
- Server shutdown
- Database resets
- World resets
- Character deletion
- Shard resets

### Progress Indicators
Long-running operations show progress:
- Aetherfall triggers
- Database backups
- Data exports

### Error Handling
Comprehensive error handling with clear messages:
- File not found errors
- Database connection issues
- Invalid input validation
- Process management errors

## Technical Details

### Architecture
- **Framework**: Click for CLI, Rich for output
- **Database**: SQLAlchemy ORM
- **Server Process**: subprocess management with PID tracking
- **Configuration**: Pydantic settings from environment

### File Locations
- **PID File**: `./data/server.pid`
- **Logs**: `./logs/server.log`
- **Backups**: `./data/backups/`
- **Database**: As configured in settings (default: `./shards_of_eternity.db`)

### Exit Codes
- `0`: Success
- `1`: Error occurred
- Ctrl+C: Graceful shutdown (code 0)

## Troubleshooting

### Server won't start
```bash
# Check if already running
python -m admin.cli server-status

# Force stop if hung
python -m admin.cli stop-server --force

# Check logs
python -m admin.cli view-logs --lines 50
```

### Database errors
```bash
# Reinitialize database
python -m admin.cli reset-db
python -m admin.cli init-db

# Or restore from backup
python -m admin.cli restore-db ./data/backups/backup_YYYYMMDD_HHMMSS.db
```

### Import errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Development

To add new commands:

1. Add new function with `@cli.command()` decorator
2. Use Click options/arguments for parameters
3. Use Rich console for output
4. Follow existing patterns for confirmation and error handling

Example:
```python
@cli.command()
@click.argument("param")
@click.option("--flag", is_flag=True)
def my_command(param: str, flag: bool):
    \"\"\"My command description.\"\"\"
    display_header("My Command")

    try:
        # Command logic here
        success("Operation completed")
    except Exception as e:
        error(f"Operation failed: {e}")
        sys.exit(1)
```

## Support

For issues or questions:
1. Check logs: `python -m admin.cli view-logs`
2. Check server status: `python -m admin.cli server-status`
3. Review this documentation
4. Check the main README.md

## License

Part of Shards of Eternity game project.
