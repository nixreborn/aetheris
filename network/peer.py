"""
P2P client networking for Shards of Eternity.

Handles client-side networking including:
- Connection to master server
- Player discovery and P2P connections
- Real-time position updates
- Party chat and communication
- Combat synchronization
- Optional encryption
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64

from config.settings import get_settings
from network.protocol import (
    protocol, ProtocolError, MessageType, BaseMessage,
    AuthRequest, AuthResponse, ChatMessage, MoveMessage,
    CharacterUpdateMessage, PartyInviteMessage, CombatActionMessage,
    create_auth_request, create_chat_message, create_move_message,
    create_character_update
)

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================================
# Encryption Support
# ============================================================================

class EncryptionHandler:
    """Handles message encryption/decryption for P2P communication."""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption handler.

        Args:
            encryption_key: Encryption key. If None, generates a new key.
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            # Generate key from settings or create new
            if settings.encryption_key:
                self.key = self._derive_key(settings.encryption_key)
            else:
                self.key = Fernet.generate_key()

        self.cipher = Fernet(self.key)

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password."""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'shards_of_eternity_salt',  # In production, use random salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, message: str) -> str:
        """Encrypt a message."""
        try:
            encrypted = self.cipher.encrypt(message.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt(self, encrypted_message: str) -> str:
        """Decrypt a message."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_message.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


# ============================================================================
# Nearby Player
# ============================================================================

@dataclass
class NearbyPlayer:
    """Represents a nearby player for P2P communication."""
    player_id: int
    character_id: int
    character_name: str
    location_id: int
    position: Optional[Dict[str, float]] = None
    last_seen: datetime = None
    faction: Optional[str] = None
    level: Optional[int] = None

    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = datetime.utcnow()

    def update_position(self, position: Dict[str, float]):
        """Update player position."""
        self.position = position
        self.last_seen = datetime.utcnow()


# ============================================================================
# Network Client (P2P Peer)
# ============================================================================

class NetworkClient:
    """
    P2P network client for Shards of Eternity.

    Handles connections to master server and P2P communication with other players.
    """

    def __init__(self, master_server_url: Optional[str] = None):
        """
        Initialize network client.

        Args:
            master_server_url: Master server URL. Defaults to settings.
        """
        self.master_server_url = master_server_url or settings.master_server_url
        self.session_token: Optional[str] = None
        self.player_id: Optional[int] = None
        self.character_id: Optional[int] = None
        self.username: Optional[str] = None

        # HTTP session for REST API calls
        self.http_session: Optional[aiohttp.ClientSession] = None

        # WebSocket for real-time updates
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.ws_task: Optional[asyncio.Task] = None

        # Nearby players
        self.nearby_players: Dict[int, NearbyPlayer] = {}

        # Encryption
        self.encryption_enabled = settings.p2p_encryption
        self.encryption_handler: Optional[EncryptionHandler] = None
        if self.encryption_enabled:
            self.encryption_handler = EncryptionHandler()

        # Message handlers
        self.message_handlers: Dict[MessageType, List[Callable]] = {}

        # Connection state
        self.connected = False
        self.authenticated = False

    # ========================================================================
    # Connection Management
    # ========================================================================

    async def connect(self, username: str, password: str) -> bool:
        """
        Connect to master server and authenticate.

        Args:
            username: Player username
            password: Player password

        Returns:
            True if connection successful
        """
        try:
            # Create HTTP session
            self.http_session = aiohttp.ClientSession()

            # Authenticate
            auth_result = await self._authenticate(username, password)
            if not auth_result:
                logger.error("Authentication failed")
                return False

            self.username = username
            self.connected = True
            self.authenticated = True

            logger.info(f"Connected to master server as {username}")

            # Start WebSocket connection for real-time updates
            await self._connect_websocket()

            return True

        except Exception as e:
            logger.error(f"Connection error: {e}")
            await self.disconnect()
            return False

    async def disconnect(self):
        """Disconnect from master server."""
        logger.info("Disconnecting from master server")

        # Close WebSocket
        if self.ws_task:
            self.ws_task.cancel()
            self.ws_task = None

        if self.ws and not self.ws.closed:
            await self.ws.close()
            self.ws = None

        # Logout
        if self.session_token and self.http_session:
            try:
                await self.http_session.post(
                    f"{self.master_server_url}/api/auth/logout",
                    json={"session_token": self.session_token}
                )
            except Exception as e:
                logger.error(f"Logout error: {e}")

        # Close HTTP session
        if self.http_session:
            await self.http_session.close()
            self.http_session = None

        self.connected = False
        self.authenticated = False
        self.session_token = None

        logger.info("Disconnected from master server")

    async def _authenticate(self, username: str, password: str) -> bool:
        """Authenticate with master server."""
        try:
            async with self.http_session.post(
                f"{self.master_server_url}/api/auth/login",
                json={"username": username, "password": password}
            ) as response:
                data = await response.json()

                if data.get("success"):
                    self.session_token = data["session_token"]
                    self.player_id = data["player_id"]
                    logger.info(f"Authenticated as {username} (ID: {self.player_id})")
                    return True
                else:
                    logger.error(f"Authentication failed: {data.get('message')}")
                    return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    async def _connect_websocket(self):
        """Connect WebSocket for real-time updates."""
        try:
            self.ws = await self.http_session.ws_connect(
                f"{self.master_server_url.replace('http', 'ws')}/ws"
            )

            # Send authentication message
            auth_msg = create_auth_request(
                username=self.username,
                password="",  # Using session token
                session_token=self.session_token
            )
            await self.ws.send_str(protocol.serialize(auth_msg))

            # Start message receiving task
            self.ws_task = asyncio.create_task(self._ws_receive_loop())

            logger.info("WebSocket connected")

        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")

    async def _ws_receive_loop(self):
        """Receive and process WebSocket messages."""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.ws.exception()}")
                    break

        except asyncio.CancelledError:
            logger.info("WebSocket receive loop cancelled")
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")

    # ========================================================================
    # Character Management
    # ========================================================================

    async def get_characters(self) -> List[Dict]:
        """Get list of characters for this player."""
        if not self.authenticated:
            logger.error("Not authenticated")
            return []

        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            async with self.http_session.get(
                f"{self.master_server_url}/api/characters",
                headers=headers
            ) as response:
                data = await response.json()
                return data.get("characters", [])

        except Exception as e:
            logger.error(f"Get characters error: {e}")
            return []

    async def select_character(self, character_id: int) -> bool:
        """Select a character for this session."""
        if not self.authenticated:
            logger.error("Not authenticated")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            async with self.http_session.post(
                f"{self.master_server_url}/api/characters/select",
                headers=headers,
                json={"character_id": character_id}
            ) as response:
                data = await response.json()

                if data.get("success"):
                    self.character_id = character_id
                    logger.info(f"Selected character ID: {character_id}")
                    return True
                else:
                    logger.error(f"Character selection failed: {data.get('error')}")
                    return False

        except Exception as e:
            logger.error(f"Select character error: {e}")
            return False

    # ========================================================================
    # Movement & Position Updates
    # ========================================================================

    async def send_move(self, to_location_id: int, from_location_id: Optional[int] = None,
                       position: Optional[Dict[str, float]] = None):
        """
        Send movement update to server.

        Args:
            to_location_id: Destination location ID
            from_location_id: Source location ID
            position: Optional position coordinates (x, y, z)
        """
        if not self.character_id:
            logger.error("No character selected")
            return

        try:
            move_msg = create_move_message(
                character_id=self.character_id,
                to_location_id=to_location_id,
                from_location_id=from_location_id,
                position=position
            )

            await self._send_ws_message(move_msg)
            logger.debug(f"Sent move to location {to_location_id}")

        except Exception as e:
            logger.error(f"Send move error: {e}")

    async def send_position_update(self, position: Dict[str, float], velocity: Optional[Dict[str, float]] = None):
        """
        Send position update (for smooth movement).

        Args:
            position: Current position (x, y, z)
            velocity: Optional velocity vector
        """
        if not self.character_id:
            return

        try:
            move_msg = MoveMessage(
                character_id=self.character_id,
                to_location_id=0,  # Same location
                position=position,
                velocity=velocity
            )

            await self._send_ws_message(move_msg)

        except Exception as e:
            logger.error(f"Send position update error: {e}")

    # ========================================================================
    # Chat & Communication
    # ========================================================================

    async def send_chat(self, message: str, channel: str = "global", recipient_id: Optional[int] = None):
        """
        Send a chat message.

        Args:
            message: Chat message content
            channel: Chat channel (global, party, faction, whisper)
            recipient_id: Recipient ID for whispers
        """
        if not self.character_id or not self.username:
            logger.error("Not properly connected")
            return

        try:
            chat_msg = create_chat_message(
                sender_id=self.character_id,
                sender_name=self.username,
                content=message,
                channel=channel,
                recipient_id=recipient_id
            )

            await self._send_ws_message(chat_msg)
            logger.debug(f"Sent chat message to {channel}")

        except Exception as e:
            logger.error(f"Send chat error: {e}")

    async def send_party_chat(self, message: str):
        """Send a message to party chat."""
        await self.send_chat(message, channel="party")

    async def send_whisper(self, recipient_id: int, message: str):
        """Send a whisper to another player."""
        await self.send_chat(message, channel="whisper", recipient_id=recipient_id)

    # ========================================================================
    # Party Management
    # ========================================================================

    async def create_party(self, party_name: str = "Adventuring Party") -> Optional[int]:
        """Create a new party."""
        if not self.authenticated:
            logger.error("Not authenticated")
            return None

        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            async with self.http_session.post(
                f"{self.master_server_url}/api/party/create",
                headers=headers,
                json={"party_name": party_name}
            ) as response:
                data = await response.json()

                if data.get("success"):
                    party_id = data["party_id"]
                    logger.info(f"Created party: {party_name} (ID: {party_id})")
                    return party_id
                else:
                    logger.error(f"Party creation failed: {data.get('message')}")
                    return None

        except Exception as e:
            logger.error(f"Create party error: {e}")
            return None

    async def invite_to_party(self, party_id: int, invitee_id: int):
        """Invite a player to party."""
        # TODO: Implement party invitation
        logger.info(f"Party invite: party_id={party_id}, invitee_id={invitee_id}")

    # ========================================================================
    # Combat Synchronization
    # ========================================================================

    async def send_combat_action(self, combat_id: str, action_type: str,
                                 target_id: Optional[int] = None,
                                 ability_name: Optional[str] = None,
                                 item_id: Optional[int] = None):
        """
        Send combat action to server.

        Args:
            combat_id: Combat session ID
            action_type: Type of action (attack, defend, spell, item, flee)
            target_id: Target character ID
            ability_name: Ability/spell name
            item_id: Item ID if using item
        """
        if not self.character_id:
            logger.error("No character selected")
            return

        try:
            combat_msg = CombatActionMessage(
                combat_id=combat_id,
                character_id=self.character_id,
                action_type=action_type,
                target_id=target_id,
                ability_name=ability_name,
                item_id=item_id
            )

            await self._send_ws_message(combat_msg)
            logger.debug(f"Sent combat action: {action_type}")

        except Exception as e:
            logger.error(f"Send combat action error: {e}")

    # ========================================================================
    # World State Queries
    # ========================================================================

    async def get_world_state(self) -> Optional[Dict]:
        """Get current world state."""
        try:
            async with self.http_session.get(
                f"{self.master_server_url}/api/world/state"
            ) as response:
                return await response.json()

        except Exception as e:
            logger.error(f"Get world state error: {e}")
            return None

    async def get_shard_status(self) -> Optional[List[Dict]]:
        """Get status of all Crystal Shards."""
        try:
            async with self.http_session.get(
                f"{self.master_server_url}/api/world/shards"
            ) as response:
                data = await response.json()
                return data.get("shards", [])

        except Exception as e:
            logger.error(f"Get shard status error: {e}")
            return None

    # ========================================================================
    # Player Discovery
    # ========================================================================

    def get_nearby_players(self, location_id: Optional[int] = None) -> List[NearbyPlayer]:
        """
        Get list of nearby players.

        Args:
            location_id: Filter by location ID

        Returns:
            List of nearby players
        """
        if location_id is not None:
            return [
                player for player in self.nearby_players.values()
                if player.location_id == location_id
            ]
        return list(self.nearby_players.values())

    def update_nearby_player(self, player_data: Dict):
        """Update or add a nearby player."""
        player_id = player_data.get("character_id")
        if not player_id:
            return

        if player_id in self.nearby_players:
            player = self.nearby_players[player_id]
            if "position" in player_data:
                player.update_position(player_data["position"])
            if "location_id" in player_data:
                player.location_id = player_data["location_id"]
        else:
            self.nearby_players[player_id] = NearbyPlayer(
                player_id=player_data.get("player_id", 0),
                character_id=player_id,
                character_name=player_data.get("character_name", "Unknown"),
                location_id=player_data.get("location_id", 0),
                position=player_data.get("position"),
                faction=player_data.get("faction"),
                level=player_data.get("level")
            )

    # ========================================================================
    # Message Handling
    # ========================================================================

    def register_handler(self, message_type: MessageType, handler: Callable):
        """
        Register a message handler.

        Args:
            message_type: Message type to handle
            handler: Async callback function
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    async def _handle_message(self, raw_message: str):
        """Handle incoming message."""
        try:
            # Decrypt if encryption enabled
            if self.encryption_enabled and self.encryption_handler:
                try:
                    raw_message = self.encryption_handler.decrypt(raw_message)
                except Exception:
                    # Message might not be encrypted
                    pass

            # Deserialize
            message = protocol.deserialize(raw_message)

            # Update nearby players on movement/character updates
            if message.type == MessageType.CHARACTER_UPDATE:
                char_msg: CharacterUpdateMessage = message
                self.update_nearby_player({
                    "character_id": char_msg.character_id,
                    "character_name": char_msg.character_name,
                    "location_id": char_msg.location_id,
                    "position": char_msg.position,
                    "level": char_msg.level,
                    "faction": char_msg.faction
                })

            # Call registered handlers
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception as e:
                        logger.error(f"Handler error: {e}")

        except ProtocolError as e:
            logger.error(f"Protocol error handling message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _send_ws_message(self, message: BaseMessage):
        """Send a message via WebSocket."""
        if not self.ws or self.ws.closed:
            logger.error("WebSocket not connected")
            return

        try:
            serialized = protocol.serialize(message)

            # Encrypt if enabled
            if self.encryption_enabled and self.encryption_handler:
                serialized = self.encryption_handler.encrypt(serialized)

            await self.ws.send_str(serialized)

        except Exception as e:
            logger.error(f"Send WebSocket message error: {e}")

    # ========================================================================
    # Ping/Heartbeat
    # ========================================================================

    async def ping(self):
        """Send ping to server."""
        if self.ws and not self.ws.closed:
            ping_msg = BaseMessage(type=MessageType.PING)
            await self._send_ws_message(ping_msg)


# ============================================================================
# Convenience Functions
# ============================================================================

async def create_client_and_connect(username: str, password: str,
                                   master_server_url: Optional[str] = None) -> Optional[NetworkClient]:
    """
    Create a network client and connect to master server.

    Args:
        username: Player username
        password: Player password
        master_server_url: Optional master server URL

    Returns:
        Connected NetworkClient or None if connection failed
    """
    client = NetworkClient(master_server_url)

    if await client.connect(username, password):
        return client
    else:
        await client.disconnect()
        return None


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example of using the network client."""
    # Create and connect client
    client = await create_client_and_connect("player1", "password123")

    if not client:
        print("Failed to connect")
        return

    try:
        # Get characters
        characters = await client.get_characters()
        print(f"Characters: {characters}")

        # Select first character
        if characters:
            await client.select_character(characters[0]["id"])

        # Register chat handler
        async def on_chat(message: ChatMessage):
            print(f"[{message.channel}] {message.sender_name}: {message.content}")

        client.register_handler(MessageType.CHAT, on_chat)

        # Send chat message
        await client.send_chat("Hello, world!")

        # Get world state
        world_state = await client.get_world_state()
        print(f"World state: {world_state}")

        # Keep running for a bit
        await asyncio.sleep(10)

    finally:
        # Disconnect
        await client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    asyncio.run(example_usage())
