# Shards of Eternity - Networking System

Comprehensive multiplayer networking system for Shards of Eternity.

## Architecture Overview

The networking system consists of three main components:

### 1. Protocol (`protocol.py`)
- **Message Types**: Defines all message types (auth, chat, movement, combat, etc.)
- **Serialization**: JSON-based message serialization/deserialization
- **Validation**: Pydantic-based message validation
- **Version Handling**: Protocol version compatibility checking

### 2. Master Server (`master_server.py`)
- **REST API**: HTTP endpoints for authentication, character management, world queries
- **WebSocket**: Real-time updates and bidirectional communication
- **Session Management**: Player session tracking and timeout handling
- **World State**: Centralized world state and shard ownership management

### 3. P2P Client (`peer.py`)
- **Server Connection**: Connect to master server for authentication
- **Real-time Communication**: WebSocket-based real-time updates
- **Player Discovery**: Track nearby players in the same area
- **Encryption**: Optional P2P message encryption
- **Event Handlers**: Extensible message handling system

## Quick Start

### Running the Master Server

```python
import asyncio
from network import MasterServer

async def main():
    server = MasterServer(host="0.0.0.0", port=8888)
    await server.start()

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

Or run directly:
```bash
python -m network.master_server
```

### Connecting as a Client

```python
import asyncio
from network import NetworkClient, MessageType

async def main():
    # Create and connect client
    client = NetworkClient()
    await client.connect("username", "password")

    # Register message handlers
    async def on_chat(message):
        print(f"[{message.channel}] {message.sender_name}: {message.content}")

    client.register_handler(MessageType.CHAT, on_chat)

    # Select character
    characters = await client.get_characters()
    if characters:
        await client.select_character(characters[0]["id"])

    # Send chat message
    await client.send_chat("Hello, world!")

    # Get world state
    world_state = await client.get_world_state()
    print(f"Current reality: {world_state['current_reality']}")

    # Keep running
    try:
        await asyncio.Event().wait()
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Message Types

### Authentication
- `AUTH_REQUEST` - Client authentication request
- `AUTH_RESPONSE` - Server authentication response
- `DISCONNECT` - Disconnect notification

### Character Management
- `CHARACTER_LIST` - Request/receive character list
- `CHARACTER_SELECT` - Select a character
- `CHARACTER_CREATE` - Create new character
- `CHARACTER_UPDATE` - Character state update
- `CHARACTER_DELETE` - Delete character

### Movement & Location
- `MOVE` - Movement update
- `LOCATION_UPDATE` - Location change notification
- `PLAYER_JOINED_AREA` - Player entered area
- `PLAYER_LEFT_AREA` - Player left area

### Chat & Communication
- `CHAT` - Global chat message
- `WHISPER` - Private message
- `PARTY_CHAT` - Party chat message
- `FACTION_CHAT` - Faction chat message
- `WORLD_ANNOUNCEMENT` - Server-wide announcement

### Party System
- `PARTY_CREATE` - Create new party
- `PARTY_INVITE` - Invite player to party
- `PARTY_ACCEPT` - Accept party invitation
- `PARTY_DECLINE` - Decline party invitation
- `PARTY_LEAVE` - Leave party
- `PARTY_KICK` - Kick member from party
- `PARTY_DISBAND` - Disband party
- `PARTY_UPDATE` - Party state update

### Combat
- `COMBAT_START` - Combat started
- `COMBAT_ACTION` - Player combat action
- `COMBAT_DAMAGE` - Damage dealt notification
- `COMBAT_HEAL` - Healing notification
- `COMBAT_END` - Combat ended
- `COMBAT_STATE` - Combat state synchronization

### World State
- `WORLD_STATE` - World state snapshot
- `SHARD_CAPTURED` - Crystal Shard captured
- `SHARD_STATUS` - Shard status update
- `REALITY_SHIFT` - Reality changed
- `AETHERFALL` - Aetherfall event

### Trading
- `TRADE_REQUEST` - Initiate trade
- `TRADE_ACCEPT` - Accept trade
- `TRADE_DECLINE` - Decline trade
- `TRADE_UPDATE` - Trade window update
- `TRADE_COMPLETE` - Trade completed

## API Endpoints

### Authentication
- `POST /api/auth/login` - Player login
- `POST /api/auth/register` - Player registration
- `POST /api/auth/logout` - Player logout

### Characters
- `GET /api/characters` - Get character list
- `POST /api/characters` - Create character
- `POST /api/characters/select` - Select character
- `DELETE /api/characters/{id}` - Delete character

### World State
- `GET /api/world/state` - Get world state
- `GET /api/world/shards` - Get shard status
- `GET /api/world/events` - Get recent events

### Party
- `GET /api/party/{id}` - Get party info
- `POST /api/party/create` - Create party
- `POST /api/party/invite` - Invite to party
- `POST /api/party/leave` - Leave party

### System
- `GET /api/status` - Server status

### WebSocket
- `WS /ws` - Real-time bidirectional communication

## Configuration

Configuration is loaded from `config/settings.py`:

```python
# Master Server
master_server_host = "localhost"
master_server_port = 8888
master_server_url = "http://localhost:8888"

# P2P
p2p_port = 9000
p2p_max_connections = 10
p2p_encryption = True  # Enable P2P encryption

# Security
encryption_key = "your-encryption-key"  # For P2P encryption
session_secret = "your-session-secret"
```

## Encryption

P2P encryption can be enabled/disabled via settings:

```python
# Enable encryption
client = NetworkClient()
client.encryption_enabled = True

# All WebSocket messages will be encrypted using Fernet (symmetric encryption)
```

Encryption uses:
- **Algorithm**: Fernet (AES-128 in CBC mode)
- **Key Derivation**: PBKDF2 with SHA-256
- **Iterations**: 100,000

## Message Handlers

Register custom handlers for specific message types:

```python
# Register async handler
async def on_shard_captured(message):
    print(f"Shard {message.shard_name} captured by {message.faction}!")
    # Trigger UI update, play sound, etc.

client.register_handler(MessageType.SHARD_CAPTURED, on_shard_captured)

# Register sync handler
def on_combat_damage(message):
    print(f"Damage dealt: {message.amount}")

client.register_handler(MessageType.COMBAT_DAMAGE, on_combat_damage)
```

## Player Discovery

Track nearby players in the same location:

```python
# Get nearby players
nearby = client.get_nearby_players(location_id=5)

for player in nearby:
    print(f"{player.character_name} (Level {player.level}, {player.faction})")
    print(f"  Position: {player.position}")
    print(f"  Last seen: {player.last_seen}")

# Nearby players are automatically updated when character updates are received
```

## Combat Synchronization

Send combat actions to server:

```python
# Attack action
await client.send_combat_action(
    combat_id="combat_123",
    action_type="attack",
    target_id=456
)

# Spell action
await client.send_combat_action(
    combat_id="combat_123",
    action_type="spell",
    target_id=456,
    ability_name="Fireball"
)

# Use item
await client.send_combat_action(
    combat_id="combat_123",
    action_type="item",
    item_id=789
)
```

## Movement Updates

Send position updates for smooth multiplayer movement:

```python
# Discrete location change
await client.send_move(
    to_location_id=5,
    from_location_id=4
)

# Smooth position update (for real-time movement)
await client.send_position_update(
    position={"x": 100.5, "y": 200.3, "z": 50.0},
    velocity={"x": 1.0, "y": 0.0, "z": 0.5}
)
```

## Error Handling

All network operations include proper error handling:

```python
try:
    characters = await client.get_characters()
except Exception as e:
    logger.error(f"Failed to get characters: {e}")
    # Handle error (retry, show error message, etc.)
```

Protocol-level errors are automatically converted to `ErrorMessage`:

```python
async def on_error(message):
    print(f"Error {message.error_code}: {message.error_message}")
    if message.details:
        print(f"Details: {message.details}")

client.register_handler(MessageType.ERROR, on_error)
```

## Session Management

Sessions are automatically managed:
- **Creation**: On successful login
- **Refresh**: On each API call or message
- **Timeout**: Default 3600 seconds (1 hour) of inactivity
- **Cleanup**: Automatic periodic cleanup of expired sessions

## Testing

### Test the Protocol

```python
from network import protocol, create_chat_message

# Create message
msg = create_chat_message(
    sender_id=1,
    sender_name="TestUser",
    content="Hello, world!"
)

# Serialize
json_str = protocol.serialize(msg)
print(json_str)

# Deserialize
parsed = protocol.deserialize(json_str)
assert parsed.content == "Hello, world!"
```

### Test Client-Server Communication

```bash
# Terminal 1: Run server
python -m network.master_server

# Terminal 2: Run client
python -m network.peer
```

## Integration with Game Logic

### Character Updates

```python
from characters import CharacterManager

manager = CharacterManager()

# When character changes, broadcast update
character = manager.load_character(character_id=1)
update_msg = create_character_update(
    character_id=character.id,
    character_name=character.name,
    location_id=character.location_id,
    health=character.health,
    max_health=character.max_health,
    level=character.level
)
await client._send_ws_message(update_msg)
```

### Shard Capture Events

```python
from world import ShardManager

shard_mgr = ShardManager()

# When shard is captured
if shard_mgr.capture_shard(shard_id=1, faction_name="Crimson Covenant"):
    # Broadcast to all players
    shard_msg = create_shard_captured_message(
        shard_id=1,
        shard_name="Phoenix Flame",
        character_id=player_id,
        character_name=player_name,
        faction="Crimson Covenant"
    )
    # Server broadcasts this to all connected clients
```

## Performance Considerations

- **WebSocket**: Used for real-time updates (low latency)
- **REST API**: Used for bulk data and one-time operations
- **Message Queuing**: Messages are queued and sent in batches
- **Connection Pooling**: HTTP sessions are reused
- **Compression**: Consider enabling WebSocket compression for large messages

## Security Best Practices

1. **Always use HTTPS/WSS in production**
2. **Enable P2P encryption** for sensitive data
3. **Validate all input** (done automatically via Pydantic)
4. **Implement rate limiting** on server endpoints
5. **Use strong session secrets**
6. **Hash passwords** (not implemented in demo - add bcrypt/argon2)
7. **Implement CSRF protection** for web clients

## Troubleshooting

### Connection Refused
- Check if master server is running
- Verify host/port settings
- Check firewall settings

### Authentication Failed
- Verify credentials
- Check session token validity
- Ensure player account exists

### WebSocket Disconnects
- Check network stability
- Implement reconnection logic
- Monitor server logs for errors

### Message Not Received
- Verify message handler is registered
- Check message type matches
- Ensure WebSocket is connected

## Future Enhancements

- [ ] Reconnection with session recovery
- [ ] Message compression for large payloads
- [ ] Voice chat integration
- [ ] Anti-cheat measures
- [ ] Load balancing for multiple server instances
- [ ] Database connection pooling
- [ ] Redis for session storage
- [ ] Metrics and monitoring
- [ ] Admin dashboard
- [ ] Rate limiting per user

## License

Part of Shards of Eternity game project.
