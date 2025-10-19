# Shards of Eternity - Networking System Guide

Comprehensive guide to the multiplayer networking system in Shards of Eternity.

## Overview

The networking system provides a complete multiplayer infrastructure with:

- **Client-Server Architecture**: Centralized master server for authentication and world state
- **Real-time Communication**: WebSocket-based bidirectional messaging
- **P2P Support**: Player-to-player communication for nearby interactions
- **Encryption**: Optional message encryption for secure communication
- **Protocol Versioning**: Support for protocol compatibility checking

## Architecture

```
┌─────────────────┐
│  Master Server  │  ← Central authority
│  (REST + WS)    │     - Authentication
└────────┬────────┘     - World state
         │              - Session management
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│Client│  │Client│  ← P2P clients
│  A   │◄─┤  B   │     - Character control
└──────┘  └──────┘     - Real-time updates
                        - Chat/party
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `.env` file or `config/settings.py`:

```env
# Master Server
MASTER_SERVER_HOST=localhost
MASTER_SERVER_PORT=8888
MASTER_SERVER_URL=http://localhost:8888

# P2P
P2P_PORT=9000
P2P_MAX_CONNECTIONS=10
P2P_ENCRYPTION=true

# Security
ENCRYPTION_KEY=your-secret-key
SESSION_SECRET=your-session-secret
```

### 3. Start the Master Server

```bash
python run_server.py
```

Or with custom settings:

```bash
python run_server.py --host 0.0.0.0 --port 9000 --log-level DEBUG
```

### 4. Connect a Client

```python
import asyncio
from network import NetworkClient

async def main():
    client = NetworkClient()

    # Connect and authenticate
    await client.connect("username", "password")

    # Select character
    characters = await client.get_characters()
    if characters:
        await client.select_character(characters[0]["id"])

    # Send chat message
    await client.send_chat("Hello, world!")

    # Keep connected
    try:
        await asyncio.Event().wait()
    finally:
        await client.disconnect()

asyncio.run(main())
```

## File Structure

```
network/
├── __init__.py              # Package exports
├── protocol.py              # Message protocol definitions
├── master_server.py         # Master server implementation
├── peer.py                  # P2P client implementation
├── example_usage.py         # Usage examples
├── test_networking.py       # Unit tests
└── README.md               # Detailed documentation
```

## Core Components

### 1. Protocol (`protocol.py`)

Defines the communication protocol:

**Message Types:**
- Authentication (AUTH_REQUEST, AUTH_RESPONSE)
- Chat (CHAT, WHISPER, PARTY_CHAT, FACTION_CHAT)
- Movement (MOVE, LOCATION_UPDATE)
- Combat (COMBAT_START, COMBAT_ACTION, COMBAT_STATE)
- World State (WORLD_STATE, SHARD_CAPTURED, REALITY_SHIFT)
- Party (PARTY_INVITE, PARTY_UPDATE, PARTY_LEAVE)

**Features:**
- JSON serialization/deserialization
- Pydantic-based validation
- Protocol version checking
- Message priority system

**Example:**

```python
from network import create_chat_message, protocol

# Create message
msg = create_chat_message(
    sender_id=1,
    sender_name="Hero",
    content="Hello!",
    channel="global"
)

# Serialize
json_str = protocol.serialize(msg)

# Deserialize
msg2 = protocol.deserialize(json_str)
```

### 2. Master Server (`master_server.py`)

Central server for authentication and coordination:

**REST API Endpoints:**
- `POST /api/auth/login` - Player login
- `POST /api/auth/logout` - Player logout
- `GET /api/characters` - Get character list
- `POST /api/characters/select` - Select character
- `GET /api/world/state` - Get world state
- `GET /api/world/shards` - Get shard status
- `GET /api/party/{id}` - Get party info
- `POST /api/party/create` - Create party

**WebSocket Endpoint:**
- `WS /ws` - Real-time bidirectional communication

**Features:**
- Session management with timeout
- WebSocket message broadcasting
- Background cleanup tasks
- CORS support

**Example:**

```python
from network import MasterServer

server = MasterServer(host="0.0.0.0", port=8888)
await server.start()
```

### 3. P2P Client (`peer.py`)

Client-side networking:

**Features:**
- Master server connection
- WebSocket real-time updates
- Message handler registration
- Player discovery
- Optional encryption
- Combat synchronization

**Example:**

```python
from network import NetworkClient, MessageType

client = NetworkClient()
await client.connect("username", "password")

# Register handler
async def on_chat(message):
    print(f"{message.sender_name}: {message.content}")

client.register_handler(MessageType.CHAT, on_chat)

# Send message
await client.send_chat("Hello!")
```

## Common Use Cases

### Chat System

```python
# Global chat
await client.send_chat("Hello everyone!", channel="global")

# Party chat
await client.send_party_chat("Ready for the raid?")

# Whisper
await client.send_whisper(recipient_id=123, message="Secret message")

# Handle incoming messages
async def on_chat(message):
    if message.channel == "whisper":
        print(f"[Whisper from {message.sender_name}] {message.content}")
    else:
        print(f"[{message.channel}] {message.sender_name}: {message.content}")

client.register_handler(MessageType.CHAT, on_chat)
```

### Character Movement

```python
# Discrete location change
await client.send_move(
    to_location_id=5,
    from_location_id=4
)

# Continuous position update
await client.send_position_update(
    position={"x": 100.5, "y": 200.3, "z": 50.0},
    velocity={"x": 1.0, "y": 0.0, "z": 0.5}
)
```

### Party Management

```python
# Create party
party_id = await client.create_party("Dragon Slayers")

# Invite player
await client.invite_to_party(party_id, invitee_id=456)

# Send party chat
await client.send_party_chat("Let's go!")
```

### Combat Synchronization

```python
# Attack
await client.send_combat_action(
    combat_id="combat_001",
    action_type="attack",
    target_id=999
)

# Cast spell
await client.send_combat_action(
    combat_id="combat_001",
    action_type="spell",
    target_id=999,
    ability_name="Fireball"
)

# Use item
await client.send_combat_action(
    combat_id="combat_001",
    action_type="item",
    item_id=123
)

# Handle combat updates
async def on_combat_state(message):
    print(f"Turn {message.turn_number}")
    print(f"Active: {message.active_character_id}")
    for entry in message.combat_log:
        print(f"  {entry}")

client.register_handler(MessageType.COMBAT_STATE, on_combat_state)
```

### World State Queries

```python
# Get world state
world_state = await client.get_world_state()
print(f"Reality: {world_state['current_reality']}")
print(f"Stability: {world_state['reality_stability']}%")

# Get shard status
shards = await client.get_shard_status()
for shard in shards:
    print(f"{shard['name']} - Owner: {shard['owning_faction']}")

# Handle shard captures
async def on_shard_captured(message):
    print(f"SHARD CAPTURED: {message.shard_name}")
    print(f"  By: {message.captured_by_character_name}")
    print(f"  Faction: {message.faction}")
    # Trigger UI notification, sound effect, etc.

client.register_handler(MessageType.SHARD_CAPTURED, on_shard_captured)
```

### Nearby Players

```python
# Get players in same location
nearby = client.get_nearby_players(location_id=5)

for player in nearby:
    print(f"{player.character_name} (Lvl {player.level})")
    print(f"  Faction: {player.faction}")
    print(f"  Position: {player.position}")
    print(f"  Last seen: {player.last_seen}")
```

## Encryption

Enable P2P message encryption:

```python
# In settings
P2P_ENCRYPTION=true
ENCRYPTION_KEY=your-secret-key

# Client automatically encrypts/decrypts messages
client = NetworkClient()
client.encryption_enabled = True
```

**Encryption Details:**
- Algorithm: Fernet (AES-128-CBC + HMAC)
- Key Derivation: PBKDF2 with SHA-256
- Salt: Application-specific
- Iterations: 100,000

## Testing

### Run Unit Tests

```bash
pytest network/test_networking.py -v
```

### Run Examples

```bash
python network/example_usage.py
```

Select from menu:
1. Simple Client Connection
2. Client with Message Handlers
3. Multiple Clients Chatting
4. Character Management
5. World State Queries
6. Party System
7. Combat Simulation
8. Run Master Server

### Manual Testing

Terminal 1 - Start server:
```bash
python run_server.py
```

Terminal 2 - Run client:
```bash
python -c "
import asyncio
from network import create_client_and_connect

async def main():
    client = await create_client_and_connect('test', 'pass')
    await client.send_chat('Hello!')
    await asyncio.sleep(5)
    await client.disconnect()

asyncio.run(main())
"
```

## Performance Tips

1. **Use WebSocket for real-time updates** - Lower latency than REST API
2. **Batch position updates** - Don't send every frame, use throttling
3. **Enable compression** - For large world state updates
4. **Connection pooling** - Reuse HTTP sessions
5. **Message prioritization** - Critical messages (combat) get priority

## Security Considerations

1. **Authentication**
   - Implement proper password hashing (bcrypt/argon2)
   - Use secure session tokens
   - Implement rate limiting

2. **Validation**
   - All input validated via Pydantic
   - Sanitize user content
   - Verify permissions

3. **Encryption**
   - Use HTTPS/WSS in production
   - Enable P2P encryption for sensitive data
   - Rotate encryption keys regularly

4. **Anti-Cheat**
   - Validate all game actions server-side
   - Detect impossible movements
   - Monitor for spam/abuse

## Error Handling

All operations include comprehensive error handling:

```python
try:
    await client.send_chat("Hello")
except Exception as e:
    logger.error(f"Failed to send chat: {e}")
    # Retry, show error to user, etc.

# Handle protocol errors
async def on_error(message):
    print(f"Error: {message.error_code}")
    print(f"Message: {message.error_message}")

client.register_handler(MessageType.ERROR, on_error)
```

## Integration with Game Systems

### Character System

```python
from characters import CharacterManager
from network import create_character_update

manager = CharacterManager()
character = manager.load_character(1)

# Broadcast character update
update = create_character_update(
    character_id=character.id,
    character_name=character.name,
    health=character.health,
    max_health=character.max_health,
    location_id=character.location_id,
    level=character.level
)
await client._send_ws_message(update)
```

### Combat System

```python
from combat import CombatSystem

combat = CombatSystem()

# Send combat actions
async def player_turn(combat_id, action):
    await client.send_combat_action(
        combat_id=combat_id,
        action_type=action["type"],
        target_id=action.get("target_id"),
        ability_name=action.get("ability")
    )

# Receive combat state
async def on_combat_state(message):
    combat.update_state(message.participants)
    combat.display_log(message.combat_log)

client.register_handler(MessageType.COMBAT_STATE, on_combat_state)
```

### World System

```python
from world import ShardManager

shard_mgr = ShardManager()

# Broadcast shard capture
if shard_mgr.capture_shard(1, "Crimson Covenant"):
    msg = create_shard_captured_message(
        shard_id=1,
        shard_name="Phoenix Flame",
        character_id=player_id,
        character_name=player_name,
        faction="Crimson Covenant"
    )
    # Server broadcasts to all clients
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to server
**Solutions**:
- Verify server is running: `netstat -an | grep 8888`
- Check firewall settings
- Verify host/port in settings
- Check network connectivity

### Authentication Failures

**Problem**: Login fails
**Solutions**:
- Verify credentials
- Check session token validity
- Review server logs for errors
- Clear old sessions

### Message Not Received

**Problem**: Messages not arriving
**Solutions**:
- Verify WebSocket connection is active
- Check message handler is registered
- Verify message type matches
- Check encryption settings match

### High Latency

**Problem**: Slow response times
**Solutions**:
- Use WebSocket instead of REST API
- Enable message compression
- Optimize database queries
- Consider server hardware upgrade

## Advanced Topics

### Custom Message Types

Add new message types to `protocol.py`:

```python
class CustomMessage(BaseMessage):
    type: MessageType = MessageType.CUSTOM
    custom_field: str
    custom_data: Dict[str, Any]

# Register in MESSAGE_MODELS
MESSAGE_MODELS[MessageType.CUSTOM] = CustomMessage
```

### Load Balancing

For multiple server instances:

```python
# Use Redis for session storage
# Implement sticky sessions
# Share world state across instances
```

### Database Optimization

```python
# Use connection pooling
# Implement caching layer
# Optimize queries
# Add indexes
```

## Resources

- **API Documentation**: `network/README.md`
- **Examples**: `network/example_usage.py`
- **Tests**: `network/test_networking.py`
- **Protocol Spec**: `network/protocol.py`

## Support

For issues or questions:
1. Check the documentation
2. Review example code
3. Run the test suite
4. Check server logs

## License

Part of the Shards of Eternity game project.
